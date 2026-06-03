import sqlite3

conn = sqlite3.connect('hardwax.db')
cursor = conn.cursor()

print("=" * 80)
print("QUERY 1: ALL RELEASES")
print("=" * 80)

query1 = '''
    SELECT DISTINCT
        r.release_id,
        a.artist_name,
        r.title,
        r.description,
        l.label_name,
        r.catalog_number,
        r.price
    FROM RELEASES r
    JOIN ARTISTS a ON r.artist_id = a.artist_id
    JOIN LABELS l ON r.label_id = l.label_id
    ORDER BY r.release_id DESC
'''

cursor.execute(query1)
results = cursor.fetchall()
print(f"\nTotal releases: {len(results)}\n")
for row in results[:5]:
    print(f"{row[1]} - {row[2]}")
    print(f"  Label: {row[4]} | Price: {row[6]}")

print("\n" + "=" * 80)
print("QUERY 2: RELEASES BY LABEL")
print("=" * 80)

cursor.execute('SELECT label_id, label_name FROM LABELS LIMIT 1')
label_sample = cursor.fetchone()

if label_sample:
    label_id, label_name = label_sample
    
    query2 = '''
        SELECT 
            a.artist_name,
            r.title,
            r.price,
            GROUP_CONCAT(f.format_name, ', ') as formats
        FROM RELEASES r
        JOIN ARTISTS a ON r.artist_id = a.artist_id
        JOIN LABELS l ON r.label_id = l.label_id
        LEFT JOIN RELEASE_FORMATS rf ON r.release_id = rf.release_id
        LEFT JOIN FORMATS f ON rf.format_id = f.format_id
        WHERE r.label_id = ?
        GROUP BY r.release_id
        ORDER BY r.release_id DESC
    '''
    
    cursor.execute(query2, (label_id,))
    results = cursor.fetchall()
    print(f"\nReleases from label '{label_name}':\n")
    for row in results:
        print(f"{row[0]} - {row[1]} | {row[2]} | Formats: {row[3]}")

print("\n" + "=" * 80)
print("QUERY 3: RELEASES BY FORMAT")
print("=" * 80)

query3 = '''
    SELECT 
        COUNT(DISTINCT r.release_id) as count,
        f.format_name
    FROM RELEASE_FORMATS rf
    JOIN RELEASES r ON rf.release_id = r.release_id
    JOIN FORMATS f ON rf.format_id = f.format_id
    GROUP BY f.format_name
    ORDER BY count DESC
'''

cursor.execute(query3)
results = cursor.fetchall()
print("\nFormats available:\n")
for row in results:
    print(f"{row[1]}: {row[0]} releases")

print("\nExample - Get all 12\" releases:")
query3b = '''
    SELECT 
        a.artist_name,
        r.title,
        r.price
    FROM RELEASES r
    JOIN ARTISTS a ON r.artist_id = a.artist_id
    JOIN RELEASE_FORMATS rf ON r.release_id = rf.release_id
    JOIN FORMATS f ON rf.format_id = f.format_id
    WHERE f.format_name = ?
    ORDER BY r.release_id DESC
'''

cursor.execute(query3b, ('12"',))
results = cursor.fetchall()
print(f"Found {len(results)} releases\n")
for row in results[:5]:
    print(f"{row[0]} - {row[1]} ({row[2]})")

print("\n" + "=" * 80)
print("QUERY 4: FULL RELEASE DETAILS WITH TRACKS")
print("=" * 80)

query4_release = '''
    SELECT 
        r.release_id,
        a.artist_name,
        r.title,
        r.description,
        l.label_name,
        r.catalog_number,
        r.price,
        GROUP_CONCAT(f.format_name, ', ') as formats
    FROM RELEASES r
    JOIN ARTISTS a ON r.artist_id = a.artist_id
    JOIN LABELS l ON r.label_id = l.label_id
    LEFT JOIN RELEASE_FORMATS rf ON r.release_id = rf.release_id
    LEFT JOIN FORMATS f ON rf.format_id = f.format_id
    WHERE r.release_id = ?
    GROUP BY r.release_id
'''

query4_tracks = '''
    SELECT track_name FROM TRACKS
    WHERE release_id = ?
    ORDER BY track_id
'''

cursor.execute('SELECT release_id FROM RELEASES LIMIT 1')
release_sample = cursor.fetchone()

if release_sample:
    release_id = release_sample[0]
    cursor.execute(query4_release, (release_id,))
    release = cursor.fetchone()
    
    if release:
        print(f"\nRelease: {release[1]} - {release[2]}")
        print(f"Description: {release[3]}")
        print(f"Label: {release[4]} | Catalog: {release[5]}")
        print(f"Formats: {release[7]} | Price: {release[6]}")
        print("\nTracks:")
        
        cursor.execute(query4_tracks, (release_id,))
        tracks = cursor.fetchall()
        for i, track in enumerate(tracks, 1):
            print(f"  {i}. {track[0]}")

print("\n" + "=" * 80)
print("QUERY 5: ARTIST DISCOGRAPHY")
print("=" * 80)

query5 = '''
    SELECT 
        r.release_id,
        r.title,
        l.label_name,
        GROUP_CONCAT(f.format_name, ', ') as formats,
        r.price
    FROM RELEASES r
    JOIN LABELS l ON r.label_id = l.label_id
    LEFT JOIN RELEASE_FORMATS rf ON r.release_id = rf.release_id
    LEFT JOIN FORMATS f ON rf.format_id = f.format_id
    WHERE r.artist_id = ?
    GROUP BY r.release_id
    ORDER BY r.release_id DESC
'''

cursor.execute('SELECT artist_id, artist_name FROM ARTISTS LIMIT 1')
artist = cursor.fetchone()

if artist:
    print(f"\nReleases by {artist[1]}:\n")
    cursor.execute(query5, (artist[0],))
    releases = cursor.fetchall()
    for row in releases:
        print(f"{row[1]} ({row[3]}) - {row[2]} | {row[4]}")

print("\n" + "=" * 80)
print("QUERY 6: SEARCH RELEASES BY DESCRIPTION")
print("=" * 80)

query6 = '''
    SELECT 
        a.artist_name,
        r.title,
        l.label_name,
        GROUP_CONCAT(f.format_name, ', ') as formats,
        r.price
    FROM RELEASES r
    JOIN ARTISTS a ON r.artist_id = a.artist_id
    JOIN LABELS l ON r.label_id = l.label_id
    LEFT JOIN RELEASE_FORMATS rf ON r.release_id = rf.release_id
    LEFT JOIN FORMATS f ON rf.format_id = f.format_id
    WHERE r.description LIKE ?
    GROUP BY r.release_id
    ORDER BY r.release_id DESC
'''

search_term = '%Dub%'
cursor.execute(query6, (search_term,))
results = cursor.fetchall()
print(f"\nSearching for releases with 'Dub' in description:")
print(f"Found {len(results)} releases\n")
for row in results[:5]:
    print(f"{row[0]} - {row[1]} | {row[2]} | Formats: {row[3]}")

conn.close()

print("\n" + "=" * 80)
print("All queries executed successfully!")
print("=" * 80)
