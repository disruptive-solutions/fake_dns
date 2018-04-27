#!/usr/bin/env python2.7

from const import *
from server import FakeDNSServer


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument('-l', '--listen', default=DEFAULT_LISTEN_ADDR, help='Address to listen on')
    p.add_argument('-p', '--port', default=DEFAULT_LISTEN_PORT, type=int, help='Purt to listen on (UDP)')
    p.add_argument('-t', '--time', default=DEFAULT_CACHE_DURATION, type=int, help='Seconds for which cache entries should exist')
    p.add_argument('-r', '--range', default=DEFAULT_ADDR_RANGE, help='Range of IP addresses to randomly generate')

    args = p.parse_args()

    s = FakeDNSServer(args.listen, args.port, args.time, args.range)

    try:
        s.start()
    except KeyboardInterrupt:
        pass
    finally:
        s.stop()
