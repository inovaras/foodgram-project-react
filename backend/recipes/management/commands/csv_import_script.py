import csv
from django.core.management.base import BaseCommand
from pathlib import Path

from recipes.models import (
    Ingredient,
)


class Command(BaseCommand):
    help = 'Transfer from csv to database'

    def handle(self, *args, **options):
        csv_path = '../data/'
        csv_files = [
            'ingredients.csv'
        ]
        model_list = [
            Ingredient
        ]
        for csv_file, model in zip(csv_files, model_list):
            with open(csv_path + csv_file, encoding='UTF-8') as file:
                reader = csv.reader(file)
                model.objects.all().delete()
                model.objects.bulk_create(model(name=row[0], measurement_unit=row[1]) for row in reader)
