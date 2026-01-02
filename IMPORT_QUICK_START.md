# Quick Start Guide - Import Pins Data

## 1️⃣ BASIC USAGE

### Test with 10 records first:
```bash
python manage.py import_pins_from_csv static/csv_files/data-1767244985089-PINS.csv --limit 10
```

### Full import without reverse geocoding:
```bash
python manage.py import_pins_from_csv static/csv_files/data-1767244985089-PINS.csv
```

### Full import WITH Nominatim reverse geocoding:
```bash
python manage.py import_pins_from_csv static/csv_files/data-1767244985089-PINS.csv --reverse-geocode
```

---

## 2️⃣ WHAT THE SCRIPT DOES

✅ Reads CSV file row by row
✅ Extracts: `placeName`, `category_name`, `location_geometry`, `country`, `state`, `city`
✅ Parses POINT(lon lat) geometry → creates Point(lon, lat, srid=4326)
✅ For each location entry:
   - Fuzzy matches country (75% threshold) or creates new
   - Fuzzy matches state in that country or creates new
   - Fuzzy matches city in that state or creates new
✅ Creates pin record in appropriate model (MainAttraction, Hotel, etc.)
✅ Generates unique slug: `{model_name}-{slug}-{random}`
✅ Logs every decision with full location hierarchy shown

---

## 3️⃣ CSV COLUMN MAPPING

```
CSV Column              → Django Field
─────────────────────────────────────
location_id            → (ignored, CSV only)
placeName              → name
category_name          → determines which model (Hotel, MainAttraction, etc)
rating                 → rating (0-5 decimal)
location_geometry      → pin (POINT geometry)
country, state, city   → determines Country/State/City FK
bestTimeToVisit        → (ignored, not in models)
cta, status            → (ignored)
```

---

## 4️⃣ EXAMPLE OUTPUT

```
Starting import of 10 records...
[1/10] ✓ CREATED: Morocco (Country Info)
  → Morocco > Morocco > Marrakech
[2/10] ✓ CREATED: Yellowstone (Places to Visit)
  → United States > Wyoming > Yellowstone
[3/10] ✓ CREATED: Eiffel Tower (Main Attraction)
  → France > Île-de-France > Paris
[4/10] ⊘ SKIPPED: BadPlace (BadCategory)
  → Unknown category: BadCategory
[5/10] ✓ CREATED: Venice (Destination Guide)
  → Italy > Veneto > Venice
... (more records) ...

============================================================
Import Complete!
Total: 10 | Created: 9 | Skipped: 1
```

---

## 5️⃣ WHAT GETS CREATED

### In Location Database:
- **Country**: Created if not found (fuzzy matched)
  - name: "Morocco", "France", "United States"
  - geometry: Point(0,0) [default, update manually later]
  
- **State**: Created if not found
  - country_id: FK to Country
  - name: "Île-de-France", "Wyoming", "Veneto"
  - geometry: Point(0,0) [default]
  
- **City**: Created if not found
  - state_id: FK to State  
  - name: "Paris", "Yellowstone", "Venice"
  - geometry: Point(0,0) [default]

### In Pins Database:
- **MainAttraction**, **Hotel**, **ThingsToDo**, etc.
  - name: placeName from CSV
  - city_id: FK to City
  - pin: Point geometry from location_geometry
  - rating: from CSV
  - slug: auto-generated
  - published: false (manual review before publishing)

---

## 6️⃣ FUZZY MATCHING DETAILS

**Threshold: 75%** - matches similar names

Examples:
```
CSV: "United States" 
DB: ["USA", "US", "United States"]
Match: "United States" ✓

CSV: "Île-de-France"
DB: ["Ile-de-France", "Ile de France"]  
Match: "Ile-de-France" ✓ (75% similar)

CSV: "RandomCity"
DB: ["Paris", "London", "Berlin"]
Match: NONE → Creates new City
```

---

## 7️⃣ REVERSE GEOCODING (Optional)

### Use when:
- CSV location data is incomplete
- Country/state/city columns are empty
- Want accurate location from coordinates

### How it works:
1. Extracts lat/lon from POINT(lon lat)
2. Calls: `https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&...`
3. Gets country/state/city from API response
4. Falls back to CSV data if API fails
5. **SLOW**: ~1 record/second (vs 100+/second without)

### Example:
```bash
python manage.py import_pins_from_csv data.csv --reverse-geocode

# For POINT(-6.037587745245016 31.996488743446648)
# API returns: Morocco, Marrakech-Safi, Marrakech
# These are used instead of CSV values if provided
```

---

## 8️⃣ COMMON ISSUES & FIXES

| Problem | Fix |
|---------|-----|
| `No module named 'requests'` | `pip install requests` |
| `Unknown category: X` | Check CATEGORY_MODEL_MAP in script or CSV data |
| `Could not determine country` | All countries empty and fuzzy match failed - check CSV |
| `Duplicate key value` | City already has that slug - check for duplicates |
| Import is slow | Use `--limit` flag to test small batch first |

---

## 9️⃣ VERIFICATION AFTER IMPORT

```python
# In Django shell
python manage.py shell

# Check counts
from location.models import Country, State, City
from pins.models import MainAttraction, Hotel

print(f"Countries: {Country.objects.count()}")
print(f"States: {State.objects.count()}")
print(f"Cities: {City.objects.count()}")
print(f"MainAttractions: {MainAttraction.objects.count()}")
print(f"Hotels: {Hotel.objects.count()}")

# Check a specific city
from location.models import City
paris = City.objects.get(name="Paris")
print(f"Paris has {paris.mainattraction_set.count()} main attractions")

# Check unpublished (should review before publishing)
unpub = MainAttraction.objects.filter(published=False).count()
print(f"Unpublished records: {unpub}")
```

---

## 🔟 NEXT STEPS

1. ✅ Run test import: `python manage.py import_pins_from_csv data.csv --limit 10`
2. ✅ Verify in Django admin
3. ✅ Check location accuracy (view on map if available)
4. ✅ Run full import: `python manage.py import_pins_from_csv data.csv`
5. ✅ Update geometry for countries/states if needed
6. ✅ Review and publish records
7. ✅ Monitor for duplicate entries

---

## SCRIPT FEATURES SUMMARY

| Feature | Details |
|---------|---------|
| **Model Mapping** | 13 categories → 13 Django models |
| **Geometry** | Parses WKT POINT, creates GIS Point objects |
| **Fuzzy Match** | 75% similarity threshold on country/state/city names |
| **Auto-Create** | Creates missing Country/State/City records |
| **Slug Generation** | Unique per city: `{model}-{slug}-{random}` |
| **Error Handling** | Graceful skip, detailed error messages |
| **Logging** | Full audit trail of all decisions |
| **Reverse Geocoding** | Optional Nominatim API integration |
| **Batch Limits** | Test with --limit flag |
| **Progress Display** | Shows record-by-record status |

---

**Created**: 2026-01-01
**Version**: 1.0
**Status**: Ready to use
