import sqlite3
import requests
from bs4 import BeautifulSoup
import re

print("Fetching Hardwax homepage...")
url = 'https://www.hardwax.com'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"Error fetching page: {e}")
    exit(1)

print(f"Status: {response.status_code}\n")

soup = BeautifulSoup(response.content, 'html.parser')

conn = sqlite3.connect('hardwax.db')
cursor = conn.cursor()

print("Clearing old data...")
cursor.execute('DELETE FROM TRACKS')
cursor.execute('DELETE FROM RELEASE_FORMATS')
cursor.execute('DELETE FROM RELEASES')
cursor.execute('DELETE FROM ARTISTS')
cursor.execute('DELETE FROM LABELS')
cursor.execute('DELETE FROM FORMATS')
conn.commit()

release_links = soup.find_all('a', href=re.compile(r'/\d+/'))
print(f"Found {len(release_links)} release links\n")

release_count = 0
processed_releases = set()

for link in release_links:
    container = link
    found_container = False
    
    for _ in range(10):
        container = container.find_parent()
        if container:
            text_content = container.get_text()
            if '€' in text_content and ('Label' in text_content or 'label' in text_content):
                found_container = True
                break
    
    if not found_container:
        continue
    
    h2 = container.find('h2')
    if not h2:
        continue
    
    h2_text = h2.get_text(strip=True)
    
    if ':' in h2_text:
        artist_name, title = h2_text.split(':', 1)
        artist_name = artist_name.strip()
        title = title.strip()
    else:
        artist_name = h2_text
        title = ""
    
    if not artist_name or not title:
        continue
    
    description = ""
    p = container.find('p')
    if p:
        description = p.get_text(strip=True)
    
    label_name = ""
    catalog_number = ""
    
    label_link = container.find('a', href=re.compile(r'/label/'))
    if label_link:
        label_name = label_link.get_text(strip=True)
        all_links = container.find_all('a')
        label_index = all_links.index(label_link) if label_link in all_links else -1
        
        if label_index >= 0 and label_index + 1 < len(all_links):
            next_link = all_links[label_index + 1]
            catalog_number = next_link.get_text(strip=True)
    
    formats_found = []
    all_text = container.get_text()
    
    format_keywords = ["12\"", "Do LP", "LP", "10\"", "7\"", "3x LP", "Do 12\"", "Do CD", "MP3", "AIFF", "Tape", "EP"]
    for keyword in format_keywords:
        if keyword in all_text:
            formats_found.append(keyword)
    
    price = ""
    price_match = re.search(r'€\s*[\d.]+', all_text)
    if price_match:
        price = price_match.group(0)
    
    release_key = f"{artist_name}|{title}|{label_name}"
    if release_key in processed_releases:
        continue
    processed_releases.add(release_key)
    
    tracks = []
    all_uls = container.find_all('ul')
    
    for ul in all_uls:
        has_audio_links = ul.find('a', href=re.compile(r'\.mp3|\.aiff|audio'))
        
        if has_audio_links:
            for li in ul.find_all('li'):
                track_link = li.find('a')
                if track_link:
                    track_text = track_link.get_text(separator=' ', strip=True)
                    track_name = ' '.join(track_text.split())
                    
                    if track_name and len(track_name) > 1:
                        tracks.append(track_name)
            break
    
    print(f"Release {release_count + 1}:")
    print(f"  Artist: {artist_name}")
    print(f"  Title: {title}")
    print(f"  Label: {label_name}")
    print(f"  Formats: {', '.join(formats_found)}")
    print(f"  Tracks: {len(tracks)}")
    print()
    
    try:
        cursor.execute('SELECT artist_id FROM ARTISTS WHERE artist_name = ?', (artist_name,))
        artist = cursor.fetchone()
        if artist:
            artist_id = artist[0]
        else:
            cursor.execute('INSERT INTO ARTISTS (artist_name) VALUES (?)', (artist_name,))
            artist_id = cursor.lastrowid
        
        if label_name:
            cursor.execute('SELECT label_id FROM LABELS WHERE label_name = ?', (label_name,))
            label = cursor.fetchone()
            if label:
                label_id = label[0]
            else:
                cursor.execute('INSERT INTO LABELS (label_name) VALUES (?)', (label_name,))
                label_id = cursor.lastrowid
        else:
            label_id = 1
        
        format_ids = []
        for fmt_name in formats_found:
            cursor.execute('SELECT format_id FROM FORMATS WHERE format_name = ?', (fmt_name,))
            fmt = cursor.fetchone()
            if fmt:
                format_ids.append(fmt[0])
            else:
                cursor.execute('INSERT INTO FORMATS (format_name) VALUES (?)', (fmt_name,))
                format_ids.append(cursor.lastrowid)
        
        if not format_ids:
            continue
        
        cursor.execute('''
            INSERT INTO RELEASES 
            (artist_id, title, description, catalog_number, price, label_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (artist_id, title, description, catalog_number, price, label_id))
        
        release_id = cursor.lastrowid
        
        for format_id in format_ids:
            cursor.execute('''
                INSERT INTO RELEASE_FORMATS (release_id, format_id)
                VALUES (?, ?)
            ''', (release_id, format_id))
        
        for track_name in tracks:
            cursor.execute('''
                INSERT INTO TRACKS (release_id, track_name)
                VALUES (?, ?)
            ''', (release_id, track_name))
        
        release_count += 1
        
    except Exception as e:
        print(f"  Error: {e}\n")
        continue

conn.commit()
conn.close()

print(f"\n✓ Successfully populated {release_count} releases")
