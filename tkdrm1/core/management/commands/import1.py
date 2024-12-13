from django.core.management.base import BaseCommand
import math
import pandas

from core.models import Rtu, CustHouse, CustPost


class Command(BaseCommand):

    def handle(self, *args, **options):
        data = pandas.read_excel('BD_25-11-2024.xlsx',
                                 # skiprows=0,
                                 # nrows=2,
                                 header=None,
                                 sheet_name='Новая база2',
                                 usecols=range(0, 17),
                                 )

        clean_data = [['' if isinstance(j, float) and math.isnan(j) else str(j) for j in i] for i in data.values if isinstance(i[0], int)]  # noqa

        clean_clean_data = []
        for i in clean_data:
            clean_clean_data_row = []
            for j in i:
                if j == 'ДВТУ':
                    clean_clean_data_row.append('Дальневосточное таможенное управление')  # noqa
                elif j == 'ПТУ':
                    clean_clean_data_row.append('Приволжское таможенное управление')  # noqa
                elif j == 'СТУ':
                    clean_clean_data_row.append('Сибирское таможенное управление')  # noqa
                elif j == 'СЗТУ':
                    clean_clean_data_row.append('Северо-Западное таможенное управление')  # noqa
                elif j == 'УТУ':
                    clean_clean_data_row.append('Уральское таможенное управление')  # noqa
                elif j == 'ЦТУ':
                    clean_clean_data_row.append('Центральное таможенное управление')  # noqa
                elif j == 'ЮТУ':
                    clean_clean_data_row.append('Южное таможенное управление')
                elif j == 'СКТУ':
                    clean_clean_data_row.append('Северо-Кавказское таможенное управление')  # noqa
                else:
                    clean_clean_data_row.append(j)
            clean_clean_data.append(clean_clean_data_row)

        del_flag = 'm'
        while not (del_flag == 'y' or del_flag == 'n'):
            del_flag = input('Удолять в БД проекта таблицы РТУ, Таможни, Посты (y/n)?')  # noqa
        print(del_flag)

        if del_flag == 'y':
            CustPost.objects.all().delete()
            CustHouse.objects.all().delete()
            Rtu.objects.all().delete()

        print(clean_clean_data[0])
        print(clean_clean_data[1])
        print('...')
        print(clean_clean_data[len(clean_clean_data)-2])
        print(clean_clean_data[len(clean_clean_data)-1])

        for i in clean_clean_data:
            if i[7] not in ['1', '2', '3', '4']:
                print(f'Строка {i[0]}, невалидный столбец 8.')
