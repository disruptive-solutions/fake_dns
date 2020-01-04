import itertools
import socket
import struct
import ipaddress
import sqlite3
import time
from os import path

from abc import ABCMeta, abstractmethod
from dnslib.server import BaseResolver, DNSServer

import delirium.const


QUERY_CREATE_TABLE = """CREATE TABLE IF NOT EXISTS cache (
                            id integer PRIMARY KEY AUTOINCREMENT,
                            addr integer NOT NULL,
                            name text NOT NULL,
                            date real NOT NULL,
                            expired integer DEFAULT 0
                        );"""

QUERY_ADD_ENTRY = "INSERT INTO cache (addr, name, date) VALUES (:addr, :name, :date);"
QUERY_EXPIRE_DELETE_BY_ID = "DELETE FROM cache WHERE id = (?);"
QUERY_EXPIRE_UPDATE_BY_ID = "UPDATE cache SET expired = 1 WHERE id = (?);"
QUERY_GET_BY_EXPIRED = "SELECT * FROM cache WHERE expired = :expired;"
QUERY_GET_BY_ADDR = "SELECT * FROM cache WHERE addr = :addr AND expired = :expired;"
QUERY_GET_BY_NAME = "SELECT * FROM cache WHERE name = :name AND expired = :expired;"
QUERY_UPDATE_DATE_BY_ID = "UPDATE cache SET date = :date WHERE id = :id;"

def get_addr_range(value):
    """Converts a <ip>-<ip> string to integers for random.randrange()"""

    values = value.split('-')
    s_int = struct.unpack('!L', socket.inet_aton(values[0]))[0]
    e_int = struct.unpack('!L', socket.inet_aton(values[1]))[0]
    return s_int, e_int


def n_generator(start, end):
    for i in itertools.cycle(range(start, end + 1)):
        yield i

class CacheObject:
    __metaclass__ = ABCMeta

    def __init__(self, addr_range, duration):
        self._addr_range = get_addr_range(addr_range)
        self._duration = duration
        self._n_generator = n_generator(*self._addr_range)

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, value):
        self._duration = value

    @property
    def addr_range(self):
        return self._addr_range

    @addr_range.setter
    def addr_range(self, value):
        self._addr_range = get_addr_range(value)

    @staticmethod
    def __socket_aton(value):
        return struct.unpack('!L', socket.inet_aton(value))[0]

    @abstractmethod
    def add_record(self, label):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def get_addr_by_name(self, value):
        pass

    @abstractmethod
    def get_name_by_addr(self, value):
        pass

    @abstractmethod
    def prune_stale(self):
        pass

def init_db(path):
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    c.execute(QUERY_CREATE_TABLE)
    return c


class CacheDatabase(CacheObject):
    def __init__(self, addr_range, duration, path):
        super(CacheDatabase, self).__init__(addr_range, duration)
        self.remove_stale = False
        self._path = path
        self._conn = init_db(self._path)
        self._cur = self._conn.cursor()

    @property
    def path(self):
        return self._path

    def add_record(self, name):
        self._cur.execute(QUERY_GET_BY_NAME, {'name': name, 'expired': 0})
        rec = self._cur.fetchone()

        if rec:
            q = QUERY_UPDATE_DATE_BY_ID
            p = {'id': rec['id'], 'date': time.time()}
        else:
            q = QUERY_ADD_ENTRY
            p = {'addr': next(self._n_generator), 'name': name, 'date': time.time()}

        self._cur.execute(q, p)
        self._conn.commit()

    def close(self):
        self._cur.close()
        self._conn.commit()
        self._conn.close()

    def get_name_by_addr(self, addr, expired=0):
        self._cur.execute(QUERY_GET_BY_ADDR, {'addr': addr, 'expired': expired})

        out = []
        for rec in self._cur:
            out.append(rec['id'])

        return out

    def get_addr_by_name(self, name, expired=0):
        self._cur.execute(QUERY_GET_BY_NAME, {'name': name, 'expired': expired})

        out = []
        for rec in self._cur:
            out.append(rec['addr'])

        return out

    def prune_stale(self):
        self._cur.execute(QUERY_GET_BY_EXPIRED, {'expired': 0})
        ids = []

        for row in self._cur:
            ids.append((row['id'],))  # executemany() seq_of_parameters should be a tuple (1-tuple in this case)

        if self.remove_stale:
            q = QUERY_EXPIRE_DELETE_BY_ID
        else:
            q = QUERY_EXPIRE_UPDATE_BY_ID

        self._cur.executemany(q, ids)
        self._conn.commit()
