import sqlite3


global db
global sql


db = sqlite3.connect('server.db')
sql = db.cursor()

sql.execute("""CREATE TABLE IF NOT EXISTS users (
        cash BIGINT
        id BIGINT)""")

db.commit()


def balance(x:int):
    sql.execute(f'UPDATE users SET cash = cash + {x} ')