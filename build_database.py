import sqlite3

conn = sqlite3.connect('hardwax.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS ARTISTS (
        artist_id INTEGER PRIMARY KEY AUTOINCREMENT,
        artist_name TEXT NOT NULL UNIQUE
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS LABELS (
        label_id INTEGER PRIMARY KEY AUTOINCREMENT,
        label_name TEXT NOT NULL UNIQUE
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS FORMATS (
        format_id INTEGER PRIMARY KEY AUTOINCREMENT,
        format_name TEXT NOT NULL UNIQUE
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS RELEASES (
        release_id INTEGER PRIMARY KEY AUTOINCREMENT,
        artist_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        catalog_number TEXT,
        price TEXT,
        image_url TEXT,
        label_id INTEGER NOT NULL,
        FOREIGN KEY (artist_id) REFERENCES ARTISTS(artist_id),
        FOREIGN KEY (label_id) REFERENCES LABELS(label_id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS RELEASE_FORMATS (
        release_id INTEGER NOT NULL,
        format_id INTEGER NOT NULL,
        PRIMARY KEY (release_id, format_id),
        FOREIGN KEY (release_id) REFERENCES RELEASES(release_id),
        FOREIGN KEY (format_id) REFERENCES FORMATS(format_id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS TRACKS (
        track_id INTEGER PRIMARY KEY AUTOINCREMENT,
        release_id INTEGER NOT NULL,
        track_name TEXT NOT NULL,
        FOREIGN KEY (release_id) REFERENCES RELEASES(release_id)
    )
''')

conn.commit()
conn.close()

print("Database created successfully: hardwax.db")
