from IPython.kernel.zmq.kernelbase import Kernel
import psycopg2
from psycopg2 import ProgrammingError
from psycopg2.extensions import (
    QueryCanceledError, POLL_OK, POLL_READ, POLL_WRITE)

import re
from select import select

from .version import __version__

version_pat = re.compile(r'^PostgreSQL (\d+(\.\d+)+)')


def wait_select_inter(conn):
    while 1:
        try:
            state = conn.poll()
            if state == POLL_OK:
                break
            elif state == POLL_READ:
                select([conn.fileno()], [], [])
            elif state == POLL_WRITE:
                select([], [conn.fileno()], [])
            else:
                raise conn.OperationalError(
                    "bad state from poll: %s" % state)
        except KeyboardInterrupt:
            conn.cancel()
            # the loop will be broken by a server error
            continue


class PostgresKernel(Kernel):
    implementation = 'postgres_kernel'
    implementation_version = __version__

    language_info = {'name': 'PostgreSQL',
                     'codemirror_mode': 'sql',
                     'mimetype': 'text/x-postgresql',
                     'file_extension': '.sql'}

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)

        # Catch KeyboardInterrupt, cancel query, raise QueryCancelledError
        psycopg2.extensions.set_wait_callback(wait_select_inter)
        self._start_connection()

    @property
    def language_version(self):
        m = version_pat.search(self.banner)
        return m.group(1)

    _banner = None

    @property
    def banner(self):
        if self._banner is None:
            self._banner = self.fetchone('SELECT VERSION()')[0]
        return self._banner

    def _start_connection(self):
        self._conn = psycopg2.connect('')  # TODO figure out a way to pass this...

    def fetchone(self, query):
        with self._conn.cursor() as c:
            c.execute(query)
            return c.fetchone()

    def fetchall(self, query):
        with self._conn.cursor() as c:
            c.execute(query)
            return c.fetchall()

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
        if not code.strip():
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}

        try:
            output = self.fetchall(code)
        except QueryCanceledError:
            self._conn.rollback()
            return {'status': 'abort', 'execution_count': self.execution_count}
        except ProgrammingError as e:
            self._conn.rollback()
            return {'status': 'error', 'execution_count': self.execution_count,
                    'ename': 'ProgrammingError', 'evalue': str(e),
                    'traceback': []}
        # Send standard output
        stream_content = {'name': 'stdout', 'text': output}
        self.send_response(self.iopub_socket, 'stream', stream_content)

        return {'status': 'ok', 'execution_count': self.execution_count,
                'payload': [], 'user_expressions': {}}
