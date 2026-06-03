# Database schema

## ARTISTS

- `artist_id` (PK)
- `artist_name`

## RELEASES

- `release_id` (PK)
- `artist_id` (FK)
- `title`
- `description`
- `catalog_number`
- `price`
- `image_url`
- `label_id` (FK)
- `format_id` (FK)

## LABELS

- `label_id` (PK)
- `label_name`

## FORMATS

- `format_id` (PK)
- `format_name`

## TRACKS

- `track_id` (PK)
- `release_id` (FK)
- `track_name`