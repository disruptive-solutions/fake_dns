import dnslib
import socket
import pytest

from delirium.const import *
from delirium.dns.fakednsserver import FakeDNSServer
from delirium.dns.fakeresolver import FakeResolver
from delirium.dns.cache import get_addr_range


def _get_unused_udp_port():
    """Returns available UDP port"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _is_valid_ip_addr(addr):
    try:
        socket.inet_aton(addr)
    except socket.error:
        return False
    else:
        return True


class TestFakeDNSServer():
    PORT = _get_unused_udp_port()  # can't bind to anything south of 1024 without root (default 53)

    def test_server_init(self):
        s = FakeDNSServer(port=self.PORT)

        assert s.port == self.PORT
        assert s.addr == DEFAULT_LISTEN_ADDR
        assert s.addr_range == get_addr_range(DEFAULT_ADDR_RANGE)
        assert s.duration == DEFAULT_CACHE_DURATION

    # noinspection PyPropertyAccess
    def test_server_update(self):
        s = FakeDNSServer(port=self.PORT)

        # reallu updating the FakeCache object but the server will proxy these
        new_dur = 500
        s.duration = new_dur
        assert s.duration == new_dur

        new_addr_range = '192.168.0.0-192.168.0.255'
        s.addr_range = new_addr_range
        assert s.addr_range == get_addr_range(new_addr_range)

        with pytest.raises(AttributeError):
            s.cache = {}

        with pytest.raises(AttributeError):
            s.port = _get_unused_udp_port()

        with pytest.raises(AttributeError):
            s.addr = '192.168.0.100'

    def test_server_start(self):
        # TODO: this could probably be improved
        s = FakeDNSServer(port=self.PORT)
        s.start_thread()
        assert s.is_alive() == True
        s.stop()


if __name__ == '__main__':
    pytest.main()
