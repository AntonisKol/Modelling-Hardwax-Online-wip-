import sqlite3
import pytest

def create_tables(cursor):
    """Create all database tables"""
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

def insert_artist(cursor, name):
    cursor.execute("INSERT INTO ARTISTS (artist_name) VALUES (?)", (name,))
    return cursor.lastrowid

def insert_label(cursor, name):
    cursor.execute("INSERT INTO LABELS (label_name) VALUES (?)", (name,))
    return cursor.lastrowid

def insert_format(cursor, name):
    cursor.execute("INSERT INTO FORMATS (format_name) VALUES (?)", (name,))
    return cursor.lastrowid

def insert_release(cursor, title, description, catalog_number, price, label_id):
    cursor.execute('''
        INSERT INTO RELEASES (title, description, catalog_number, price, label_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, description, catalog_number, price, label_id))
    return cursor.lastrowid

def link_artist_to_release(cursor, release_id, artist_id):
    cursor.execute('INSERT INTO RELEASE_ARTISTS (release_id, artist_id) VALUES (?, ?)', (release_id, artist_id))

def link_format_to_release(cursor, release_id, format_id):
    cursor.execute('INSERT INTO RELEASE_FORMATS (release_id, format_id) VALUES (?, ?)', (release_id, format_id))

def insert_track(cursor, release_id, track_name):
    cursor.execute('INSERT INTO TRACKS (release_id, track_name) VALUES (?, ?)', (release_id, track_name))

@pytest.fixture
def test_db():
    """Create fresh test database for each test"""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    create_tables(cursor)
    
    artist1_id = insert_artist(cursor, 'Test Artist 1')
    artist2_id = insert_artist(cursor, 'Test Artist 2')
    
    label1_id = insert_label(cursor, 'Test Label A')
    label2_id = insert_label(cursor, 'Test Label B')
    
    format1_id = insert_format(cursor, '12"')
    format2_id = insert_format(cursor, 'LP')
    
    release1_id = insert_release(cursor, 'Test Release 1', 'A test release', '001', '€ 12', label1_id)
    release2_id = insert_release(cursor, 'Test Release 2', 'Another test', '002', '€ 15', label2_id)
    release3_id = insert_release(cursor, 'Test Release 3', 'Third release', '003', '€ 20', label1_id)
    
    link_artist_to_release(cursor, release1_id, artist1_id)
    link_artist_to_release(cursor, release2_id, artist2_id)
    link_artist_to_release(cursor, release3_id, artist1_id)
    
    link_format_to_release(cursor, release1_id, format1_id)
    link_format_to_release(cursor, release2_id, format2_id)
    link_format_to_release(cursor, release3_id, format2_id)
    
    insert_track(cursor, release1_id, 'Track 1A')
    insert_track(cursor, release1_id, 'Track 1B')
    insert_track(cursor, release1_id, 'Track 1C')
    insert_track(cursor, release2_id, 'Track 2A')
    insert_track(cursor, release2_id, 'Track 2B')
    
    conn.commit()
    yield conn, cursor
    conn.close()

def test_query_all_releases(test_db):
    conn, cursor = test_db
    query = '''
        SELECT a.artist_name, r.title, l.label_name
        FROM RELEASES r
        JOIN RELEASE_ARTISTS ra ON r.release_id = ra.release_id
        JOIN ARTISTS a ON ra.artist_id = a.artist_id
        JOIN LABELS l ON r.label_id = l.label_id
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    assert len(results) == 3

def test_query_by_label(test_db):
    conn, cursor = test_db
    query = '''
        SELECT r.title, l.label_name
        FROM RELEASES r
        JOIN LABELS l ON r.label_id = l.label_id
        WHERE l.label_name = ?
    '''
    cursor.execute(query, ('Test Label A',))
    results = cursor.fetchall()
    assert len(results) == 2

def test_query_by_format(test_db):
    conn, cursor = test_db
    query = '''
        SELECT COUNT(*) as count
        FROM RELEASE_FORMATS rf
        JOIN FORMATS f ON rf.format_id = f.format_id
        WHERE f.format_name = ?
    '''
    cursor.execute(query, ('LP',))
    result = cursor.fetchone()
    assert result[0] == 2

def test_query_release_with_tracks(test_db):
    conn, cursor = test_db
    release_query = '''
        SELECT release_id FROM RELEASES WHERE title = ?
    '''
    cursor.execute(release_query, ('Test Release 1',))
    release_id = cursor.fetchone()[0]
    tracks_query = '''
        SELECT track_name FROM TRACKS WHERE release_id = ? ORDER BY track_id
    '''
    cursor.execute(tracks_query, (release_id,))
    tracks = cursor.fetchall()
    assert len(tracks) == 3

def test_query_artist_discography(test_db):
    conn, cursor = test_db
    query = '''
        SELECT r.title FROM RELEASES r
        JOIN RELEASE_ARTISTS ra ON r.release_id = ra.release_id
        JOIN ARTISTS a ON ra.artist_id = a.artist_id
        WHERE a.artist_name = ?
    '''
    cursor.execute(query, ('Test Artist 1',))
    results = cursor.fetchall()
    assert len(results) == 2

def test_query_keyword_search(test_db):
    conn, cursor = test_db
    query = '''
        SELECT r.title FROM RELEASES r WHERE r.title LIKE ?
    '''
    cursor.execute(query, ('%Test Release%',))
    results = cursor.fetchall()
    assert len(results) == 3

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
