import sqlite3
import pytest


def setup_test_db(): # creates a fresh database for each test
    """Create a fresh test database with known data"""
    conn = sqlite3.connect(':memory:')  # creates a database in RAM (not on disk), so it's fast and clean for testing
    cursor = conn.cursor()
    
    # Core functionality — can you fetch all data with JOINs?
    cursor.execute('''
        CREATE TABLE ARTISTS (
            artist_id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_name TEXT NOT NULL UNIQUE
        )
    ''')
    # Filtering — does WHERE clause work? Does GROUP BY work?
    cursor.execute('''
        CREATE TABLE LABELS (
            label_id INTEGER PRIMARY KEY AUTOINCREMENT,
            label_name TEXT NOT NULL UNIQUE
        )
    ''')
    # Aggregation — does COUNT(*) work?
    cursor.execute('''
        CREATE TABLE FORMATS (
            format_id INTEGER PRIMARY KEY AUTOINCREMENT,
            format_name TEXT NOT NULL UNIQUE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE RELEASES (
            release_id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            catalog_number TEXT,
            price TEXT,
            image_url TEXT,
            label_id INTEGER NOT NULL,
            format_id INTEGER NOT NULL,
            FOREIGN KEY (artist_id) REFERENCES ARTISTS(artist_id),
            FOREIGN KEY (label_id) REFERENCES LABELS(label_id),
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
    
    # Insert known test data
    # Artists
    cursor.execute("INSERT INTO ARTISTS (artist_name) VALUES ('Test Artist 1')")
    artist1_id = cursor.lastrowid
    cursor.execute("INSERT INTO ARTISTS (artist_name) VALUES ('Test Artist 2')")
    artist2_id = cursor.lastrowid
    
    # Labels
    cursor.execute("INSERT INTO LABELS (label_name) VALUES ('Test Label A')")
    label1_id = cursor.lastrowid
    cursor.execute("INSERT INTO LABELS (label_name) VALUES ('Test Label B')")
    label2_id = cursor.lastrowid
    
    # Formats
    cursor.execute("INSERT INTO FORMATS (format_name) VALUES ('12\"')")
    format1_id = cursor.lastrowid
    cursor.execute("INSERT INTO FORMATS (format_name) VALUES ('LP')")
    format2_id = cursor.lastrowid
    
    # Releases
    cursor.execute('''
        INSERT INTO RELEASES 
        (artist_id, title, description, catalog_number, price, label_id, format_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (artist1_id, 'Test Release 1', 'A test release', '001', '€ 12', label1_id, format1_id))
    release1_id = cursor.lastrowid
    
    cursor.execute('''
        INSERT INTO RELEASES 
        (artist_id, title, description, catalog_number, price, label_id, format_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (artist2_id, 'Test Release 2', 'Another test', '002', '€ 15', label2_id, format2_id))
    release2_id = cursor.lastrowid
    
    cursor.execute('''
        INSERT INTO RELEASES 
        (artist_id, title, description, catalog_number, price, label_id, format_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (artist1_id, 'Test Release 3', 'Third release', '003', '€ 20', label1_id, format2_id))
    release3_id = cursor.lastrowid
    
    # Tracks for release 1
    cursor.execute("INSERT INTO TRACKS (release_id, track_name) VALUES (?, ?)", (release1_id, 'Track 1A'))
    cursor.execute("INSERT INTO TRACKS (release_id, track_name) VALUES (?, ?)", (release1_id, 'Track 1B'))
    cursor.execute("INSERT INTO TRACKS (release_id, track_name) VALUES (?, ?)", (release1_id, 'Track 1C'))
    
    # Tracks for release 2
    cursor.execute("INSERT INTO TRACKS (release_id, track_name) VALUES (?, ?)", (release2_id, 'Track 2A'))
    cursor.execute("INSERT INTO TRACKS (release_id, track_name) VALUES (?, ?)", (release2_id, 'Track 2B'))
    
    conn.commit()
    return conn, cursor

# ============================================================================
# TEST 1: Query all releases
# ============================================================================
def test_query_all_releases():
    """Test that we can fetch all releases"""
    conn, cursor = setup_test_db()
    
    query = '''
        SELECT 
            a.artist_name,
            r.title,
            l.label_name,
            f.format_name,
            r.price
        FROM RELEASES r
        JOIN ARTISTS a ON r.artist_id = a.artist_id
        JOIN LABELS l ON r.label_id = l.label_id
        JOIN FORMATS f ON r.format_id = f.format_id
    '''
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    # Assert we have 3 releases
    assert len(results) == 3, f"Expected 3 releases, got {len(results)}"
    
    # Assert first release has correct data
    assert results[0][0] == 'Test Artist 1'
    assert results[0][1] == 'Test Release 1'
    assert results[0][2] == 'Test Label A'
    assert results[0][3] == '12"'
    
    conn.close()
    print("✓ test_query_all_releases PASSED")

# ============================================================================
# TEST 2: Query releases by label
# ============================================================================
def test_query_by_label():
    """Test that we can filter releases by label"""
    conn, cursor = setup_test_db()
    
    query = '''
        SELECT 
            r.title,
            l.label_name
        FROM RELEASES r
        JOIN LABELS l ON r.label_id = l.label_id
        WHERE l.label_name = ?
    '''
    
    cursor.execute(query, ('Test Label A',))
    results = cursor.fetchall()
    
    # Assert we have 2 releases from Label A
    assert len(results) == 2, f"Expected 2 releases from Label A, got {len(results)}"
    
    # Assert all results are from Label A
    for row in results:
        assert row[1] == 'Test Label A'
    
    conn.close()
    print("✓ test_query_by_label PASSED")

# ============================================================================
# TEST 3: Query releases by format
# ============================================================================
def test_query_by_format():
    """Test that we can filter releases by format"""
    conn, cursor = setup_test_db()
    
    query = '''
        SELECT 
            COUNT(*) as count
        FROM RELEASES r
        JOIN FORMATS f ON r.format_id = f.format_id
        WHERE f.format_name = ?
    '''
    
    cursor.execute(query, ('LP',))
    result = cursor.fetchone()
    
    # Assert we have 2 LP releases
    assert result[0] == 2, f"Expected 2 LP releases, got {result[0]}"
    
    conn.close()
    print("✓ test_query_by_format PASSED")

# ============================================================================
# TEST 4: Query full release details with tracks
# ============================================================================
def test_query_release_with_tracks():
    """Test that we can get a release with all its tracks"""
    conn, cursor = setup_test_db()
    
    # Get release 1
    release_query = '''
        SELECT 
            r.release_id,
            a.artist_name,
            r.title
        FROM RELEASES r
        JOIN ARTISTS a ON r.artist_id = a.artist_id
        WHERE r.title = ?
    '''
    
    cursor.execute(release_query, ('Test Release 1',))
    release = cursor.fetchone()
    release_id = release[0]
    
    # Get tracks for this release
    tracks_query = '''
        SELECT 
            track_name
        FROM TRACKS
        WHERE release_id = ?
    '''
    
    cursor.execute(tracks_query, (release_id,))
    tracks = cursor.fetchall()
    
    # Assert we have 3 tracks
    assert len(tracks) == 3, f"Expected 3 tracks, got {len(tracks)}"
    
    # Assert track names
    assert tracks[0][0] == 'Track 1A'
    assert tracks[1][0] == 'Track 1B'
    assert tracks[2][0] == 'Track 1C'
    
    conn.close()
    print("✓ test_query_release_with_tracks PASSED")

# ============================================================================
# TEST 5: Query artist discography
# ============================================================================
def test_query_artist_discography():
    """Test that we can get all releases by an artist"""
    conn, cursor = setup_test_db()
    
    query = '''
        SELECT 
            r.title,
            a.artist_name
        FROM RELEASES r
        JOIN ARTISTS a ON r.artist_id = a.artist_id
        WHERE a.artist_name = ?
    '''
    
    cursor.execute(query, ('Test Artist 1',))
    results = cursor.fetchall()
    
    # Assert we have 2 releases by Test Artist 1
    assert len(results) == 2, f"Expected 2 releases, got {len(results)}"
    
    # Assert all are by Test Artist 1
    for row in results:
        assert row[1] == 'Test Artist 1'
    
    conn.close()
    print("✓ test_query_artist_discography PASSED")

# ============================================================================
# TEST 6: Query with keyword search
# ============================================================================
def test_query_keyword_search():
    """Test that we can search releases by title"""
    conn, cursor = setup_test_db()
    
    query = '''
        SELECT 
            r.title
        FROM RELEASES r
        WHERE r.title LIKE ?
    '''
    
    cursor.execute(query, ('%Test Release%',))
    results = cursor.fetchall()
    
    # Assert we have 3 results
    assert len(results) == 3, f"Expected 3 results, got {len(results)}"
    
    conn.close()
    print("✓ test_query_keyword_search PASSED")

# ============================================================================
# RUN ALL TESTS
# ============================================================================
if __name__ == '__main__':
    print("=" * 80)
    print("RUNNING UNIT TESTS FOR HARDWAX QUERIES")
    print("=" * 80)
    print()
    
    try:
        test_query_all_releases()
        test_query_by_label()
        test_query_by_format()
        test_query_release_with_tracks()
        test_query_artist_discography()
        test_query_keyword_search()
        
        print()
        print("=" * 80)
        print("✓ ALL TESTS PASSED!")
        print("=" * 80)
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")