import click

from .const import *
from .dns import FakeDNSServer

@click.group()
def delirium():
    pass

@click.command()
@click.option('--listen', default=DEFAULT_LISTEN_ADDR, help='Address to listen on')
@click.option('--port', default=DEFAULT_LISTEN_PORT, type=int, help='Port to listen on (UDP)')
@click.option('--time', default=DEFAULT_CACHE_DURATION, type=int, help='Seconds for which cache entries should exist')
@click.option('--range', default=DEFAULT_ADDR_RANGE, help='Range of IP addresses to randomly generate')
@click.option('--cache_type', default=CACHE_TYPE.DICTIONARY, help='Cache type.')
@click.option('--db-path', help='Path to sqlite3 database')
def dns(listen, port, time, range, cache_type, db_path):
    click.echo('Running Delirium DNS Server')
    s = FakeDNSServer(listen, port, time, range, cache_type, db_path)
    if db_path:  # there's probably a better way to do this
        cache_type = CACHE_TYPE.DATABASE
    else:
        cache_type = CACHE_TYPE.DICTIONARY
    try:
        s.start()
    except KeyboardInterrupt:
        pass
    finally:
        s.stop()

delirium.add_command(dns)

if __name__ == "__main__":
    delirium()
