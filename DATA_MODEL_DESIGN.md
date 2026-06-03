# Hardwax Online Data Engineering Assessment

## 1: Data Model Design

Design the relational database that can be used to populate the Hardwax releases module on the homepage.

### Database Schema

#### ARTISTS
- `artist_id` (PK, AUTOINCREMENT)
- `artist_name` (TEXT, UNIQUE, NOT NULL)

#### LABELS
- `label_id` (PK, AUTOINCREMENT)
- `label_name` (TEXT, UNIQUE, NOT NULL)

#### FORMATS
- `format_id` (PK, AUTOINCREMENT)
- `format_name` (TEXT, UNIQUE, NOT NULL)

#### RELEASES
- `release_id` (PK, AUTOINCREMENT)
- `artist_id` (FK → ARTISTS.artist_id)
- `title` (TEXT, NOT NULL)
- `description` (TEXT)
- `catalog_number` (TEXT)
- `price` (TEXT)
- `image_url` (TEXT)
- `label_id` (FK → LABELS.label_id)

#### RELEASE_FORMATS (Junction Table)
- `release_id` (FK → RELEASES.release_id, PK)
- `format_id` (FK → FORMATS.format_id, PK)
- **Purpose:** Links releases to multiple formats (e.g., vinyl + digital)

#### TRACKS
- `track_id` (PK, AUTOINCREMENT)
- `release_id` (FK → RELEASES.release_id)
- `track_name` (TEXT, NOT NULL)

### Relationships