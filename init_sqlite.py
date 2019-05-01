import os
import sqlite3

DATABASE = "product.db"


def get_db():
    db = sqlite3.connect(DATABASE)
    return db


def init_db():
    db = get_db()
    with open('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def remove_db():
    if os.path.isfile(DATABASE):
        os.remove(DATABASE)


if __name__ == '__main__':
    db = get_db()
    init_db()
