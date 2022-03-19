__all__ = ['database']
import sqlite3
class database:
    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self.conn.isolation_level = None
    def insert(self, table_name, content):
        if isinstance(content, list): content = tuple(content)
        sql = 'INSERT INTO \'$table_name\' VALUES ' + str(content)
        self.conn.execute(sql.replace('$table_name', table_name))
    def delete(self, table_name, filter):
        if isinstance(filter, str):
            sql = 'DELETE FROM \'$table_name\' WHERE ' + filter
            self.conn.execute(sql.replace('$table_name', table_name))
        else:
            sql = 'DELETE FROM \'$table_name\' WHERE ' + str(filter[0]) + '=\'' + str(filter[1]) + '\''
            self.conn.execute(sql.replace('$table_name', table_name))
    def select(self, table_name, column, filter):
        column = str(column)[1:-1]
        column = column.replace("'",'')
        column = column.replace('"','')
        if isinstance(filter, str):
            sql = 'SELECT ' + column + ' FROM \'$table_name\' WHERE ' + filter
            return self.conn.execute(sql.replace('$table_name', table_name)).fetchall()
        else:
            sql = 'SELECT ' + column + ' FROM \'$table_name\' WHERE ' + str(filter[0]) + '=\'' + str(filter[1]) + '\''
            return self.conn.execute(sql.replace('$table_name', table_name)).fetchall()
    def blob(self, table_name, id):
        return self.select(table_name, ['content'], ['id', id])[0][0]

    def indb(self, target):
        cat = {
            '/': '$resource',
        }
        return cat.get(target,0)

    def exit(self):
        self.conn.close()
    SELECT * FROM COMPANY WHERE AGE IN ( 25, 27 );