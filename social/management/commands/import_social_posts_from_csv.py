import csv
import re
import math
import logging
from decimal import Decimal
from difflib import get_close_matches
from django.core.management.base import BaseCommand, CommandError
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

# Tolerance for point matching (meters)
DISTANCE_TOLERANCE_METERS = 10

# Map CSV category_name -> (ModelClass, SocialPost field name)
CATEGORY_TO_MODEL_FIELD = {
    "Main Attraction": (MainAttraction, 'mainattraction'),
    "Things to Do": (ThingsToDo, 'thingsToDo'),
    "Places to Visit": (PlacesToVisit, 'placestovisit'),
    "Places to Eat": (PlacesToEat, 'placesToEat'),
    "Market": (Market, 'market'),
    "Country Info": (CountryInfo, 'countryinfo'),
    "Destination Guide": (DestinationGuide, 'DestinationGuide'),
    "Place Information": (PlaceInformation, 'placeinformation'),
    "Travel Hacks": (TravelHacks, 'travelhacks'),
    "Festivals": (Festivals, 'Festivals'),
    "Famous Photo Point": (FamousPhotoPoint, 'famousphotopoint'),
    "Activities": (Activities, 'activites'),
    "Hotel": (Hotel, 'hotel'),
    "Hotels": (Hotel, 'hotel'),
}

ALL_PIN_MODELS = [
    MainAttraction, ThingsToDo, PlacesToVisit, PlacesToEat, Market,
    CountryInfo, DestinationGuide, PlaceInformation, TravelHacks,
    Festivals, FamousPhotoPoint, Activities, Hotel
]

class Command(BaseCommand):
    help = "Import social posts from CSV and link to nearest pin/location"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')
        parser.add_argument('--limit', type=int, default=None, help='Limit number of records')
        parser.add_argument('--reverse-geocode', action='store_true', help='(Optional) use reverse geocode to fill missing location info')

    def extract_point_from_wkt(self, wkt_string):
        if not wkt_string:
            return None
        # sanitize common issues: remove commas between coords, trim
        s = wkt_string.strip()
        s = s.replace(',', ' ')
        match = re.search(r'POINT\(([-\d.]+)\s+([-\d.]+)\)', s)
        if match:
            try:
                a = float(match.group(1))
                b = float(match.group(2))
                # return as parsed (we'll try both orders when matching)
                return a, b
            except Exception:
                return None
        return None

    def find_candidates(self, point, tolerance_m=None):
        """Return a list of (model, instance, distance_m) candidate pin objects within tolerance.

        If `tolerance_m` is None, uses `DISTANCE_TOLERANCE_METERS`.
        """
        tol = DISTANCE_TOLERANCE_METERS if tolerance_m is None else tolerance_m
        candidates = []
        for model in ALL_PIN_MODELS:
            try:
                qs = model.objects.filter(pin__distance_lte=(point, D(m=tol)))
                # annotate distance if supported
                try:
                    qs = qs.annotate(distance=Distance('pin', point)).order_by('distance')
                except Exception:
                    qs = qs
                for inst in qs[:5]:
                    dist = None
                    try:
                        dist = getattr(inst, 'distance', None)
                        if dist is not None:
                            dist = float(dist.m)
                    except Exception:
                        dist = None
                    candidates.append((model, inst, dist))
            except Exception:
                # model may not have 'pin' field or DB doesn't support spatial query; skip
                continue
        # sort by distance where available
        candidates.sort(key=lambda x: x[2] if x[2] is not None else 1e9)
        return candidates

    def haversine_meters(self, lon1, lat1, lon2, lat2):
        """Return distance in meters between two lon/lat points using Haversine."""
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        R = 6371000  # Earth radius in meters
        return R * c

    def resolve_best_candidate(self, candidates, csv_category_name):
        """If multiple candidates: prefer one matching csv_category_name, else nearest."""
        if not candidates:
            return None
        if len(candidates) == 1:
            return candidates[0]
        # Try to match by category name
        if csv_category_name:
            key = csv_category_name.strip()
            mapping = CATEGORY_TO_MODEL_FIELD.get(key)
            if mapping:
                wanted_model = mapping[0]
                for model, inst, dist in candidates:
                    if model is wanted_model:
                        return (model, inst, dist)
            # case-insensitive fallback: compare lower names
            lower_key = key.lower()
            for model, inst, dist in candidates:
                model_name = model.__name__.lower()
                if lower_key in model_name or model_name in lower_key:
                    return (model, inst, dist)
        # otherwise nearest
        return candidates[0]

    def get_or_create_platform(self, platform_text):
        if not platform_text:
            return None
        text = platform_text.strip()
        # try exact match name
        try:
            return PostPlatform.objects.get(name__iexact=text)
        except PostPlatform.DoesNotExist:
            pass
        # try code
        try:
            return PostPlatform.objects.get(code__iexact=text)
        except PostPlatform.DoesNotExist:
            pass
        # try fuzzy among names
        names = list(PostPlatform.objects.values_list('name', flat=True))
        match = get_close_matches(text, names, n=1, cutoff=0.7)
        if match:
            return PostPlatform.objects.get(name=match[0])
        # create fallback platform (use text as name and code)
        return PostPlatform.objects.create(name=text.title(), code=text[:10].lower())

    def handle(self, *args, **options):
        csv_file = options['csv_file']
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
                for idx, row in enumerate(rows, 1):
                    try:
                        res = self.import_row(row)
                        if res['success']:
                            created += 1
                            status = '✓ CREATED'
                        else:
                            skipped += 1
                            status = '⊘ SKIPPED'
                        self.stdout.write(f"[{idx}/{total}] {status}: {res['link']} -> {res.get('message','')}")
                    except Exception as e:
                        skipped += 1
                        self.stdout.write(self.style.ERROR(f"[{idx}/{total}] ✗ ERROR: {str(e)[:120]}"))
                        logger.exception(f"Error importing social row {idx}: {row}")
                self.stdout.write(self.style.SUCCESS(f"Import complete. Total: {total} | Created: {created} | Skipped: {skipped}"))
        except FileNotFoundError:
            raise CommandError(f"CSV file not found: {csv_file}")

    def import_row(self, row):
        # csv columns: platform, link, reel_place_name, language, location_geometry, category_name, ...
        platform_text = row.get('platform', '').strip()
        link = row.get('link', '').strip()
        reel_place_name = row.get('reel_place_name', '') or row.get('location_name', '') or ''
        language = row.get('language', '').strip()
        location_geometry = row.get('location_geometry', '').strip()
        csv_category = row.get('category_name', '').strip()

        if not link:
            return {'success': False, 'link': 'N/A', 'message': 'Missing link'}
        # skip if link already exists
        if SocialPost.objects.filter(link=link).exists():
            return {'success': False, 'link': link, 'message': 'Link already imported'}

        # parse point
        coords = self.extract_point_from_wkt(location_geometry)
        if not coords:
            return {'success': False, 'link': link, 'message': 'Invalid location_geometry'}
        a, b = coords
        # Build two point variants: assume parsed is (lon, lat) first; we'll try both orders
        point = Point(a, b, srid=4326)        # interpreted as (x=a, y=b)
        swapped_point = Point(b, a, srid=4326)

        # Search all pin models for this point with progressive radii
        radii = [0, 10, 50, 200, 1000]  # meters; 0 means exact equality via pin__equals
        candidates = []
        chosen = None
        # iterate radii and stop when any candidates found
        for tol in radii:
            candidates = []
            for model in ALL_PIN_MODELS:
                try:
                    # Try both orientations: parsed (a,b) and swapped (b,a)
                    points_to_try = [point, swapped_point]
                    for p in points_to_try:
                        if tol == 0:
                            qs = model.objects.filter(pin__equals=p)
                            for inst in qs[:5]:
                                candidates.append((model, inst, 0.0))
                        else:
                            qs = model.objects.filter(pin__distance_lte=(p, D(m=tol)))
                            try:
                                qs = qs.annotate(distance=Distance('pin', p)).order_by('distance')
                            except Exception:
                                qs = qs
                            for inst in qs[:5]:
                                dist = None
                                try:
                                    dist = getattr(inst, 'distance', None)
                                    if dist is not None:
                                        dist = float(dist.m)
                                except Exception:
                                    dist = None
                                candidates.append((model, inst, dist))
                except Exception:
                    continue
            if candidates:
                # sort and pick best (prefer category match then nearest)
                candidates.sort(key=lambda x: x[2] if x[2] is not None else 1e9)
                chosen = self.resolve_best_candidate(candidates, csv_category)
                break

        # If no candidate found, skip the row (do not create standalone posts)
        if not chosen:
            # DB-level spatial queries returned nothing — fallback to Python-level comparison
            py_candidates = []
            try:
                for model in ALL_PIN_MODELS:
                    try:
                        for inst in model.objects.exclude(pin__isnull=True)[:2000]:
                            try:
                                geom = inst.pin
                                # ensure we have a Point; if not, use centroid
                                if hasattr(geom, 'geom_type') and geom.geom_type != 'Point':
                                    geom = geom.centroid
                                x = getattr(geom, 'x', None)
                                y = getattr(geom, 'y', None)
                                if x is None or y is None:
                                    continue
                                # compute distance to both orientations
                                try:
                                    d1 = self.haversine_meters(point.x, point.y, x, y)
                                except Exception:
                                    d1 = float('inf')
                                try:
                                    d2 = self.haversine_meters(swapped_point.x, swapped_point.y, x, y)
                                except Exception:
                                    d2 = float('inf')
                                dist_m = min(d1, d2)
                                if dist_m <= 1000:  # consider within 1km for fallback
                                    py_candidates.append((model, inst, dist_m))
                            except Exception:
                                continue
                    except Exception:
                        continue
            except Exception:
                py_candidates = []

            if py_candidates:
                py_candidates.sort(key=lambda x: x[2])
                chosen = self.resolve_best_candidate(py_candidates, csv_category)

        if not chosen:
            return {'success': False, 'link': link, 'message': 'No nearby pin found; skipped'}

        # determine platform
        platform = self.get_or_create_platform(platform_text)

        # Create SocialPost and link
        post = SocialPost(
            name=reel_place_name or link,
            platform=platform,
            link=link,
            language=language or None,
            published=False
        )

        # We have a chosen pin; create and link the post
        model, inst, dist = chosen
        # set corresponding FK field on SocialPost
        mapping_field = None
        # find mapping key by model
        for k, v in CATEGORY_TO_MODEL_FIELD.items():
            if v[0] is model:
                mapping_field = v[1]
                break
        # If we didn't find via mapping, use model name lower
        if not mapping_field:
            mapping_field = model.__name__.lower()
        # assign attribute if field exists
        if hasattr(post, mapping_field):
            setattr(post, mapping_field, inst)
        # also fill country/state/city based on inst.city if available
        try:
            inst_city = getattr(inst, 'city', None)
            if inst_city:
                post.city = inst_city
                post.state = inst_city.state
                post.country = inst_city.state.country
        except Exception:
            pass
        message = f'Linked to {model.__name__} id={inst.pk} dist_m={dist}'

        try:
            post.save()
            return {'success': True, 'link': link, 'message': message}
        except Exception as e:
            logger.exception(f"Failed to save SocialPost for link {link}: {e}")
            return {'success': False, 'link': link, 'message': f'Error saving post: {str(e)[:120]}'}
