# Credit hasancagrigungor this script is taken from one of their repos (i've slightly edited it)

import sqlite3
import pandas as pd

class Database:
    
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()

    def create_table(self, table_name, *columns):
        columns_sql = ", ".join(columns)
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"
        self.c.execute(sql)
        self.conn.commit()
    
    def add(self, table_name, *data):
        placeholder = ",".join(len(data) * ["?"])
        sql = f"INSERT INTO {table_name} VALUES({placeholder})"
        self.c.execute(sql, data)
        self.conn.commit()
    
    def get(self, table_name, where=None):
        sql = f"SELECT * FROM {table_name}"
        if where:
            sql = sql + f' WHERE {where}'
        self.c.execute(sql)
        return self.c.fetchall()
    
    def update(self, table_name, set_clause, where):
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {where}"
        self.c.execute(sql)
        self.conn.commit()

    def delete(self, table_name, where):
        sql = f"DELETE FROM {table_name} WHERE {where}"
        self.c.execute(sql)
        self.conn.commit()

    def exists(self, table_name, where):
        sql = f"SELECT * FROM {table_name} WHERE {where}"
        self.c.execute(sql)
        data = self.c.fetchall()
        return len(data) > 0
    
    def close(self):
        self.conn.close()