import sqlite3

DB_NAME = 'hardwax.db'

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def close_connection(conn):
    """Close database connection"""
    conn.close()
