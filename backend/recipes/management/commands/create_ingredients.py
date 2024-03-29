import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import ingredients from CSV file'

    def handle(self, *args, **options):
        csv_file = os.path.join(settings.BASE_DIR, 'data', 'ingredients.csv')
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                name, measurement_unit = row
                Ingredient.objects.create(
                    name=name.strip(),
                    measurement_unit=measurement_unit.strip()
                )
        self.stdout.write(
            self.style.SUCCESS('Ingredients imported successfully'))
