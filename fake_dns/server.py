import ipaddress

from dnslib import A, CLASS, PTR, RCODE, RR, QTYPE
from dnslib.server import BaseResolver, DNSServer

from const import *
from models.cache import create_cache


class FakeResolver(BaseResolver):
    """Resolver object with reference to Server.cache so resolve() can interact with the cache"""

    def __init__(self, cache):
        self._cache = cache

    @staticmethod
    def get_ip_from_reverse_pointer(arpa):
        ip_str = '.'.join(arpa.split('.')[:-2][::-1])  # strip in-addr.arpa/ip6.arpa, reverse order, join on '.'
        ip = ipaddress.ip_address(ip_str)

        if arpa != ip.reverse_pointer:
            raise ValueError("Reverse pointer provided didn't match the calculated pointer")

        return str(ip)

    def resolve(self, request, handler):
        # TODO: use the handler?
        idna = request.q.qname.idna()

        self._cache.prune_stale()
        reply = request.reply()
        reply.header.rcode = RCODE.NXDOMAIN

        if request.q.qtype == QTYPE.A:
            self._cache.add_record(idna)
            for rec in self._cache.get_addr_by_name(idna):
                reply.add_answer(RR(idna, rclass=CLASS.IN, rtype=QTYPE.A, rdata=A(rec['addr'])))
        elif request.q.qtype == QTYPE.PTR:
            ip = self.get_ip_from_reverse_pointer(idna)
            for rec in self._cache.get_name_by_addr(ip):
                reply.add_answer(RR(idna, rclass=CLASS.IN, rtype=QTYPE.PTR, rdata=PTR(rec['name'])))

        if reply.rr:
            reply.header.rcode = RCODE.NOERROR

        return reply


class FakeDNSServer(object):
    def __init__(self, addr=DEFAULT_LISTEN_ADDR, port=DEFAULT_LISTEN_PORT, duration=DEFAULT_CACHE_DURATION,
                 ip_range=DEFAULT_ADDR_RANGE, cache_type=CACHE_TYPE.DICTIONARY, cache_path=DEFAULT_DB_PATH):
        self._addr = addr
        self._port = port

        self._cache = create_cache(ip_range, duration, cache_type, cache_path)
        self._resolver = FakeResolver(self._cache)
        self._dns_server = DNSServer(self._resolver, self._addr, self._port)

    @property
    def cache(self):
        return self._cache

    @property
    def addr(self):
        return self._addr

    @property
    def port(self):
        return self._port

    @property
    def duration(self):
        return self._cache.duration

    @duration.setter
    def duration(self, value):
        self._cache.duration = value

    @property
    def addr_range(self):
        return self._cache.addr_range

    @addr_range.setter
    def addr_range(self, value):
        self._cache.addr_range = value

    def is_alive(self):
        return self._dns_server.isAlive()

    def start(self):
        self._dns_server.start()

    def start_thread(self):
        self._dns_server.start_thread()

    def stop(self):
        self._cache.close()
        self._dns_server.stop()
