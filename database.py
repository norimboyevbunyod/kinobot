import sqlite3

def db_query(query, params=(), fetch=False, one=False):
    with sqlite3.connect('kinobaza.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetch: return cursor.fetchone() if one else cursor.fetchall()
        conn.commit()

def init_db():
    db_query("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, lang TEXT DEFAULT 'uz')")
    db_query("CREATE TABLE IF NOT EXISTS admins (id INTEGER PRIMARY KEY)")
    db_query("CREATE TABLE IF NOT EXISTS channels (id TEXT PRIMARY KEY, url TEXT)")
    db_query("CREATE TABLE IF NOT EXISTS movies (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, file_id TEXT, views INTEGER DEFAULT 0)")
    db_query("CREATE TABLE IF NOT EXISTS serials (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, part INTEGER, file_id TEXT)")