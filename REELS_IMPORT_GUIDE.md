# Reels Import Script Usage Guide

## Overview
This script imports reels from a CSV file and links them to existing pins in the database based on location geometry (POINT coordinates).

## CSV Format Expected
The script expects a CSV with these columns:
- `link`: YouTube/social media URL (required, unique)
- `platform`: Platform name (e.g., "youtube")
- `location_geometry`: POINT(longitude latitude) format
- `location_name`: Name of the location
- `reel_place_name`: Optional place name for the reel
- `category_name`: Category for preference matching
- `language`: Language of the content

## How It Works

1. **Point Extraction**: Extracts coordinates from `POINT(x y)` format
2. **Pin Matching**: Searches all pin models for matching locations using:
   - Exact coordinate match (0m tolerance)
   - Progressive distance search (10m, 50m, 200m, 1000m)
   - Both coordinate orders (lon,lat and lat,lon)
3. **Category Preference**: Prefers pins matching the CSV category_name
4. **Social Post Creation**: Creates SocialPost linked to the matched pin

## Usage

### Basic Import
```bash
python manage.py import_reels_from_csv
```

### With Custom CSV File
```bash
python manage.py import_reels_from_csv --csv-file path/to/your/file.csv
```

### Limit Records (for testing)
```bash
python manage.py import_reels_from_csv --limit 10
```

## Pin Model Mapping
The script searches these pin models in order:
- MainAttraction
- ThingsToDo  
- PlacesToVisit
- PlacesToEat
- Market
- CountryInfo
- DestinationGuide
- PlaceInformation
- TravelHacks
- Festivals
- FamousPhotoPoint
- Activities
- Hotel

## Category to Model Preference
- "Famous Photo Point" → FamousPhotoPoint
- "Destination Guide" → DestinationGuide  
- "Country Info" → CountryInfo
- "Main Attraction" → MainAttraction
- etc.

## Output
The script provides detailed feedback:
- ✓ Success: Shows linked pin details
- ⊘ Skipped: Shows reason (duplicate, no match, etc.)
- ✗ Error: Shows error details

## Example Output
```
[1/100] ✓ Linked to FamousPhotoPoint "Tiger Hill" (id=123)
[2/100] ⊘ Already exists
[3/100] ✗ Error: Invalid location_geometry
```

## Troubleshooting

### No Matching Pin Found
- Check if pins exist in database with similar coordinates
- Verify POINT format: `POINT(longitude latitude)`
- Consider coordinate order (script tries both)

### Django Import Errors
- Ensure virtual environment is activated
- Install required packages: `pip install django djangorestframework django-gis`
- Check database connection settings

### Performance
- Use `--limit` for testing with large files
- Script processes ~6500 records efficiently
- Database queries are optimized with distance annotations