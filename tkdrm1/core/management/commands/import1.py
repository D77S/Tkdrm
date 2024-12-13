from django.core.management.base import BaseCommand, CommandError
import pandas

class Command(BaseCommand):

    def handle(self, *args, **options):
        data=pandas.read_excel('BD_25-11-2024.xlsx',
                               # skiprows=5,
                               # nrows=2,
                               header=0,
                               sheet_name='Новая база2',
                               usecols=range(0, 17),
                               )

        clean_data = [[j for j in i] for i in data.values]


        print(clean_data[len(clean_data)-2])
        print(clean_data[len(clean_data)-1])
                
