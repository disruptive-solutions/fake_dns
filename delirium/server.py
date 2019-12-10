import ipaddress

from dns import FakeDNSServer
from dns import FakeResolver
from dnslib import A, CLASS, PTR, RCODE, RR, QTYPE
from dnslib.server import BaseResolver, DNSServer

from const import *
from models.database import CacheDatabase
from models.dictionary import CacheDictionary


def create_cache(addr_range, duration, cache_type, path=DEFAULT_DB_PATH):
    """Provides a caching mechanism for the dnslib.DNSServer"""

    if cache_type == CACHE_TYPE.DICTIONARY:
        return CacheDictionary(addr_range, duration)
    elif cache_type == CACHE_TYPE.DATABASE:
        return CacheDatabase(addr_range, duration, path)
    else:
        raise ValueError("Unsupported cache type")
