# ETL process for migrating data from PostgreSQL to Elasticsearch

This is a learning project whose goal is to implement a fault-tolerant ETL process for migrating data from PostgreSQL to Elasticsearch.

Data on films, actors and genres is loaded into PostgreSQL (the structure is in the file src/db/movies_db_schema.ddl).
The first time you run ETL, an Elasticsearch index will be created (mapping and index settings are in the postgres_to_es/index_config.json file) and the source data from PostgreSQL will be transferred to it. If new or updated records appear in PostgreSQL, they will be transferred to Elasticsearch. The search for new data will be performed using the "updated_at" field. PostgreSQL will check for new data at the interval set in the "fetch_delay" setting.

Also, the time of the last update of the Elasticsearch index will be saved in the state.yaml file (the file name can be changed in the settings - “state_file_name”) so that the process can continue working from where it stopped in case of a restart, rather than starting PostgesSQL overload from the beginning.
**Basic requirements for the project**:

- The script should restore connections to databases when the connection is lost. Repeat requests with gradually increasing time between them. Implemented as a parametric decorator.

- The script must save states in a yaml file. When restarted, the process will continue from where it stopped. If you update or add new records, only the new records will be processed and transferred to the Elasticsearch index

- The script should load settings for logging, creating an Elasticsearch index and connecting to databases from a separate yaml file

- The script must be run in a container. The launch is carried out in four docker containers: ElasticSearch, PostgresSQL, ETL process and Kibana (for easy verification that the data is loaded into ES correctly) using docker-compose.

- Apply type annotation, logging, data classes to represent database records and the pydantic package to validate settings in the project.

### Technology stack
- python 3.9
- PostgreSQL 13
- elasticsearch 7.15.2
- docker

### Launch the application
To launch the application:

1. clone the repository
```bash
git clone 'path to repository'
```
2. create and launch a virtual environment
```bash
python -m venv venv
source venv/bin/activate
```
3. install external dependencies from requirements.txt
```bash
pip install -r requirements.txt
```
4. run docker-compose
```bash
docker-compose up
```

Docker will build the necessary images and launch the containers.
### Repository structure
**root directory**:

- **.env** - file with the environment variables necessary to run the project
- **Dockerfile** - instructions for building a docker image of an ETL process
- **docker-compose.yaml** - docker container configuration
- **requirements.txt** - list of external project dependencies

*Although it is not recommended to save sensitive data (passwords, logins, etc.) in the repository, for the convenience of launching containers and connecting to databases, all necessary data is specified in the .env and postgres_to_es/config.py files.*

**directory src/db:**

- **001_init_user_db.sh** - bash script, will run when the PostgreSQL container is started for the first time
- **movies_db_schema.ddl** - PostgreSQL database structure
- **movies_db_content.dump** - source data for filling the PostgreSQL database

*Files from src/db will be copied to the PostgreSQL container and the first time the container is started, the script 001_init_user_db.sh will be launched. As a result, a new user and database will be created in accordance with the environment variables specified in the .env file. A schema, tables, and indexes specified in the movies_db_schema.ddl file will be created in the database and the database will be filled with data from movies_db_content.dump.*

**directory postgres_to_es:**

- **backoff.py** - parametric decorator function for restoring connections to databases
- **config.py** - pydantic models for validating settings from the config.yaml file
- **config.yaml** - file with settings for the ETL process, database connections, logging
- **dataclass.py** - dataclasses for representing records in PostgreSQL
- **index_config.json** - index schema in Elasticsearch
- **main.py** - ETL process
- **sql.py** - SQL queries for retrieving data from PostgreSQL
- **state.py** - for working with state saving