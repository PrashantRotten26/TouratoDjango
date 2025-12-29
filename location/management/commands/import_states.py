import json
import os
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import GEOSGeometry
from django.db import transaction
from location.models import Country, State

class Command(BaseCommand):
    help = 'Import states from GeoJSON file'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='static/all_contry_states.geojson',
            help='Path to states GeoJSON file'
        )
    
    def handle(self, *args, **options):
        geojson_path = options['file']
        
        if not os.path.exists(geojson_path):
            self.stdout.write(
                self.style.ERROR(f'GeoJSON file not found: {geojson_path}')
            )
            return
        
        self.stdout.write(f'Starting states import from: {geojson_path}')
        
        with open(geojson_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        created = 0
        updated = 0
        skipped = 0
        country_not_found = 0
        
        self.stdout.write(f'Processing {len(data["features"])} features...')
        
        with transaction.atomic():
            for feature in data['features']:
                props = feature['properties']
                geom = feature['geometry']
                
                # Get state name and country name
                state_name = props.get('name')
                country_name = props.get('admin')
                
                if not state_name or not country_name:
                    skipped += 1
                    self.stdout.write(
                        self.style.WARNING(f'Skipping feature - missing name or admin field')
                    )
                    continue
                
                state_name = state_name.strip()
                country_name = country_name.strip()
                
                try:
                    # Find the country first
                    try:
                        country = Country.objects.get(name=country_name)
                    except Country.DoesNotExist:
                        country_not_found += 1
                        self.stdout.write(
                            self.style.WARNING(f'Country not found: {country_name} for state: {state_name}')
                        )
                        continue
                    
                    # Convert geometry to Django GEOSGeometry
                    geometry = GEOSGeometry(json.dumps(geom), srid=4326)
                    
                    # Create or update state
                    state, is_created = State.objects.update_or_create(
                        country=country,
                        name=state_name,
                        defaults={'geometry': geometry}
                    )
                    
                    if is_created:
                        created += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'Created: {country_name} - {state_name}')
                        )
                    else:
                        updated += 1
                        self.stdout.write(f'Updated: {country_name} - {state_name}')
                        
                except Exception as e:
                    skipped += 1
                    self.stdout.write(
                        self.style.ERROR(f'Error processing {country_name} - {state_name}: {str(e)}')
                    )
                    continue
        
        self.stdout.write('\nImport Summary:')
        self.stdout.write(f'  Created: {created}')
        self.stdout.write(f'  Updated: {updated}')
        self.stdout.write(f'  Skipped: {skipped}')
        self.stdout.write(f'  Country not found: {country_not_found}')
        self.stdout.write(f'  Total processed: {created + updated + skipped + country_not_found}')
        self.stdout.write(self.style.SUCCESS('States import completed!'))

#python manage.py import_states
       