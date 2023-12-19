import datetime as dt
from functools import wraps
from time import sleep

import elasticsearch
import psycopg2  # to establish connections to PostgreSQL databases, execute SQL queries, and retrieve data easily.


def backoff(start_sleep_time=0.01, factor=2, border_sleep_time=4,
            logger=None, is_connection=True):
    """
        A function to re-execute a function after some time if an error occurs.

         Args:
            logger
            is_connection:
            start_sleep_time: Start repeat time
            factor: How many times should the waiting time be increased?
            border_sleep_time: Boundary sleep time

         Returns:
             Callable: Decorable function
    """
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            _factor = factor
            counter = 1
            begin = dt.datetime.now()
            while True:
                try:
                    connection = func(*args, **kwargs)
                    finish_time = (dt.datetime.now() - begin).total_seconds()
                    if logger and is_connection:
                        logger.info('Number of attempts: %s. Time: %s seconds',
                                    counter, finish_time)
                    return connection
                except psycopg2.OperationalError:
                    if logger:
                        logger.error('Can\'t connect to postgres')
                except elasticsearch.ConnectionError:
                    if logger:
                        logger.error('Can\'t connect to elasticsearch')
                wait = min(start_sleep_time * 2 ** _factor, border_sleep_time)
                _factor += 1
                counter += 1
                sleep(wait)

        return inner
    return func_wrapper
