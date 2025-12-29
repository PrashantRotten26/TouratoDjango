import json
import os
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import GEOSGeometry
from django.db import transaction
from location.models import Country

class Command(BaseCommand):
    help = 'Import countries from GeoJSON file'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='static/contory_geojson.geojson',
            help='Path to GeoJSON file'
        )
    
    def handle(self, *args, **options):
        geojson_path = options['file']
        
        if not os.path.exists(geojson_path):
            self.stdout.write(
                self.style.ERROR(f'GeoJSON file not found: {geojson_path}')
            )
            return
        
        self.stdout.write(f'Starting country import from: {geojson_path}')
        
        with open(geojson_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        created = 0
        updated = 0
        skipped = 0
        
        self.stdout.write(f'Processing {len(data["features"])} features...')
        
        with transaction.atomic():
            for feature in data['features']:
                props = feature['properties']
                geom = feature['geometry']
                
                # Get country name from ADMIN field
                country_name = props.get('ADMIN')
                
                if not country_name:
                    skipped += 1
                    self.stdout.write(
                        self.style.WARNING('Skipping feature without ADMIN field')
                    )
                    continue
                
                country_name = country_name.strip()
                
                try:
                    # Convert geometry to Django GEOSGeometry
                    geometry = GEOSGeometry(json.dumps(geom), srid=4326)
                    
                    # Create or update country
                    country, is_created = Country.objects.update_or_create(
                        name=country_name,
                        defaults={'geometry': geometry}
                    )
                    
                    if is_created:
                        created += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'Created: {country_name}')
                        )
                    else:
                        updated += 1
                        self.stdout.write(f'Updated: {country_name}')
                        
                except Exception as e:
                    skipped += 1
                    self.stdout.write(
                        self.style.ERROR(f'Error processing {country_name}: {str(e)}')
                    )
                    continue
        
        self.stdout.write('\nImport Summary:')
        self.stdout.write(f'  Created: {created}')
        self.stdout.write(f'  Updated: {updated}')
        self.stdout.write(f'  Skipped: {skipped}')
        self.stdout.write(f'  Total processed: {created + updated + skipped}')
        self.stdout.write(self.style.SUCCESS('Import completed!'))