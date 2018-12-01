from ipykernel.kernelbase import Kernel
import psycopg2
from psycopg2 import Error, ProgrammingError, OperationalError
from psycopg2.extensions import (
    QueryCanceledError, POLL_OK, POLL_READ, POLL_WRITE)

import re
import os
from select import select

from .version import __version__
from tabulate import tabulate
version_pat = re.compile(r'^PostgreSQL (\d+(\.\d+)+)')


def log(val):
    with open('kernel.log', 'a') as f:
        f.write(str(val) + '\n')
    return val


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
        log('inside init')
        # Catch KeyboardInterrupt, cancel query, raise QueryCancelledError
        psycopg2.extensions.set_wait_callback(wait_select_inter)
        self._conn_string = os.getenv('DATABASE_URL', '')
        self._conn = None
        self._start_connection()

    @property
    def language_version(self):
        m = version_pat.search(self.banner)
        return m.group(1)

    _banner = None

    @property
    def banner(self):
        if self._banner is None:
            if self._conn is None:
                return 'not yet connected to a database'
            self._banner = self.fetchone('SELECT VERSION();')[0]
        return self._banner

    def _start_connection(self):
        log('starting connection')
        try:
            self._conn = psycopg2.connect(self._conn_string)
        except OperationalError:
            log('failed to connect to {}'.format(self._conn_string))
            message = '''Failed to connect to a database at {}'''.format(self._conn_string)
            self.send_response(self.iopub_socket, 'stream',
                               {'name': 'stderr', 'text': message})

    def fetchone(self, query):
        log('fetching one from: \n' + query)
        with self._conn.cursor() as c:
            c.execute(query)
            return log(c.fetchone())

    def fetchall(self, query):
        log('fetching all from: \n' + query)
        with self._conn.cursor() as c:
            c.execute(query)
            desc = c.description
            if c.description:
                keys = [col[0] for col in c.description]
                return keys, c.fetchall()
            return None, None

    CONN_STRING_COMMENT = re.compile(r'--\s?connection:\s?(.*)$')
    AUTOCOMMIT_SWITCH = re.compile(r'--autocommit:(.*)$')

    def change_connection(self, conn_string):
        self._conn_string = conn_string
        self._start_connection()

    def switch_autocommit(self, switch_to):
        if not self._conn:
            self._start_connection()
        self._conn.commit()
        self._conn.autocommit = switch_to

    def handle_autocoomit_switch(self, switch):
        """
        Strip and make a string case insensitive and ensure it is either 'true' or 'false'.

        If neither, prompt user for either value.
        When 'true', return True, and when 'false' return False.
        """
        parsed_switch = switch.strip().lower()
        if not parsed_switch in ['true', 'false']:
            self.send_response(
                self.iopub_socket, 'stream', {
                    'name': 'stderr',
                    'text': 'autocommit must be true or false.\n\n'
                }
            )
            return {'status': 'error', 'execution_count': self.execution_count}

        switch_bool = (parsed_switch == 'true')
        self.switch_autocommit(switch_bool)
        self.send_response(
            self.iopub_socket, 'stream', {
                'name': 'stdout',
                'text': (
                    'commited current transaction & switched autocommit mode to ' +
                    str(self._conn.autocommit)
                )
            }
        )
        return {'status': 'ok', 'execution_count': self.execution_count, 'payload': []}

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
        print(code)

        connection_string = self.CONN_STRING_COMMENT.findall(code)
        autocommit_switch = self.AUTOCOMMIT_SWITCH.findall(code)
        if autocommit_switch:
            return self.handle_autocoomit_switch(autocommit_switch[0])
        if connection_string:
            self.change_connection(connection_string[0])

        code = self.CONN_STRING_COMMENT.sub('', code)
        if not code.strip():
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}

        if self._conn is None:
            self.send_response(
                self.iopub_socket, 'stream', {
                    'name': 'stderr',
                    'text': '''\
Error: Unable to connect to a database at "{}".
  Perhaps you need to set a connection string with
  -- connection: <connection string here>'''.format(self._conn_string)
                })
            return {'status': 'error', 'execution_count': self.execution_count,
                    'ename': 'MissingConnection'}
        try:
            header, rows = self.fetchall(code)
        except QueryCanceledError:
            self._conn.rollback()
            return {'status': 'abort', 'execution_count': self.execution_count}
        except Error as e:
            self.send_response(self.iopub_socket, 'stream',
                               {'name': 'stderr', 'text': str(e)})                              
            self._conn.rollback()
            return {'status': 'error', 'execution_count': self.execution_count,
                    'ename': 'ProgrammingError', 'evalue': str(e),
                    'traceback': []}
        else:
            self.send_response(
                self.iopub_socket, 'stream', {
                    'name': 'stdout',
                    'text': str(len(rows)) + " row(s) returned.\n"
                })

            for notice in self._conn.notices:
                self.send_response(
                    self.iopub_socket, 'stream', {
                        'name': 'stdout',
                        'text': str(notice)
                })
            self._conn.notices = []

            if header is not None and len(rows) > 0:
                self.send_response(self.iopub_socket, 'display_data', display_data(header, rows))

        return {'status': 'ok', 'execution_count': self.execution_count,
                'payload': [], 'user_expressions': {}}


def display_data(header, rows):
    d = {
        'data': {
            'text/latex': tabulate(rows, header, tablefmt='latex_booktabs'),
            'text/plain': tabulate(rows, header, tablefmt='simple'),
            'text/html': tabulate(rows, header, tablefmt='html'),
        },
        'metadata': {}
    }
    return d
