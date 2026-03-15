# Credit hasancagrigungor this script is taken from one of their repos (i've slightly edited it)

import sqlite3
import pandas as pd
import re

IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

class Database:
    
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()

    def _validate_identifier(self, name):
        if not IDENTIFIER.match(name):
            raise ValueError("Invalid SQL identifier")

    def create_table(self, table_name, *columns):
        self._validate_identifier(table_name)

        validated_columns = []
        for col in columns:
            col_name = col.split()[0]
            self._validate_identifier(col_name)
            validated_columns.append(col)

        columns_sql = ", ".join(validated_columns)
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"
        self.c.execute(sql)
        self.conn.commit()
    
    def add(self, table_name, *data):
        self._validate_identifier(table_name)

        placeholders = ",".join(["?"] * len(data))
        sql = f"INSERT INTO {table_name} VALUES({placeholders})"
        self.c.execute(sql, data)
        self.conn.commit()

    def get(self, table_name, where=None):
        self._validate_identifier(table_name)

        sql = f"SELECT * FROM {table_name}"
        values = []

        if where:
            clauses = []
            for col, val in where.items():
                self._validate_identifier(col)
                clauses.append(f"{col}=?")
                values.append(val)

            sql += " WHERE " + " AND ".join(clauses)

        self.c.execute(sql, values)
        return self.c.fetchall()


    def update(self, table_name, updates, where):
        self._validate_identifier(table_name)

        set_clauses = []
        values = []

        for col, val in updates.items():
            self._validate_identifier(col)
            set_clauses.append(f"{col}=?")
            values.append(val)

        where_clauses = []
        for col, val in where.items():
            self._validate_identifier(col)
            where_clauses.append(f"{col}=?")
            values.append(val)

        sql = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE {' AND '.join(where_clauses)}"

        self.c.execute(sql, values)
        self.conn.commit()


    def delete(self, table_name, where):
        self._validate_identifier(table_name)

        clauses = []
        values = []

        for col, val in where.items():
            self._validate_identifier(col)
            clauses.append(f"{col}=?")
            values.append(val)

        sql = f"DELETE FROM {table_name} WHERE {' AND '.join(clauses)}"

        self.c.execute(sql, values)
        self.conn.commit()

    def exists(self, table_name, column, value):
        self._validate_identifier(table_name)
        self._validate_identifier(column)

        sql = f"SELECT 1 FROM {table_name} WHERE {column}=? LIMIT 1"
        self.c.execute(sql, (value,))
        return self.c.fetchone() is not None
    
    def close(self):
        self.conn.close()