import csv
import re
import logging
from decimal import Decimal
from difflib import get_close_matches
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point, Polygon, MultiPolygon
from django.db.models import Q
from django.contrib.gis.measure import D
import requests

from pins.models import (
    MainAttraction, ThingsToDo, PlacesToVisit, PlacesToEat, Market,
    CountryInfo, DestinationGuide, PlaceInformation, TravelHacks,
    Festivals, FamousPhotoPoint, Activities, Hotel, HotelCategory
)
from location.models import Country, State, City
from account.models import UserProfile


logger = logging.getLogger(__name__)

# Distance tolerance (meters) to consider points as duplicates
DISTANCE_TOLERANCE_METERS = 10


# Mapping of CSV category_name to Django model
CATEGORY_MODEL_MAP = {
    "Main Attraction": MainAttraction,
    "Things to Do": ThingsToDo,
    "Places to Visit": PlacesToVisit,
    "Places to Eat": PlacesToEat,
    "Market": Market,
    "Country Info": CountryInfo,
    "Destination Guide": DestinationGuide,
    "Place Information": PlaceInformation,
    "Travel Hacks": TravelHacks,
    "Festivals": Festivals,
    "Famous Photo Point": FamousPhotoPoint,
    "Activities": Activities,
    "Hotel": Hotel,
    "Hotels": Hotel,
}


class NominatimReverseGeocoder:
    """Handle reverse geocoding via Nominatim API."""
    
    BASE_URL = "https://nominatim.openstreetmap.org/reverse"
    
    @staticmethod
    def reverse_geocode(lat, lon):
        """
        Reverse geocode coordinates to get country, state, city.
        Returns dict with 'country', 'state', 'city' keys.
        """
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json',
                'zoom': 10,
                'addressdetails': 1
            }
            headers = {'User-Agent': 'TouratoDjango/1.0'}
            
            response = requests.get(
                NominatimReverseGeocoder.BASE_URL,
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            address = data.get('address', {})

            # Prefer explicit 'state', but some responses use 'province' or 'region'
            state = (
                address.get('state') or
                address.get('province') or
                address.get('region') or
                ''
            )

            # City fallback order: city -> town -> village -> region
            city = (
                address.get('city') or
                address.get('town') or
                address.get('village') or
                address.get('region') or
                ''
            )

            return {
                'country': address.get('country', ''),
                'state': state,
                'city': city,
            }
        except Exception as e:
            logger.warning(f"Nominatim reverse geocoding failed for ({lat}, {lon}): {e}")
            return {'country': '', 'state': '', 'city': ''}


class LocationMatcher:
    """Handle fuzzy matching and creation of Country, State, City."""
    
    @staticmethod
    def _fuzzy_match(name, candidates, threshold=0.6):
        """
        Fuzzy match a name against candidates.
        Returns the best match if similarity is above threshold.
        """
        if not name or not candidates:
            return None
        
        matches = get_close_matches(name.strip(), candidates, n=1, cutoff=threshold)
        return matches[0] if matches else None
    
    @staticmethod
    def get_or_create_country(country_name, geometry=None):
        """
        Get or create a country by fuzzy matching.
        If not found, create with provided geometry.
        """
        if not country_name or country_name.strip() == '':
            return None
        
        country_name = country_name.strip()
        
        # Try exact match first
        try:
            return Country.objects.get(name__iexact=country_name)
        except Country.DoesNotExist:
            pass
        
        # Try fuzzy match
        all_countries = list(Country.objects.values_list('name', flat=True))
        matched = LocationMatcher._fuzzy_match(country_name, all_countries, threshold=0.75)
        
        if matched:
            return Country.objects.get(name=matched)
        
        # Create new country
        logger.info(f"Creating new country: {country_name}")
        return Country.objects.create(
            name=country_name,
            geometry=geometry or Point(0, 0)  # Default point if no geometry provided
        )
    
    @staticmethod
    def get_or_create_state(country, state_name, geometry=None):
        """
        Get or create a state for a country by fuzzy matching.
        """
        if not state_name or state_name.strip() == '':
            return None
        
        state_name = state_name.strip()
        
        # Try exact match first
        try:
            return State.objects.get(
                country=country,
                name__iexact=state_name
            )
        except State.DoesNotExist:
            pass
        
        # Try fuzzy match within this country
        all_states = list(
            State.objects.filter(country=country).values_list('name', flat=True)
        )
        matched = LocationMatcher._fuzzy_match(state_name, all_states, threshold=0.75)
        
        if matched:
            return State.objects.get(country=country, name=matched)
        
        # Create new state (no geometry): link by name to country only
        logger.info(f"Creating new state (no geometry): {state_name} in {country.name}")
        return State.objects.create(
            country=country,
            name=state_name
        )
    
    @staticmethod
    def get_or_create_city(state, city_name, geometry=None):
        """
        Get or create a city for a state by fuzzy matching.
        """
        if not city_name or city_name.strip() == '':
            return None
        
        city_name = city_name.strip()
        
        # Try exact match first
        try:
            return City.objects.get(
                state=state,
                name__iexact=city_name
            )
        except City.DoesNotExist:
            pass
        
        # Try fuzzy match within this state
        all_cities = list(
            City.objects.filter(state=state).values_list('name', flat=True)
        )
        matched = LocationMatcher._fuzzy_match(city_name, all_cities, threshold=0.75)
        
        if matched:
            return City.objects.get(state=state, name=matched)
        
        # Create new city (no geometry): link by name to state only
        logger.info(f"Creating new city (no geometry): {city_name} in {state.name}")
        return City.objects.create(
            state=state,
            name=city_name
        )


class Command(BaseCommand):
    help = "Import pins data from CSV file with geolocation and location hierarchy"
    
    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to CSV file'
        )
        parser.add_argument(
            '--reverse-geocode',
            action='store_true',
            help='Use Nominatim API to reverse geocode coordinates'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of records to import'
        )
    
    def extract_point_from_wkt(self, wkt_string):
        """
        Extract lat, lon from POINT(lon lat) WKT format.
        Returns (lat, lon) tuple or None.
        """
        if not wkt_string:
            return None
        
        match = re.search(r'POINT\(([-\d.]+)\s+([-\d.]+)\)', wkt_string)
        if match:
            try:
                lon = float(match.group(1))
                lat = float(match.group(2))
                return lat, lon
            except (ValueError, AttributeError):
                return None
        return None
    
    def handle(self, *args, **options):
        csv_file = options['csv_file']
        use_reverse_geocode = options.get('reverse_geocode', False)
        limit = options.get('limit')
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                if limit:
                    rows = rows[:limit]
                
                total = len(rows)
                created = 0
                skipped = 0
                
                self.stdout.write(
                    self.style.SUCCESS(f"Starting import of {total} records...")
                )
                
                for idx, row in enumerate(rows, 1):
                    try:
                        result = self.import_row(
                            row,
                            use_reverse_geocode=use_reverse_geocode
                        )
                        
                        if result['success']:
                            created += 1
                            status = "✓ CREATED"
                        else:
                            skipped += 1
                            status = "⊘ SKIPPED"
                        
                        self.stdout.write(
                            f"[{idx}/{total}] {status}: {result['name']} "
                            f"({result['category']})"
                        )
                        
                        if result.get('message'):
                            self.stdout.write(
                                self.style.WARNING(f"  → {result['message']}")
                            )
                    
                    except Exception as e:
                        skipped += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f"[{idx}/{total}] ✗ ERROR: {str(e)[:80]}"
                            )
                        )
                        logger.exception(f"Error importing row {idx}: {row}")
                
                # Summary
                self.stdout.write(self.style.SUCCESS("\n" + "="*60))
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Import Complete!\n"
                        f"Total: {total} | Created: {created} | Skipped: {skipped}"
                    )
                )
        
        except FileNotFoundError:
            raise CommandError(f"CSV file not found: {csv_file}")
        except Exception as e:
            raise CommandError(f"Import failed: {str(e)}")
    
    def import_row(self, row, use_reverse_geocode=False):
        """
        Import a single row from CSV.
        Returns dict with import result.
        """
        # Extract basic info
        place_name = row.get('placeName', '').strip()
        category_name = row.get('category_name', '').strip()
        rating_str = row.get('rating', '0')
        location_geometry = row.get('location_geometry', '').strip()
        
        if not place_name:
            return {
                'success': False,
                'name': 'N/A',
                'category': category_name,
                'message': 'Missing placeName'
            }
        
        # Get category model
        model_class = CATEGORY_MODEL_MAP.get(category_name)
        if not model_class:
            return {
                'success': False,
                'name': place_name,
                'category': category_name,
                'message': f'Unknown category: {category_name}'
            }
        
        # Extract coordinates
        coords = self.extract_point_from_wkt(location_geometry)
        if not coords:
            return {
                'success': False,
                'name': place_name,
                'category': category_name,
                'message': 'Invalid location_geometry format'
            }
        
        lat, lon = coords
        
        # Get location info from CSV or reverse geocode
        csv_country = row.get('country', '').strip()
        csv_state = row.get('state', '').strip()
        csv_city = row.get('city', '').strip()
        
        if use_reverse_geocode:
            geocoded = NominatimReverseGeocoder.reverse_geocode(lat, lon)
            country_name = geocoded.get('country') or csv_country
            state_name = geocoded.get('state') or csv_state
            city_name = geocoded.get('city') or csv_city
        else:
            country_name = csv_country
            state_name = csv_state
            city_name = csv_city
        
        # Get or create location hierarchy
        # Prepare a Point for geometry-based defaults
        pin_point = Point(lon, lat, srid=4326)

        country = LocationMatcher.get_or_create_country(country_name, geometry=pin_point)
        if not country:
            return {
                'success': False,
                'name': place_name,
                'category': category_name,
                'message': 'Could not determine country'
            }

        # If CSV/reverse-geocode didn't provide a state, use a fallback name
        # (use country name) so we can still associate a State and proceed.
        if not state_name or state_name.strip() == '':
            state_name = country.name

        state = LocationMatcher.get_or_create_state(country, state_name, geometry=pin_point)
        if not state:
            try:
                # Create a placeholder state to avoid skipping the record
                logger.info(f"Creating placeholder state '{state_name}' for country {country.name}")
                state = State.objects.create(country=country, name=state_name)
            except Exception:
                return {
                    'success': False,
                    'name': place_name,
                    'category': category_name,
                    'message': f'Could not determine state for {country.name}'
                }

        # If CSV/reverse-geocode didn't provide a city, fall back to the state name
        if not city_name or city_name.strip() == '':
            city_name = state.name

        city = LocationMatcher.get_or_create_city(state, city_name, geometry=pin_point)
        if not city:
            try:
                # Create a placeholder city to avoid skipping the record
                logger.info(f"Creating placeholder city '{city_name}' for state {state.name}")
                city = City.objects.create(state=state, name=city_name)
            except Exception:
                return {
                    'success': False,
                    'name': place_name,
                    'category': category_name,
                    'message': f'Could not determine city for {state.name}'
                }
        
        # Create the pin record
        try:
            pin_point = Point(lon, lat, srid=4326)
            
            # Convert rating
            try:
                rating = Decimal(rating_str) if rating_str else None
            except:
                rating = None
            
            # Duplicate check: same model within city (within tolerance)
            try:
                same_exists = model_class.objects.filter(
                    city=city,
                    pin__distance_lte=(pin_point, D(m=DISTANCE_TOLERANCE_METERS))
                ).exists()
            except Exception:
                same_exists = False

            if same_exists:
                return {
                    'success': False,
                    'name': place_name,
                    'category': category_name,
                    'message': f'Duplicate point exists in {model_class.__name__} (within {DISTANCE_TOLERANCE_METERS}m)'
                }

            # Cross-model duplicate check: avoid creating the same point in other pin tables
            try:
                for other_model in set(CATEGORY_MODEL_MAP.values()):
                    if other_model is model_class:
                        continue
                    try:
                        if other_model.objects.filter(
                            city=city,
                            pin__distance_lte=(pin_point, D(m=DISTANCE_TOLERANCE_METERS))
                        ).exists():
                            return {
                                'success': False,
                                'name': place_name,
                                'category': category_name,
                                'message': f'Duplicate point exists in {other_model.__name__} (within {DISTANCE_TOLERANCE_METERS}m)'
                            }
                    except Exception:
                        # If other_model doesn't have a pin field or query fails, skip
                        continue
            except Exception:
                # If something unexpected happens, proceed to create (we'll handle DB errors below)
                pass

            # Create object
            pin_obj = model_class.objects.create(
                name=place_name,
                city=city,
                pin=pin_point,
                rating=rating,
                published=False
            )
            
            return {
                'success': True,
                'name': place_name,
                'category': category_name,
                'message': f'{country.name} > {state.name} > {city.name}'
            }
        
        except Exception as e:
            logger.error(f"Error creating {model_class.__name__} for {place_name}: {e}")
            return {
                'success': False,
                'name': place_name,
                'category': category_name,
                'message': f'Error creating record: {str(e)[:50]}'
            }
