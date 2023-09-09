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
            print(Path(csv_path + csv_file).resolve())
            with open(csv_path + csv_file, encoding='UTF-8') as file:
                reader = csv.reader(file)
                model.objects.all().delete()
                for row in reader:
                    obg = model(name=row[0], measurement_unit=row[1])
                    obg.save()

