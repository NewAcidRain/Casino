import sqlite3

database_path = 'server.db'
db = sqlite3.connect(database_path)
sql = db.cursor()


def create_table(table_name: str, column_titles: dict):
    """
    Создать таблицу в базе данных, чего не понятного?
    :param column_titles:
    :param table_name: ключ - имя, значение - тип
    """

    sql.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    if len(sql.fetchall()) == 0:
        sql.execute(
            f'CREATE TABLE IF NOT EXISTS {table_name}({list(column_titles.keys())[0]} {column_titles[list(column_titles.keys())[0]]});')
        for i in list(column_titles.keys())[1:]:
            sql.execute(f'ALTER TABLE {table_name} ADD {i} {column_titles[i]};')
        db.commit()


def add_record(table_name: str, value: iter):
    """
    Добавляет запись в таблицу, в случае возникновения ошибки - возвращает её
    :param table_name:
    :param value:
    :return:
    """
    sql.execute(f'PRAGMA TABLE_INFO({table_name})')
    if len(value) == len(sql.fetchall()):
        try:
            sql.execute(f'INSERT INTO {table_name} VALUES({("?, " * len(value))[:-2]})', tuple(value))
            db.commit()
            return 'Success'
        except Exception as e:
            print("DATABASE: ", str(e))
            return f'CRITICAL ERROR\n{str(e)}\nОбратитесь к @artem_pas'
    else:
        raise IndexError


def remove_record(table_name: str, column_name: str, value):
    """
    Удаляет запись из таблицы Вывод -> Bool
    :param table_name:
    :param column_name:
    :param value:
    :return:
    """
    if column_name == '*' and value == '*':
        try:
            sql.execute(f'DELETE FROM {table_name}')
        except Exception as e:
            print("DATABASE: ", str(e))
            return False
        db.commit()
        return True
    else:
        try:
            sql.execute(f'DELETE FROM {table_name} WHERE {column_name} = ?', (value,))
        except Exception as e:
            print("DATABASE: " + str(e))
            return False
        db.commit()
        return True


def read_table(table_name: str, column_name=None, value=None):
    """
    Читает записи из базы данных, при
    отсутствии значений у параметров column_name и value
    возвращает все значения из таблицы
    :param table_name:
    :param column_name:
    :param value:
    :return:
    """
    if column_name is not None and value is not None:
        sql.execute(f"SELECT * FROM {table_name} WHERE {column_name} = ?", (value,))
        db.commit()
        return sql.fetchall()
    else:
        sql.execute(f'SELECT * FROM {table_name}')
        db.commit()
        try:
            return sql.fetchall()
        except UnicodeEncodeError:
            pass
