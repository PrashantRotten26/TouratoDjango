import csv
import re

def extract_point_from_wkt(wkt_string):
    """Extract coordinates from POINT(x y) format"""
    if not wkt_string:
        return None
    match = re.search(r'POINT\(([-\d.]+)\s+([-\d.]+)\)', wkt_string.strip())
    if match:
        try:
            return float(match.group(1)), float(match.group(2))
        except ValueError:
            return None
    return None

def test_csv_parsing():
    """Test CSV parsing and point extraction"""
    csv_file = 'static/csv_files/data-1767251193081_reels_with_point.csv'
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            print(f"Total rows: {len(rows)}")
            print("\nFirst 5 rows analysis:")
            
            for idx, row in enumerate(rows[:5], 1):
                link = row.get('link', '').strip()
                platform = row.get('platform', '').strip()
                location_geometry = row.get('location_geometry', '').strip()
                location_name = row.get('location_name', '').strip()
                category_name = row.get('category_name', '').strip()
                
                coords = extract_point_from_wkt(location_geometry)
                
                print(f"\nRow {idx}:")
                print(f"  Link: {link}")
                print(f"  Platform: {platform}")
                print(f"  Location: {location_name}")
                print(f"  Category: {category_name}")
                print(f"  Geometry: {location_geometry}")
                print(f"  Extracted coords: {coords}")
                
                if coords:
                    lon, lat = coords
                    print(f"  Point 1 (lon,lat): POINT({lon} {lat})")
                    print(f"  Point 2 (lat,lon): POINT({lat} {lon})")
                
    except FileNotFoundError:
        print(f"CSV file not found: {csv_file}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_csv_parsing()