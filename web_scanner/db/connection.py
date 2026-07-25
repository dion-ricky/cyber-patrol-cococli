from functools import lru_cache

import psycopg

from config.settings import Settings


@lru_cache(maxsize=1)
def get_connection(settings: Settings) -> psycopg.Connection:
    return psycopg.connect(settings.db.url)
