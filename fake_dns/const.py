from enum import Enum

DEFAULT_ADDR_RANGE = '10.0.0.0-10.0.0.255'
DEFAULT_CACHE_DURATION = 900  # 15 minutes
DEFAULT_DB_PATH = 'fake_dns.sqlite3'
DEFAULT_LISTEN_ADDR = '0.0.0.0'
DEFAULT_LISTEN_PORT = 53


# noinspection PyPep8Naming
class CACHE_TYPE(Enum):
    DATABASE = 1
    DICTIONARY = 2
