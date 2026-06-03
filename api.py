from fastapi import FastAPI
from fastapi.responses import JSONResponse
import sqlite3

app = FastAPI(title="Hardwax API", description="API for Hardwax releases data")

def get_db_connection():
    conn = sqlite3.connect('hardwax.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def root():
    """API home page"""
    return {
        "name": "Hardwax API",
        "description": "API for accessing Hardwax releases data",
        "endpoints": {
            "GET /releases": "Get all releases",
            "GET /release/{release_id}": "Get specific release with tracks",
            "GET /artist/{artist_name}": "Get all releases by artist",
            "GET /label/{label_name}": "Get all releases from label",
            "GET /format/{format_name}": "Get all releases in format",
            "GET /search?q=query": "Search releases by description",
            "GET /stats": "Get database statistics"
        }
    }

@app.get("/releases")
def get_all_releases():
    """Get all releases"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT DISTINCT
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
        GROUP BY r.release_id
        ORDER BY r.release_id DESC
    '''
    
    cursor.execute(query)
    releases = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"count": len(releases), "releases": releases}

@app.get("/label/{label_name}")
def get_releases_by_label(label_name: str):
    """Get all releases from a specific label"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT 
            r.release_id,
            a.artist_name,
            r.title,
            r.price,
            GROUP_CONCAT(f.format_name, ', ') as formats
        FROM RELEASES r
        JOIN ARTISTS a ON r.artist_id = a.artist_id
        JOIN LABELS l ON r.label_id = l.label_id
        LEFT JOIN RELEASE_FORMATS rf ON r.release_id = rf.release_id
        LEFT JOIN FORMATS f ON rf.format_id = f.format_id
        WHERE l.label_name = ?
        GROUP BY r.release_id
        ORDER BY r.release_id DESC
    '''
    
    cursor.execute(query, (label_name,))
    releases = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"label": label_name, "count": len(releases), "releases": releases}

@app.get("/format/{format_name}")
def get_releases_by_format(format_name: str):
    """Get all releases in a specific format"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT 
            r.release_id,
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
    
    cursor.execute(query, (format_name,))
    releases = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"format": format_name, "count": len(releases), "releases": releases}

@app.get("/release/{release_id}")
def get_release_with_tracks(release_id: int):
    """Get full details of a release including all tracks"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    release_query = '''
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
    
    cursor.execute(release_query, (release_id,))
    release_row = cursor.fetchone()
    
    if not release_row:
        conn.close()
        return {"error": "Release not found"}, 404
    
    release = dict(release_row)
    
    tracks_query = '''
        SELECT track_name FROM TRACKS
        WHERE release_id = ?
        ORDER BY track_id
    '''
    
    cursor.execute(tracks_query, (release_id,))
    tracks = [row[0] for row in cursor.fetchall()]
    
    release["tracks"] = tracks
    conn.close()
    
    return release

@app.get("/artist/{artist_name}")
def get_artist_discography(artist_name: str):
    """Get all releases by a specific artist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT 
            r.release_id,
            r.title,
            l.label_name,
            r.price,
            GROUP_CONCAT(f.format_name, ', ') as formats
        FROM RELEASES r
        JOIN LABELS l ON r.label_id = l.label_id
        LEFT JOIN RELEASE_FORMATS rf ON r.release_id = rf.release_id
        LEFT JOIN FORMATS f ON rf.format_id = f.format_id
        JOIN ARTISTS a ON r.artist_id = a.artist_id
        WHERE a.artist_name = ?
        GROUP BY r.release_id
        ORDER BY r.release_id DESC
    '''
    
    cursor.execute(query, (artist_name,))
    releases = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"artist": artist_name, "count": len(releases), "releases": releases}

@app.get("/search")
def search_releases(q: str):
    """Search releases by description"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT 
            r.release_id,
            a.artist_name,
            r.title,
            l.label_name,
            r.price,
            GROUP_CONCAT(f.format_name, ', ') as formats
        FROM RELEASES r
        JOIN ARTISTS a ON r.artist_id = a.artist_id
        JOIN LABELS l ON r.label_id = l.label_id
        LEFT JOIN RELEASE_FORMATS rf ON r.release_id = rf.release_id
        LEFT JOIN FORMATS f ON rf.format_id = f.format_id
        WHERE r.description LIKE ?
        GROUP BY r.release_id
        ORDER BY r.release_id DESC
    '''
    
    cursor.execute(query, (f'%{q}%',))
    releases = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"search_term": q, "count": len(releases), "releases": releases}

@app.get("/stats")
def get_stats():
    """Get database statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM RELEASES')
    releases_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM ARTISTS')
    artists_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM LABELS')
    labels_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM FORMATS')
    formats_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM TRACKS')
    tracks_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "releases": releases_count,
        "artists": artists_count,
        "labels": labels_count,
        "formats": formats_count,
        "tracks": tracks_count
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
