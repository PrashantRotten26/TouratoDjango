# Import Script Technical Documentation

## Architecture Overview

The import system consists of 3 main components:

### 1. NominatimReverseGeocoder
Handles coordinate → address conversion
```python
lat, lon = -6.037, 31.996
data = NominatimReverseGeocoder.reverse_geocode(lat, lon)
# Returns: {'country': 'Morocco', 'state': 'Marrakech', 'city': 'Marrakech'}
```

### 2. LocationMatcher  
Handles fuzzy matching and location hierarchy creation
```python
country = LocationMatcher.get_or_create_country('Marocco')  # Typo OK, fuzzy matches
state = LocationMatcher.get_or_create_state(country, 'Marrakesh')
city = LocationMatcher.get_or_create_city(state, 'Marrakech')
```

### 3. Command
Main orchestrator that reads CSV and creates pin records

---

## Implementation Details

### WKT Geometry Parsing
```python
def extract_point_from_wkt(self, wkt_string):
    """
    Input:  'POINT(-6.037587745245016 31.996488743446648)'
    Pattern: r'POINT\(([-\d.]+)\s+([-\d.]+)\)'
    Output: (-6.037587745245016, 31.996488743446648)
    
    Note: (lon, lat) NOT (lat, lon) - important!
    """
```

### Fuzzy Matching Algorithm
Uses Python's `difflib.get_close_matches`:

```python
from difflib import get_close_matches

# Example
name = "Marocco"  # Typo
candidates = ["Morocco", "Maldives", "Mexico"]
matches = get_close_matches(name, candidates, n=1, cutoff=0.75)
# Returns: ["Morocco"] - 88% match is above 75% threshold
```

**Matching Process:**
1. Try exact case-insensitive match first: `Country.objects.get(name__iexact=name)`
2. If not found, fuzzy match against all names: `get_close_matches(..., cutoff=0.75)`
3. If still not found, create new record

### CSV Row Processing

```
Row from CSV
    ↓
Extract: placeName, category_name, location_geometry, 
         country, state, city, rating
    ↓
Parse POINT geometry → (lat, lon)
    ↓
[Optional] Reverse geocode if --reverse-geocode flag
    ↓
Match/Create Country, State, City hierarchy
    ↓
Create Pin object in appropriate model
    ↓
Model.save() triggers slug generation if new
    ↓
Log result with location hierarchy
```

### Slug Generation (Done by Model.save())

```python
# In each pin model's save() method:
if not self.pk:  # Only on creation
    base_slug = slugify(self.name)[:200]
    # slugify: "Eiffel Tower" → "eiffel-tower"
    
    random_suffix = uuid.uuid4().hex[:5]
    # Example: "a1b2c"
    
    self.slug = f"{model_name}-{base_slug}-{random_suffix}"
    # "mainattraction-eiffel-tower-a1b2c"
```

---

## Database Operations

### Location Creation Sequence
```
INSERT Country('Morocco', Point(0,0), active=True)
    ↓
INSERT State(country_id=1, 'Marrakech-Safi', active=True)
    ↓
INSERT City(state_id=1, 'Marrakech', Point(0,0), active=True)
    ↓
INSERT MainAttraction(
    name='Koutoubia Mosque',
    city_id=1,
    pin=Point(-6.037, 31.996),
    rating=4.8,
    slug='mainattraction-koutoubia-mosque-a1b2c',
    published=False
)
```

### Constraints Enforced
```
Country:
  - name: UNIQUE

State:
  - (country_id, name): UNIQUE per country
  - Can't have duplicate states in same country

City:
  - (state_id, name): UNIQUE per state
  - Can't have duplicate cities in same state

Pin Models:
  - (city_id, slug): UNIQUE per city
  - Can't have duplicate slugs in same city
```

---

## Error Handling Strategy

### By Severity

**SKIP & LOG (Recoverable)**
- Missing placeName → skip row
- Unknown category → skip row
- Invalid geometry format → skip row
- Missing country/state/city after all attempts → skip row

**CREATE ANYWAY (Non-critical)**
- No geometry: use Point(0,0)
- No rating: set to NULL
- Reverse geocode fails: use CSV values

**RAISE ERROR (Fatal)**
- CSV file not found
- Permission denied
- Database constraint violation

### Logging Levels
```
logger.warning() → Nominatim API failed, falling back to CSV
logger.info()    → Creating new Country/State/City
logger.error()   → Failed to create pin record
logger.exception() → Unexpected exception in row
```

---

## Performance Characteristics

### Without --reverse-geocode
- **Speed**: 100-200 records/second
- **Bottleneck**: Database inserts
- **Operations per record**: ~5-10 DB queries (fuzzy match + create)

### With --reverse-geocode
- **Speed**: ~1 record/second
- **Bottleneck**: HTTP requests to Nominatim API
- **Timeout**: 10 seconds per request
- **Recommendation**: Use `--limit 100` for testing

### Query Optimization
```python
# Each row performs:
1. Country.objects.get(name__iexact=...) - 1 query
2. State.objects.filter(country=...).values_list() - 1 query  
3. City.objects.filter(state=...).values_list() - 1 query
4. Model.objects.create(...) - 1 query
─────────────────────────────────────
= 4 queries per record (if no fuzzy match)

# With fuzzy match: +1 per level = 7 queries
# With reverse geocode: +1 HTTP request = slow
```

---

## Data Flow Diagrams

### Location Matching Flow
```
Input: country_name = "Marocco"

① Exact Match?
   Country.objects.get(name__iexact="Marocco")
   → NOT FOUND
   
② Fuzzy Match?
   get_close_matches("Marocco", ["Morocco", "Maldives", ...], cutoff=0.75)
   → FOUND "Morocco" (88% match)
   
③ Return existing Morocco
```

### Alternative Path (No Match)
```
Input: country_name = "RandomLand"

① Exact Match? NOT FOUND
② Fuzzy Match? NOT FOUND (too different)
③ Create new Country("RandomLand", Point(0,0))
   → Returns new record
```

### Coordinate Parsing
```
CSV: 'POINT(-6.037587745245016 31.996488743446648)'

Regex: r'POINT\(([-\d.]+)\s+([-\d.]+)\)'
Match: group(1) = '-6.037587745245016'  (longitude)
       group(2) = '31.996488743446648'   (latitude)

Result: lat=31.996, lon=-6.037
Create: Point(lon=-6.037, lat=31.996, srid=4326)
```

---

## Exception Handling

### Try-Catch Blocks

**Main Import Loop**
```python
for row in rows:
    try:
        result = self.import_row(row)
        # Success path
    except Exception as e:
        # Log full traceback
        logger.exception(f"Error importing row: {row}")
        # Skip to next row
```

**API Call**
```python
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return parsed_json
except Exception as e:
    logger.warning(f"Nominatim failed: {e}")
    return {'country': '', 'state': '', 'city': ''}
```

**Database Insert**
```python
try:
    pin_obj = model_class.objects.create(...)
    return {'success': True, ...}
except Exception as e:
    logger.error(f"Database error: {e}")
    return {'success': False, 'message': str(e)[:50]}
```

---

## Configuration & Customization

### To Add New Category

1. **Add Model** in `pins/models.py` (already done)
2. **Update CATEGORY_MODEL_MAP**:
```python
CATEGORY_MODEL_MAP = {
    # ... existing ...
    "New Category Name": NewCategoryModel,
}
```
3. **Re-run import** - script auto-detects new mapping

### To Change Fuzzy Match Threshold

In `LocationMatcher._fuzzy_match()`:
```python
# Current: 0.75 (75% match required)
matches = get_close_matches(name, candidates, n=1, cutoff=0.75)

# More lenient: 0.60
# Stricter: 0.85
```

### To Add More Coordinate Systems

```python
# Currently SRID 4326 (WGS 84)
pin_point = Point(lon, lat, srid=4326)

# For other SRID:
pin_point = Point(lon, lat, srid=3857)  # Web Mercator
```

---

## Testing Guide

### Test Case 1: Single Row
```python
# Shell
python manage.py shell
from pins.management.commands.import_pins_from_csv import LocationMatcher
from location.models import Country

country = LocationMatcher.get_or_create_country("Morocco")
print(country.name)  # Should print "Morocco"
```

### Test Case 2: Import 5 Records
```bash
python manage.py import_pins_from_csv data.csv --limit 5
```

### Test Case 3: Verify Results
```python
from location.models import Country, State, City
from pins.models import MainAttraction

print(f"Countries: {Country.objects.count()}")
print(f"Cities: {City.objects.count()}")
print(f"MainAttractions: {MainAttraction.objects.count()}")

# Check a specific record
ma = MainAttraction.objects.first()
print(f"Name: {ma.name}")
print(f"City: {ma.city.name}")
print(f"Slug: {ma.slug}")
print(f"Geometry: {ma.pin}")
```

### Test Case 4: Fuzzy Matching
```python
from difflib import get_close_matches

# Test your strings
result = get_close_matches("Marocco", ["Morocco", "Maldives"], n=1, cutoff=0.75)
print(result)  # Should print ['Morocco']
```

---

## Troubleshooting

### Script Not Found
```bash
# Wrong: python manage.py import_from_csv
# Right: python manage.py import_pins_from_csv
```

### Module Not Found
```bash
# Ensure __init__.py exists:
pins/management/__init__.py ✓
pins/management/commands/__init__.py ✓
```

### Import Errors
```
ImportError: No module named 'requests'
→ pip install requests

ImportError: No module named 'django.contrib.gis'
→ Install GeoDjango (PostgreSQL with PostGIS)
```

### Duplicate Key Error
```
IntegrityError: duplicate key value violates unique constraint
→ City already has another record with same slug
→ Check for duplicates: City.objects.filter(name="Paris").count()
```

---

## Appendix: Full Field Mapping

| CSV Column | Django Field | Model | Type | Required | Notes |
|------------|--------------|-------|------|----------|-------|
| location_id | - | - | - | No | Ignored |
| placeName | name | All | CharField | **Yes** | Required |
| category_name | - | All | String | **Yes** | Determines model |
| location_geometry | pin | All | PointField | **Yes** | POINT(lon lat) |
| rating | rating | All | Decimal | No | 0-5, default NULL |
| country | - | Location | String | No | Fuzzy matched |
| state | - | Location | String | No | Fuzzy matched |
| city | - | Location | String | No | Fuzzy matched |
| bestTimeToVisit | - | - | - | No | Not in model |
| cta | - | - | - | No | Not in model |
| status | - | - | - | No | Not in model |
| locationType | - | - | - | No | Not in model |

**Optional but available in models:**
- description
- header_image
- icon
- tags
- link
- published (default: False)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-01 | Initial release with all features |

---

**Last Updated**: 2026-01-01
**Compatibility**: Django 3.2+, PostGIS 3.0+
**Author**: Tourato Dev Team
