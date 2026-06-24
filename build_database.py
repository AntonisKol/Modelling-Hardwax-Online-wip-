import sqlite3

conn = sqlite3.connect('hardwax.db')
cursor = conn.cursor()

# Create in correct order
cursor.execute('''
    CREATE TABLE ARTISTS (
        artist_id INTEGER PRIMARY KEY AUTOINCREMENT,
        artist_name TEXT NOT NULL UNIQUE
    )
''')

cursor.execute('''
    CREATE TABLE LABELS (
        label_id INTEGER PRIMARY KEY AUTOINCREMENT,
        label_name TEXT NOT NULL UNIQUE
    )
''')

cursor.execute('''
    CREATE TABLE FORMATS (
        format_id INTEGER PRIMARY KEY AUTOINCREMENT,
        format_name TEXT NOT NULL UNIQUE
    )
''')

cursor.execute('''
    CREATE TABLE RELEASES (
        release_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        catalog_number TEXT,
        price TEXT,
        image_url TEXT,
        label_id INTEGER NOT NULL,
        FOREIGN KEY (label_id) REFERENCES LABELS(label_id)
    )
''')

cursor.execute('''
    CREATE TABLE RELEASE_ARTISTS (
        release_artist_join_id INTEGER PRIMARY KEY AUTOINCREMENT,
        release_id INTEGER NOT NULL,
        artist_id INTEGER NOT NULL,
        FOREIGN KEY (release_id) REFERENCES RELEASES(release_id),
        FOREIGN KEY (artist_id) REFERENCES ARTISTS(artist_id)
    )
''')

cursor.execute('''
    CREATE TABLE RELEASE_FORMATS (
        release_id INTEGER NOT NULL,
        format_id INTEGER NOT NULL,
        PRIMARY KEY (release_id, format_id),
        FOREIGN KEY (release_id) REFERENCES RELEASES(release_id),
        FOREIGN KEY (format_id) REFERENCES FORMATS(format_id)
    )
''')

cursor.execute('''
    CREATE TABLE TRACKS (
        track_id INTEGER PRIMARY KEY AUTOINCREMENT,
        release_id INTEGER NOT NULL,
        track_name TEXT NOT NULL,
        FOREIGN KEY (release_id) REFERENCES RELEASES(release_id)
    )
''')

conn.commit()
conn.close()

print("Database created successfully: hardwax.db")
