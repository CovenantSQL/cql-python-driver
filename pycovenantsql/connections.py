import sys
import os
import requests
from . import err
from .cursors import Cursor
from .optionfile import Parser
from . import converters
from ._compat import PY2, range_type, text_type, str_type, JYTHON, IRONPYTHON


DEBUG = False
VERBOSE = False

class Connection(object):
    """
    Representation of a RPC connect with a CovenantSQL server.

    The proper way to get an instance of this class is to call
    connect().

    Establish a connection to the CovenantSQL database. Accepts several
    arguments:

    :param uri: Uri address starts with "covenantsql://", where the database id is located
    :param key: Private key to access database.
    :param database: Database id to use. uri and database should set at least one.
    :param read_timeout: The timeout for reading from the connection in seconds (default: None - no timeout)
    #(Not supported now):param write_timeout: The timeout for writing to the connection in seconds (default: None - no timeout)
    :param read_default_file:
        Specifies  my.cnf file to read these parameters from under the [client] section.
    :param cursorclass: Custom cursor class to use.
    :param connect_timeout: Timeout before throwing an exception when connecting.
        (default: 10, min: 1, max: 31536000)
    :param read_default_group: Group to read from in the configuration file.

    See `Connection <https://www.python.org/dev/peps/pep-0249/#connection-objects>`_ in the
    specification.
    """


    _closed = False

    def __init__(self, dsn=None, host=None, port=0, key=None, database=None,
                 https_pem=None, read_default_file=None,
                 cursorclass=Cursor, connect_timeout=None, read_default_group=None,
                 read_timeout=None):

        self._resp = None

        # 1. pre process params in init
        self.encoding = 'utf8'

        # 2. read config params from file(if init is None)
        if read_default_group and not read_default_file:
            read_default_file = "covenant.cnf"

        if read_default_file:
            if not read_default_group:
                read_default_group = "python-client"

            cfg = Parser()
            cfg.read(os.path.expanduser(read_default_file))

            def _config(key, arg):
                if arg:
                    return arg
                try:
                    return cfg.get(read_default_group, key)
                except Exception:
                    return arg

            dsn = _config("dsn", dsn)
            host = _config("host", host)
            port = int(_config("port", port))
            key = _config("key", key)
            database = _config("database", database)
            https_pem = _config("https_pem", https_pem)

        # 3. save params
        self.dsn = dsn
        # TODO dsn parse to host, port and database
        self.host = host or "localhost"
        self.port = port or 11108
        self.key = key
        self.database = database

        self._query_uri = "https://" + self.host + ":" + str(self.port) + "/v1/query"
        self._exec_uri = "https://" + self.host + ":" + str(self.port) + "/v1/exec"
        if VERBOSE:
            try:
                import http.client as http_client
            except ImportError:
                # Python 2
                import httplib as http_client
            http_client.HTTPConnection.debuglevel = 1
        requests.packages.urllib3.disable_warnings()
        if https_pem:
            self._cert = (https_pem, self.key)
        else:
            self._cert = self.key

        self.timeout = None
        if connect_timeout is not None and connect_timeout <= 0:
            raise ValueError("connect_timeout should be >= 0")
        if read_timeout is not None and read_timeout <= 0:
            raise ValueError("read_timeout should be >= 0")
        #if write_timeout is not None and write_timeout <= 0:
        #    raise ValueError("write_timeout should be >= 0")
        if connect_timeout is not None or read_timeout is not None:
            self.timeout = (connect_timeout, read_timeout)

        self.cursorclass = cursorclass

        self._result = None
        self._affected_rows = 0

        self.connect()

    def connect(self):
        self._closed = False
        self._execute_command("select 1;")
        self._read_ok_packet()

    def close(self):
        """
        Send the quit message and close the socket.

        See `Connection.close() <https://www.python.org/dev/peps/pep-0249/#Connection.close>`_
        in the specification.

        :raise Error: If the connection is already closed.
        """
        if self._closed:
            raise err.Error("Already closed")
        self._closed = True

    @property
    def open(self):
        """Return True if the connection is open"""
        return not self._closed

    def commit(self):
        """
        Commit changes to stable storage.

        See `Connection.commit() <https://www.python.org/dev/peps/pep-0249/#commit>`_
        in the specification.
        """
        return
        #self._execute_command("COMMIT")
        #self._read_ok_packet()

    def rollback(self):
        """
        Roll back the current transaction.

        See `Connection.rollback() <https://www.python.org/dev/peps/pep-0249/#rollback>`_
        in the specification.
        """
        return
        #self._execute_command("ROLLBACK")
        #self._read_ok_packet()


    def cursor(self, cursor=None):
        """
        Create a new cursor to execute queries with.

        :param cursor: The type of cursor to create; current only :py:class:`Cursor`
            None means use Cursor.
        """
        if cursor:
            return cursor(self)
        return self.cursorclass(self)

    # The following methods are INTERNAL USE ONLY (called from Cursor)
    def query(self, sql):
        if isinstance(sql, text_type) and not (JYTHON or IRONPYTHON):
            if PY2:
                sql = sql.encode(self.encoding)
            else:
                sql = sql.encode(self.encoding, 'surrogateescape')
        self._execute_command(sql)
        self._affected_rows = self._read_query_result()
        return self._affected_rows

    def _execute_command(self, sql):
        """
        :raise InterfaceError: If the connection is closed.
        :raise ValueError: If no username was specified.
        """
        if self._closed:
            raise err.InterfaceError("Connection closed")

        if isinstance(sql, text_type):
            sql = sql.encode(self.encoding)

        if isinstance(sql, bytearray):
            sql = bytes(sql)

        # drop last command return
        if self._resp is not None:
            self._resp = None

        # post request
        data = {"database": self.database,"query": sql}
        if DEBUG:
            print("DEBUG: sending query:", sql)
        try:
            if (sql.lower().lstrip().startswith(b'select') or
                sql.lower().lstrip().startswith(b'show') or
                sql.lower().lstrip().startswith(b'desc')):
                self._resp = self._send(self._query_uri, data=data)
            else:
                self._resp = self._send(self._exec_uri, data=data)
        except Exception as error:
            raise err.InterfaceError("Request proxy err: %s" % error)

        try:
            self._resp_json = self._resp.json()
            if DEBUG:
                print("DEBUG: response:", self._resp_json)
        except Exception as error:
            raise err.InterfaceError("Proxy return invalid data", self._resp.reason)

    def _send(self, uri, data):
        session = requests.Session()
        session.verify = False
        session.cert = self._cert
        return session.post(uri, data, timeout=self.timeout)

    def escape(self, obj, mapping=None):
        """Escape whatever value you pass to it.

        Non-standard, for internal use; do not use this in your applications.
        """
        if isinstance(obj, str_type):
            return "'" + self.escape_string(obj) + "'"
        if isinstance(obj, (bytes, bytearray)):
            ret = self._quote_bytes(obj)
            return ret
        return converters.escape_item(obj, mapping=mapping)

    def escape_string(self, s):
        return converters.escape_string(s)

    def _quote_bytes(self, s):
        return converters.escape_bytes(s)

    def _read_query_result(self):
        self._result = None
        self._read_ok_packet()
        result = CovenantSQLResult(self)
        result.read()
        self._result = result
        return result.affected_rows

    def _read_ok_packet(self):
        self.server_status = self._resp_json["success"]
        if not self.server_status:
            raise err.InternalError("InternalError: ", self._resp_json["status"])

        if not self._resp.ok:
            raise err.OperationalError("Proxy return false", self._resp.reason)

        return self.server_status

    def __enter__(self):
        """Context manager that returns a Cursor"""
        return self.cursor()

    def __exit__(self, exc, value, traceback):
        """On successful exit, commit. On exception, rollback"""
        if exc:
            self.rollback()
        else:
            self.commit()

class CovenantSQLResult(object):
    def __init__(self, connection):
        """
        :type connection: Connection
        """
        self.connection = connection
        self.affected_rows = 0
        self.insert_id = None
        self.warning_count = 0
        self.message = None
        self.field_count = 0
        self.description = None
        self.rows = None
        self.has_next = None

    def read(self):
        try:
            data = self.connection._resp_json["data"]
        except:
            raise err.InterfaceError("Unsupported response format: no data field")
        if data is None:
            # exec result
            return

        # read json data
        try:
            # return from query api, data like {'columns': ['name'], 'rows': [['test'], ['test2'], ['test3'], ['test4']], 'types': ['TEXT']}
            self.affected_rows = len(data['rows'])
        except:
            # return from exec api, data like {'affected_rows': 4, 'last_insert_id': 4}
            self.affected_rows = data['affected_rows']
            self.insert_id = data['last_insert_id']
            return

        rows = []
        for line in data['rows']:
            row = []
            for column in line:
                row.append(column)
            rows.append(tuple(row))
        self.rows = tuple(rows)

        try:
            self.field_count = len(data['columns'])

            description = []
            for i in range(self.field_count):
                fields = []
                fields.append(data['columns'][i])
                fields.append(data['types'][i])
                description.append(tuple(fields))
            self.description = tuple(description)
        except:
            raise err.InterfaceError("Proxy return column count and types count are not equal")
