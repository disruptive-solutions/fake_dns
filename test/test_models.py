import socket
import struct
import time
import unittest

from fake_dns.const import *
from fake_dns.models.cache import get_ip_as_ints
from fake_dns.models.dictionary import CacheDictionary
from fake_dns.models.database import CacheDatabase


def suite():
    cache_dict_suite = unittest.TestLoader().loadTestsFromTestCase(TestCacheDictionary)
    cache_db_suite = unittest.TestLoader().loadTestsFromTestCase(TestCacheDatabase)
    return unittest.TestSuite([cache_dict_suite, cache_db_suite])


class TestCacheDictionary(unittest.TestCase):
    TEST_HOST = 'www.somedomain.tld'

    def test_cache_init(self):
        c = CacheDictionary(DEFAULT_ADDR_RANGE, DEFAULT_CACHE_DURATION)

        self.assertEqual(c.addr_range, get_ip_as_ints(DEFAULT_ADDR_RANGE))
        self.assertEqual(c.duration, DEFAULT_CACHE_DURATION)

    # noinspection PyPropertyAccess
    def test_cache_update(self):
        c = CacheDictionary(DEFAULT_ADDR_RANGE, DEFAULT_CACHE_DURATION)

        new_dur = 500
        c.duration = new_dur
        self.assertEqual(c.duration, new_dur)

        new_addr_range = '192.168.0.0-192.168.0.255'
        c.addr_range = new_addr_range
        self.assertEqual(c.addr_range, get_ip_as_ints(new_addr_range))

        with self.assertRaises(AttributeError):
            c.data = {}

    def test_cache_timeout(self):
        c = CacheDictionary(DEFAULT_ADDR_RANGE, duration=1)
        c.add_record(self.TEST_HOST)

        self.assertTrue(c.get_addr_by_name(self.TEST_HOST))

        time.sleep(1)
        c.prune_stale()

        with self.assertRaises(AttributeError):
            self.assertFalse(c.get_addr_by_name(self.TEST_HOST))

    def test_cache_range(self):
        c = CacheDictionary(DEFAULT_ADDR_RANGE, DEFAULT_CACHE_DURATION)
        c.add_record(self.TEST_HOST)
        ip = c.get_addr_by_name(self.TEST_HOST)
        ip_int = struct.unpack('!L', socket.inet_aton(ip))[0]

        self.assertTrue(c.addr_range[0] <= ip_int <= c.addr_range[1])


class TestCacheDatabase(unittest.TestCase):
    TEST_HOST = 'www.somedomain.tld'

    def test_cache_init(self):
        c = CacheDatabase(DEFAULT_ADDR_RANGE, DEFAULT_CACHE_DURATION, DEFAULT_DB_PATH)

        self.assertEqual(c.addr_range, get_ip_as_ints(DEFAULT_ADDR_RANGE))
        self.assertEqual(c.duration, DEFAULT_CACHE_DURATION)


if __name__ == '__main__':
    unittest.main()
