from django.core.management.base import BaseCommand, CommandError
import csv
# from staff.models import Staff

class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('3.csv') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                row2 = row
                # firstname = row['firstname']
                # lastname = row['lastname']
                # email = row['email']
                # staff = Staff(firstname=firstname, lastname=lastname, email=email)
                # staff.save()
            print(type(row2))
    # csv_file.close() # you don't need this since you used `with`