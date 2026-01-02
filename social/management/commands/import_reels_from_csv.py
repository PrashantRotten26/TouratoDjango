import csv
import re
import logging
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Q

from social.models import PostPlatform, SocialPost
from pins.models import (
    MainAttraction, ThingsToDo, PlacesToVisit, PlacesToEat, Market,
    CountryInfo, DestinationGuide, PlaceInformation, TravelHacks,
    Festivals, FamousPhotoPoint, Activities, Hotel
)

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Import reels from CSV and link to pins based on location_geometry"

    def add_arguments(self, parser):
        parser.add_argument('--csv-file', type=str, default='static/csv_files/data-1767251193081_reels_with_point.csv')
        parser.add_argument('--limit', type=int, help='Limit number of records to process')

    def extract_point_from_wkt(self, wkt_string):
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

    def find_matching_pin(self, point, category_name=None):
        """Find matching pin in all pin models with progressive search radii"""
        pin_models = [
            MainAttraction, ThingsToDo, PlacesToVisit, PlacesToEat, Market,
            CountryInfo, DestinationGuide, PlaceInformation, TravelHacks,
            Festivals, FamousPhotoPoint, Activities, Hotel
        ]
        
        # Category to model mapping for preference
        category_model_map = {
            'Famous Photo Point': FamousPhotoPoint,
            'Destination Guide': DestinationGuide,
            'Country Info': CountryInfo,
            'Main Attraction': MainAttraction,
            'Things to Do': ThingsToDo,
            'Places to Visit': PlacesToVisit,
            'Places to Eat': PlacesToEat,
            'Market': Market,
            'Place Information': PlaceInformation,
            'Travel Hacks': TravelHacks,
            'Festivals': Festivals,
            'Activities': Activities,
            'Hotel': Hotel,
            'Hotels': Hotel,
        }
        
        # Try progressive search radii
        search_radii = [0, 10, 50, 200, 1000]  # meters
        
        for radius in search_radii:
            candidates = []
            
            for model in pin_models:
                try:
                    if radius == 0:
                        # Exact match
                        matches = model.objects.filter(pin__equals=point)
                    else:
                        # Distance-based search
                        matches = model.objects.filter(pin__distance_lte=(point, D(m=radius)))
                        try:
                            matches = matches.annotate(distance=Distance('pin', point)).order_by('distance')
                        except Exception:
                            pass
                    
                    for match in matches[:5]:  # Limit to 5 matches per model
                        distance = 0 if radius == 0 else radius
                        try:
                            if hasattr(match, 'distance'):
                                distance = float(match.distance.m)
                        except Exception:
                            pass
                        candidates.append((model, match, distance))
                        
                except Exception as e:
                    logger.debug(f"Error searching {model.__name__}: {e}")
                    continue
            
            if candidates:
                # Sort by distance
                candidates.sort(key=lambda x: x[2])
                
                # Prefer category match if available
                if category_name and category_name in category_model_map:
                    preferred_model = category_model_map[category_name]
                    for model, match, distance in candidates:
                        if model == preferred_model:
                            return model, match
                
                # Return closest match
                return candidates[0][0], candidates[0][1]
        
        return None, None

    def get_or_create_platform(self, platform_name):
        """Get or create platform"""
        if not platform_name:
            return None
        
        try:
            # Try exact match first
            platform = PostPlatform.objects.get(name__iexact=platform_name)
            return platform
        except PostPlatform.DoesNotExist:
            pass
        
        try:
            # Try by code
            platform = PostPlatform.objects.get(code__iexact=platform_name)
            return platform
        except PostPlatform.DoesNotExist:
            pass
        
        # Create new platform
        platform = PostPlatform.objects.create(
            name=platform_name.title(),
            code=platform_name[:10].lower()
        )
        return platform

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        limit = options.get('limit')
        
        created_count = 0
        skipped_count = 0
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                if limit:
                    rows = rows[:limit]
                
                for idx, row in enumerate(rows, 1):
                    try:
                        result = self.process_row(row)
                        if result['success']:
                            created_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(f"[{idx}/{len(rows)}] ✓ {result['message']}")
                            )
                        else:
                            skipped_count += 1
                            self.stdout.write(
                                self.style.WARNING(f"[{idx}/{len(rows)}] ⊘ {result['message']}")
                            )
                            
                    except Exception as e:
                        skipped_count += 1
                        logger.exception(f"Error processing row {idx}")
                        self.stdout.write(
                            self.style.ERROR(f"[{idx}/{len(rows)}] ✗ Error: {str(e)[:100]}")
                        )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Import complete. Created: {created_count}, Skipped: {skipped_count}"
                    )
                )
                
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"CSV file not found: {csv_file}"))

    def process_row(self, row):
        """Process a single CSV row"""
        link = row.get('link', '').strip()
        platform_name = row.get('platform', '').strip()
        location_geometry = row.get('location_geometry', '').strip()
        reel_place_name = row.get('reel_place_name', '').strip() or row.get('location_name', '').strip()
        language = row.get('language', '').strip()
        
        if not link:
            return {'success': False, 'link': 'N/A', 'message': 'Missing link'}
        
        # Skip if already exists
        if SocialPost.objects.filter(link=link).exists():
            return {'success': False, 'link': link, 'message': 'Already exists'}
        
        # Extract point coordinates
        coords = self.extract_point_from_wkt(location_geometry)
        if not coords:
            return {'success': False, 'link': link, 'message': 'Invalid location_geometry'}
        
        # Create point (try both coordinate orders)
        lon, lat = coords
        point1 = Point(lon, lat, srid=4326)
        point2 = Point(lat, lon, srid=4326)
        
        # Get category for preference matching
        category_name = row.get('category_name', '').strip()
        
        # Find matching pin
        model, pin_instance = self.find_matching_pin(point1, category_name)
        if not model:
            model, pin_instance = self.find_matching_pin(point2, category_name)
        
        if not model or not pin_instance:
            return {'success': False, 'link': link, 'message': 'No matching pin found'}
        
        # Get or create platform
        platform = self.get_or_create_platform(platform_name)
        
        # Create social post
        post = SocialPost(
            name=reel_place_name or f"Reel {link.split('/')[-1]}",
            platform=platform,
            link=link,
            language=language or None,
            published=False
        )
        
        # Link to the found pin
        model_name = model.__name__.lower()
        field_mapping = {
            'mainattraction': 'mainattraction',
            'thingstodo': 'thingsToDo',
            'placestovisit': 'placestovisit',
            'placestoeat': 'placesToEat',
            'market': 'market',
            'countryinfo': 'countryinfo',
            'destinationguide': 'DestinationGuide',
            'placeinformation': 'placeinformation',
            'travelhacks': 'travelhacks',
            'festivals': 'Festivals',
            'famousphotopoint': 'famousphotopoint',
            'activities': 'activites',
            'hotel': 'hotel'
        }
        
        field_name = field_mapping.get(model_name)
        if field_name and hasattr(post, field_name):
            setattr(post, field_name, pin_instance)
        
        # Set location info from pin
        if hasattr(pin_instance, 'city') and pin_instance.city:
            post.city = pin_instance.city
            post.state = pin_instance.city.state
            post.country = pin_instance.city.state.country
        
        try:
            post.save()
            return {
                'success': True, 
                'link': link, 
                'message': f'Linked to {model.__name__} "{pin_instance.name}" (id={pin_instance.pk})'
            }
        except Exception as e:
            logger.exception(f"Error saving post for link {link}")
            return {'success': False, 'link': link, 'message': f'Save error: {str(e)[:100]}'}