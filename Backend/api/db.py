import os
import re
import sqlite3
import tempfile

import pymysql
from flask import current_app


def _ssl_options():
    ca_path = current_app.config.get('MYSQL_SSL_CA')
    ca_content = current_app.config.get('MYSQL_SSL_CA_CONTENT')

    if ca_content:
        ca_path = os.path.join(tempfile.gettempdir(), 'aiven-ca.pem')
        if not os.path.exists(ca_path):
            with open(ca_path, 'w', encoding='utf-8') as ca_file:
                ca_file.write(ca_content.replace('\\n', '\n'))

    return {'ca': ca_path} if ca_path else None


_sqlite_test_db_path = os.path.join(tempfile.gettempdir(), 'volunteer_management_test.sqlite3')
_sqlite_initialized = False


def _initialize_sqlite_test_db():
    global _sqlite_initialized
    if _sqlite_initialized and os.path.exists(_sqlite_test_db_path):
        return

    if os.path.exists(_sqlite_test_db_path):
        os.remove(_sqlite_test_db_path)

    conn = sqlite3.connect(_sqlite_test_db_path)
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS usercredentials (
              user_id INTEGER PRIMARY KEY AUTOINCREMENT,
              email TEXT NOT NULL UNIQUE COLLATE NOCASE,
              password_hash TEXT NOT NULL,
              role TEXT NOT NULL,
              created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS verification_codes (
              email TEXT PRIMARY KEY COLLATE NOCASE,
              code INTEGER NOT NULL,
              verified INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS eventdetails (
              event_id INTEGER PRIMARY KEY AUTOINCREMENT,
              event_name TEXT NOT NULL,
              required_skills TEXT NOT NULL,
              address TEXT NOT NULL,
              state TEXT NOT NULL,
              city TEXT NOT NULL,
              zipcode TEXT NOT NULL,
              urgency TEXT NOT NULL,
              location_name TEXT NOT NULL,
              event_duration INTEGER NOT NULL,
              event_description TEXT NOT NULL,
              date TEXT NOT NULL,
              created_at TEXT DEFAULT CURRENT_TIMESTAMP,
              event_status TEXT DEFAULT 'Pending',
              volunteers_needed INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS notifications (
              notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER NOT NULL,
              message TEXT NOT NULL,
              event_date TEXT NOT NULL,
              read INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS skills (
              skills_id INTEGER PRIMARY KEY AUTOINCREMENT,
              skill_name TEXT NOT NULL UNIQUE,
              skill_description TEXT
            );

            CREATE TABLE IF NOT EXISTS states (
              state_id INTEGER PRIMARY KEY AUTOINCREMENT,
              state_name TEXT NOT NULL,
              abbreviation TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS userprofile (
              volunteer_id INTEGER PRIMARY KEY,
              full_name TEXT NOT NULL,
              address1 TEXT,
              address2 TEXT,
              city TEXT NOT NULL,
              state_name TEXT NOT NULL,
              zipcode TEXT NOT NULL,
              preferences TEXT,
              date_of_birth TEXT NOT NULL,
              phone_number TEXT
            );

            CREATE TABLE IF NOT EXISTS volunteer_availability (
              availability_id INTEGER PRIMARY KEY AUTOINCREMENT,
              volunteer_id INTEGER NOT NULL,
              date_available TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS volunteer_skills (
              volunteer_skills_id INTEGER PRIMARY KEY AUTOINCREMENT,
              volunteer_id INTEGER NOT NULL,
              skill_id INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS required_skills (
              required_skills_id INTEGER PRIMARY KEY AUTOINCREMENT,
              event_id INTEGER NOT NULL,
              skills_id INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS volunteerhistory (
              event_id INTEGER NOT NULL,
              volunteer_id INTEGER NOT NULL,
              participation_status TEXT NOT NULL DEFAULT 'Registered',
              performance INTEGER,
              notes TEXT,
              PRIMARY KEY (event_id, volunteer_id)
            );
        """)
        conn.commit()
        _sqlite_initialized = True
    finally:
        conn.close()


def _sqlite_regexp(pattern, value):
    if value is None:
        return False
    return re.search(pattern, str(value)) is not None


def _sqlite_substring_index(value, delimiter, count):
    if value is None:
        return None
    parts = str(value).split(str(delimiter))
    count = int(count)
    if count >= 0:
        return str(delimiter).join(parts[:count])
    return str(delimiter).join(parts[count:])


class _SQLiteTestCursor:
    def __init__(self, cursor):
        self._cursor = cursor
        self._manual_rows = None

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    @property
    def rowcount(self):
        return self._cursor.rowcount

    def execute(self, query, params=None):
        self._manual_rows = None
        sql = _translate_sql(query)

        if sql == '__SHOW_TABLES__':
            self._cursor.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
            db_name = current_app.config.get('MYSQL_DB', 'test_db')
            self._manual_rows = [{f'Tables_in_{db_name}': row[0]} for row in self._cursor.fetchall()]
            return self

        if sql.startswith('__TRUNCATE__:'):
            table_name = sql.split(':', 1)[1]
            self._cursor.execute(f'DELETE FROM "{table_name}"')
            self._cursor.execute("DELETE FROM sqlite_sequence WHERE name = ?", (table_name,))
            return self

        if sql.startswith('PRAGMA foreign_keys'):
            self._cursor.execute(sql)
            return self

        if params is None:
            params = ()
        elif not isinstance(params, (list, tuple)):
            params = (params,)

        self._cursor.execute(sql, params)
        return self

    def fetchone(self):
        if self._manual_rows is not None:
            return self._manual_rows.pop(0) if self._manual_rows else None
        row = self._cursor.fetchone()
        return dict(row) if row is not None else None

    def fetchall(self):
        if self._manual_rows is not None:
            rows = self._manual_rows
            self._manual_rows = []
            return rows
        return [dict(row) for row in self._cursor.fetchall()]

    def close(self):
        self._cursor.close()


class _SQLiteTestConnection:
    def __init__(self, connection):
        self._connection = connection

    def cursor(self):
        return _SQLiteTestCursor(self._connection.cursor())

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
        self._connection.close()


def _translate_sql(query):
    sql = ' '.join(str(query).strip().rstrip(';').split())
    upper_sql = sql.upper()

    if upper_sql.startswith('SET FOREIGN_KEY_CHECKS=0'):
        return 'PRAGMA foreign_keys = OFF'
    if upper_sql.startswith('SET FOREIGN_KEY_CHECKS=1'):
        return 'PRAGMA foreign_keys = ON'
    if upper_sql == 'SHOW TABLES':
        return '__SHOW_TABLES__'

    truncate_match = re.match(r'TRUNCATE\s+TABLE\s+`?([A-Za-z_][A-Za-z0-9_]*)`?', sql, re.IGNORECASE)
    if truncate_match:
        return f'__TRUNCATE__:{truncate_match.group(1)}'

    sql = sql.replace('defaultdb.', '')
    sql = sql.replace('`read`', 'read')
    sql = re.sub(r'\bCURDATE\(\)', "DATE('now')", sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bNOW\(\)', "CURRENT_TIMESTAMP", sql, flags=re.IGNORECASE)
    sql = re.sub(
        r"DATE_SUB\(\s*DATE\('now'\)\s*,\s*INTERVAL\s+(\d+)\s+DAY\s*\)",
        lambda match: f"DATE('now', '-{match.group(1)} day')",
        sql,
        flags=re.IGNORECASE,
    )
    sql = re.sub(
        r"DATE_SUB\(\s*DATE\('now'\)\s*,\s*INTERVAL\s+(\d+)\s+MONTH\s*\)",
        lambda match: f"DATE('now', '-{match.group(1)} month')",
        sql,
        flags=re.IGNORECASE,
    )
    sql = re.sub(
        r'DATE_SUB\(\s*CURRENT_TIMESTAMP\s*,\s*INTERVAL\s+(\d+)\s+DAY\s*\)',
        lambda match: f"DATETIME('now', '-{match.group(1)} day')",
        sql,
        flags=re.IGNORECASE,
    )
    sql = re.sub(
        r'DATE_FORMAT\(\s*([^,]+?)\s*,\s*[\'"]%%?Y-%%?m-%%?d[\'"]\s*\)',
        r"strftime('%Y-%m-%d', \1)",
        sql,
        flags=re.IGNORECASE,
    )
    sql = re.sub(
        r'DATE_FORMAT\(\s*([^,]+?)\s*,\s*[\'"]%%?Y-%%?m[\'"]\s*\)',
        r"strftime('%Y-%m', \1)",
        sql,
        flags=re.IGNORECASE,
    )
    sql = re.sub(
        r'GROUP_CONCAT\(\s*DISTINCT\s+(.+?)\s+ORDER\s+BY\s+.+?\s+SEPARATOR\s+[\'"],\s*[\'"]\s*\)',
        r'GROUP_CONCAT(DISTINCT \1)',
        sql,
        flags=re.IGNORECASE,
    )
    sql = re.sub(
        r'GROUP_CONCAT\(\s*(.+?)\s+ORDER\s+BY\s+.+?\s+SEPARATOR\s+[\'"],\s*[\'"]\s*\)',
        r"GROUP_CONCAT(\1, ', ')",
        sql,
        flags=re.IGNORECASE,
    )
    sql = re.sub(
        r'GROUP_CONCAT\(\s*DISTINCT\s+(.+?)\s+SEPARATOR\s+[\'"],\s*[\'"]\s*\)',
        r'GROUP_CONCAT(DISTINCT \1)',
        sql,
        flags=re.IGNORECASE,
    )
    sql = re.sub(
        r'GROUP_CONCAT\(\s*(.+?)\s+SEPARATOR\s+[\'"],\s*[\'"]\s*\)',
        r"GROUP_CONCAT(\1, ', ')",
        sql,
        flags=re.IGNORECASE,
    )
    return sql.replace('%s', '?')


def _get_sqlite_test_db():
    _initialize_sqlite_test_db()
    connection = sqlite3.connect(_sqlite_test_db_path)
    connection.row_factory = sqlite3.Row
    connection.create_function('REGEXP', 2, _sqlite_regexp)
    connection.create_function('SUBSTRING_INDEX', 3, _sqlite_substring_index)
    return _SQLiteTestConnection(connection)


def get_db():
    try:
        if current_app.config.get('USE_SQLITE_TEST_DB'):
            return _get_sqlite_test_db()

        connect_kwargs = dict(
            host=current_app.config['MYSQL_HOST'],
            port=current_app.config.get('MYSQL_PORT', 3306),
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            db=current_app.config['MYSQL_DB'],
            cursorclass=pymysql.cursors.DictCursor
        )

        ssl = _ssl_options()
        if ssl:
            connect_kwargs['ssl'] = ssl

        connection = pymysql.connect(**connect_kwargs)
        return connection
    except Exception as e:
        print("Error connecting to DB:", e)
        raise
