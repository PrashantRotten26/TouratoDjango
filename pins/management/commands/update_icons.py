import csv
from django.core.management.base import BaseCommand
from pins.models import (MainAttraction, ThingsToDo, PlacesToVisit, PlacesToEat, Market,
                        CountryInfo, DestinationGuide, PlaceInformation, TravelHacks,
                        Festivals, FamousPhotoPoint, Activities, Hotel)

class Command(BaseCommand):
    help = 'Update pin icons from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')

    def handle(self, *args, **options):
        name_to_model = {
            'Country Info': CountryInfo,
            'Activities': Activities,
            'Destination Guide': DestinationGuide,
            'Places to Visit': PlacesToVisit,
            'Places to Eat': PlacesToEat,
            'Hotels': Hotel,
            'Market': Market,
            'Travel Hacks': TravelHacks,
            'Festivals': Festivals,
            'Main Attraction': MainAttraction,
            'Place Information': PlaceInformation,
            'Famous Photo Point': FamousPhotoPoint,
        }

        with open(options['csv_file'], 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row['name']
                marker_icon_value = row['svg'].replace('/Markers/', '')
                icon_value = row['btnIcon'].replace('/Icons/', '')
                
                if name in name_to_model:
                    model = name_to_model[name]
                    updated = model.objects.update(
                        icon=icon_value,
                        marker_icon=marker_icon_value
                    )
                    self.stdout.write(f"Updated {updated} {name} records - icon: {icon_value}, marker_icon: {marker_icon_value}")
                else:
                    self.stdout.write(f"No model found for: {name}")