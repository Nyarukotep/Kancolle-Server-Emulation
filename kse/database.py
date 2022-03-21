__all__ = ['database']
import sqlite3
class database:
    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self.conn.isolation_level = None
    def insert(self, table_name, content):
        content = tuple(content)
        sql = 'INSERT INTO \'' + table_name + '\' VALUES ' + str(content)
        self.conn.execute(sql.replace('$table_name', table_name))
    def update(self, table_name, column, column_value, row, row_value):
        row_value = tuple(row_value)
        sql = 'UPDATE \''+ table_name + '\' SET '
        sql += ', '.join([column[i]+'=\''+column_value[i]+'\'' for i in range(len(column))])
        self.conn.execute(sql)
    def delete(self, table_name, row, row_value):
        row_value = tuple(row_value)
        sql = 'DELETE FROM \''+ table_name + '\' WHERE '
        sql += row + 'IN ' + str(row_value)
        self.conn.execute(sql)
    def select(self, table_name, column, row, row_value):
        row_value = tuple(row_value)
        if column:
            column = ', '.join(column)
        else:
            column = '*'
        sql = 'SELECT ' + column + ' FROM \''+ table_name+ '\' WHERE '
        sql += row + 'IN ' + str(row_value)
        result = self.conn.execute(sql).fetchall()
        return [list(value) for value in result]
    def blob(self, table_name, id):
        sql = 'SELECT content FROM \''+ table_name+ '\' WHERE id IN ' + str(tuple(id))
        result = self.conn.execute(sql).fetchone()
        return result
    def exit(self):
        self.conn.close()