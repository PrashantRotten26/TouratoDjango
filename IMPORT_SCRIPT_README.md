# CSV Import Script for Pins Data

This Django management command imports tourist attraction data from CSV files into the Tourato database.

## Features

- ✅ **Smart Location Matching**: Fuzzy matches country, state, and city names
- ✅ **Auto-Create Locations**: Creates new Country/State/City records if they don't exist
- ✅ **Nominatim Integration**: Optional reverse geocoding from coordinates
- ✅ **Multiple Categories**: Supports all 13 pin categories (MainAttraction, ThingsToDo, Hotel, etc.)
- ✅ **WKT Geometry**: Parses POINT(lon lat) format from CSV
- ✅ **Slug Generation**: Auto-generates unique slugs with random suffixes
- ✅ **Detailed Logging**: Shows progress and explains all decisions

## CSV Format

Expected columns:
```
location_id
placeName          → name of the attraction
locationType
rating             → decimal rating (0-5)
bestTimeToVisit
country            → country name
state              → state/province name
city               → city name
cta
status
location_geometry  → POINT(lon lat) WKT format
category_name      → Category (see mapping below)
```

## Category Mapping

```
"Main Attraction"          → MainAttraction
"Things to Do"             → ThingsToDo
"Places to Visit"          → PlacesToVisit
"Places to Eat"            → PlacesToEat
"Market"                   → Market
"Country Info"             → CountryInfo
"Destination Guide"        → DestinationGuide
"Place Information"        → PlaceInformation
"Travel Hacks"             → TravelHacks
"Festivals"                → Festivals
"Famous Photo Point"       → FamousPhotoPoint
"Activities"               → Activities
"Hotel"                    → Hotel
```

## Usage

### Basic Import (use CSV locations)
```bash
python manage.py import_pins_from_csv static/csv_files/data-1767244985089-PINS.csv
```

### With Reverse Geocoding
If CSV location data is incomplete/inaccurate, use Nominatim API to determine location from coordinates:

```bash
python manage.py import_pins_from_csv static/csv_files/data-1767244985089-PINS.csv --reverse-geocode
```

**Note**: Reverse geocoding uses the free Nominatim API. It's slow but accurate. Each request takes ~1-2 seconds.

### Import First 100 Records (Testing)
```bash
python manage.py import_pins_from_csv static/csv_files/data-1767244985089-PINS.csv --limit 100
```

### Combined Options
```bash
python manage.py import_pins_from_csv static/csv_files/data-1767244985089-PINS.csv --reverse-geocode --limit 50
```

## How It Works

### Location Hierarchy Process
1. **Country**: Fuzzy matches against existing countries (threshold 75%)
   - If no match found, creates new Country with default Point(0,0) geometry
2. **State**: Fuzzy matches against states in that country
   - If no match found, creates new State with default geometry
3. **City**: Fuzzy matches against cities in that state
   - If no match found, creates new City with default geometry

### Coordinate Parsing
- Extracts (lon, lat) from `POINT(lon lat)` WKT format
- Creates Point object with SRID 4326 (WGS 84)
- Example: `POINT(-6.037587745245016 31.996488743446648)` → Point(-6.037587745245016, 31.996488743446648)

### Slug Generation
Automatic on first save (only when pk is None):
```python
slug = f"{model_table_name}-{base_slug}-{random_suffix}"
# Example: "mainattraction-eiffel-tower-a1b2c"
```

### Reverse Geocoding (Optional)
If `--reverse-geocode` flag is set:
1. Calls Nominatim API: `https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1`
2. Extracts country, state, city from response
3. Falls back to CSV values if API fails or returns empty
4. Uses extracted location if available, CSV otherwise

## Output Example

```
Starting import of 100 records...
[1/100] ✓ CREATED: Morocco (Country Info)
  → Morocco > Morocco > Marrakech
[2/100] ✓ CREATED: Georgia (Country Info)
  → Georgia > Georgia > Tbilisi
[3/100] ✓ CREATED: Yellowstone National Park (Places to Visit)
  → United States > Wyoming > Yellowstone
[4/100] ⊘ SKIPPED: Invalid Record (Unknown)
  → Unknown category: BadCategory

============================================================
Import Complete!
Total: 100 | Created: 98 | Skipped: 2
```

## Error Handling

### Common Issues & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `Missing placeName` | Empty name column | Check CSV data |
| `Unknown category: X` | Category not in mapping | Add category to CATEGORY_MODEL_MAP or check CSV |
| `Invalid location_geometry format` | Bad WKT string | Ensure POINT(lon lat) format |
| `Could not determine country` | All matching failed | Manual entry required or check CSV |
| `Error creating record: ...` | Database constraint violation | Check unique constraints, may be duplicate |

## Logging

All decisions are logged to Django's logger under `pins.management.commands.import_pins_from_csv`:

```python
# In settings.py, enable detailed logging:
LOGGING = {
    'version': 1,
    'loggers': {
        'pins.management.commands.import_pins_from_csv': {
            'level': 'DEBUG',
        }
    }
}
```

## Performance Notes

- **Without --reverse-geocode**: ~100-200 records/second
- **With --reverse-geocode**: ~1 record/second (due to API calls)
- Use `--limit 10` for testing before full import
- For large imports with reverse geocoding, consider using `--limit` and running in batches

## Dependencies

Requires:
- `requests` library (for Nominatim API)
- Django GIS (GeoDjango)

Install if needed:
```bash
pip install requests
```

## Next Steps

After import, consider:
1. ✅ Verify imported records: `Country.objects.count()`, `City.objects.count()`
2. ✅ Check for duplicates in same city: `MainAttraction.objects.filter(city=city).count()`
3. ✅ Add geometry data to countries/states (currently default Point(0,0))
4. ✅ Review unpublished records (`published=False` by default)
5. ✅ Verify accurate location matching in admin interface
