from typing import Optional, Dict
from pydantic import BaseModel #for data validation and settings management that's based on Python type hints.


class DSNSettings(BaseModel):
    host: str
    port: int
    dbname: str
    password: str
    user: str
    options: str


class PostgresSettings(BaseModel):
    """
        Class for validating connection settings to postgresql
    """
    dsn: DSNSettings
    limit: Optional[int]


class ESHost(BaseModel):

    host: str
    port: int


class ESSettings(BaseModel):
    """
    Class for validating connection settings to Elasticsearch
    """
    default_host: ESHost
    index_name: str
    index_config: str


class ETLSettings(BaseModel):
    """
    Class for validating connection settings to ETL-process
    """
    postgres: PostgresSettings
    es: ESSettings
    fetch_delay: float
    state_file_name: str  # state_file_name: -	The time of the last update of the Elasticsearch index will be saved in it
    log_status_period: float


class Config(BaseModel):
    etl: ETLSettings
    logger: Dict
