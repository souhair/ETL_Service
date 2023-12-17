import datetime as dt
import json
import logging
from dataclasses import asdict
from logging.config import dictConfig
from pathlib import Path
from time import sleep
from typing import Iterator, List, Tuple, Union

#import elasticsearch
import psycopg2
import yaml
from elasticsearch import Elasticsearch, helpers
from psycopg2.extensions import connection as pg_connection
from psycopg2.extras import DictCursor

import sql
from backoff import backoff
from config import Config, DSNSettings, ESHost, ESSettings, PostgresSettings
from dataclass import Filmwork, FilmworkStorage, Genre, Person
from state import State, YamlFileStorage

CONFIG_FILENAME = 'config.yaml'
if __name__ == '__main__':
    logger = logging.getLogger(__name__)


class ElasticSaver:
    """class for working with elasticsearch"""
    index_name: str
    host: ESHost
    index_config: str
    es_client: Elasticsearch

    def __init__(self, params: ESSettings):
        self.index_name = params.index_name
        self.host = params.default_host
        self.index_config = params.index_config
        self.es_client = self.get_es_client()
        if not self.check_index():
            self._create_index()

    def check_index(self) -> bool:
        """Checks the existence of an index with the specified name"""
        return self.es_client.indices.exists(index=self.index_name)

    @backoff(logger=logger)
    def get_es_client(self) -> Elasticsearch:
        """Creates an elasticsearch client"""
        logger.info('Connecting to elasticsearch...')
        host = f'{self.host.host}:{self.host.port}'
        _client = Elasticsearch(hosts=host)
        _client.cluster.health(wait_for_status="yellow")
        logger.info('The connection to elasticsearch has been successfully established!')
        return _client

    def _create_index(self) -> None:
        """Creates an index with the specified settings and name"""
        path = Path(__file__).parent.joinpath(self.index_config)
        with open(path, 'r', encoding='utf-8') as index_file:
            index_settings = json.load(index_file)

        settings = index_settings.get('settings')
        mappings = index_settings.get('mappings')
        self.es_client.indices.create(index=self.index_name,
                                      settings=settings,
                                      mappings=mappings)

    def save_to_es(self, data: List[Filmwork]) -> None:
        """Loads data into the index"""
        actions = [
            {
                "_index": "movies",
                "_id": movie.id,
                "_source": asdict(movie)
            }
            for movie in data
        ]
        while True:
            try:
                records, errors = helpers.bulk(client=self.es_client,
                                               actions=actions,
                                               raise_on_error=False,
                                               stats_only=True)

                if records:
                    logger.info('Movies updated in Elasticsearch: %s',
                                records)
                if errors:
                    logger.error(
                        'Errors occurred while updating Elasticsearch: %s',
                        errors)
                return
            except elasticsearch.ConnectionError as error:
                logger.error(
                        ' No connection to Elasticsearch %s',
                        error)
                self.es_client = self.get_es_client()


class DataTransformer:
    """
        Class for converting data from postgres into Filmork class objects and
        storing them in a container for later saving in elasticsearch
    """
    inner_storage: FilmworkStorage

    def __init__(self):
        self.inner_storage = FilmworkStorage()

    def trasform_data(self, data: Iterator[Tuple]) -> List[Filmwork]:
        """Converts data from postgres into class objects Filmork """
        if self.inner_storage:
            self.inner_storage.clear()

        for movie in data:
            film_id, *data, role, person_id, fullname, genre_id, name = movie
            candidate = Filmwork(film_id, *data)
            person = Person(person_id, fullname)
            genre = Genre(genre_id, name)
            movie = self.inner_storage.get_or_append(candidate)
            movie.add_person(role, person)
            movie.add_genre(genre)
        logger.info('Prepared films for updating in еlasticsearch: %s',
                    self.inner_storage.count())

        return self.inner_storage.get_all()


class PostgresLoader:
    """Class for unloading data from postgres"""
    dsn: DSNSettings
    connection: pg_connection
    state: State
    check_date: dt.datetime
    limit: int

    def __init__(self, params: PostgresSettings, state: State):
        self.dsn = params.dsn
        self.connection = self.get_connection()
        self.state = state
        self.check_date = self.state.get_state('last_update') or dt.datetime.min
        self.limit = params.limit

    @backoff(logger=logger)
    def get_connection(self) -> pg_connection:
        """ Creates a connection to postgres"""
        logger.info('Connection to postgres...')
        with psycopg2.connect(**self.dsn.dict(), cursor_factory=DictCursor) as pg_conn:
            logger.info('Connection to postgres successfully established')
            return pg_conn

    def executor(self, sql_query: str, params: tuple) -> Iterator[Tuple]:
        """Executes sql query"""
        while True:
            try:
                if self.connection.closed:
                    self.connection = self.get_connection()
                cursor = self.connection.cursor()
                cursor.execute(sql_query, params)
                while True:
                    chunk_data = cursor.fetchmany(self.limit)
                    if not chunk_data:
                        return
                    for row in chunk_data:
                        yield row
            except psycopg2.OperationalError as pg_error:
                logger.error('Connection error when executing SQL query %s',
                             pg_error)

    @backoff(logger=logger, is_connection=False)
    def load_data(self) -> Union[Iterator[Tuple], List]:
        """
        Unloads data updated after the specified date from postgres:
            - finds new records and determines the id of changed films
            - downloads information for these films
        """
        now = dt.datetime.utcnow()
        films_ids = self.executor(sql.movies_ids, (self.check_date,))
        films_ids = tuple([record[0] for record in films_ids])
        if films_ids:
            films_data = self.executor(sql.movies_data, (films_ids,))
            self.state.set_state('last_update', str(now))
            self.check_date = now
            return films_data
        return []


def setup_logger() -> None:
    """Configures script logging"""
    log_file = Path(__file__).parent.joinpath('log', 'etl.log')
    log_file.parent.mkdir(parents=True, exist_ok=True)
    config.logger['handlers']['file']['filename'] = log_file
    config.logger['handlers']['file_error']['filename'] = log_file
    dictConfig(config.logger)


def get_state_storage() -> State:
    """Set up a container for storing states"""
    state_file_name= Path(__file__).parent.joinpath(config.etl.state_file_name)
    storage = YamlFileStorage(state_file_name)
    return State(storage)


def start_etl_process() -> None:
    """Starts the etl process"""
    logger.info('The script started working...')
    elastic = ElasticSaver(config.etl.es)
    state = get_state_storage()
    postgres = PostgresLoader(config.etl.postgres, state)
    transformer = DataTransformer()
    time_log_status = dt.datetime.utcnow()
    while True:
        now = dt.datetime.utcnow()
        data = postgres.load_data()
        if data:
            tranformed_data = transformer.trasform_data(data)
            elastic.save_to_es(tranformed_data)
        if now > time_log_status + dt.timedelta(seconds=config.etl.log_status_period):
            logger.info('The script works normally...')
            time_log_status = now
        sleep(config.etl.fetch_delay)


if __name__ == '__main__':
    config_file = Path(__file__).parent.joinpath(CONFIG_FILENAME)
    config_dict = yaml.safe_load(config_file.open(encoding='utf-8'))
    config = Config.parse_obj(config_dict)
    setup_logger()
    start_etl_process()
