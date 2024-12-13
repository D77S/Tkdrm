from django.core.management.base import BaseCommand, CommandError
import pandas

class Command(BaseCommand):

    def handle(self, *args, **options):
        # Чтение из эксель-файла в пандасовский тип данных.
        # Его можно потом имтерировать двумерным образом.
        data=pandas.read_excel('BD_25-11-2024.xlsx',
                               # skiprows=0,
                               # nrows=2,
                               header=None,
                               sheet_name='Новая база2',
                               usecols=range(0, 17),
                               )

        # Пример кусочка полученных данных:
        print('Пример кусочка данных:')
        print(data.values[10])

        # Преобразование в нормальный тип данных, список списков.
        # Заодно заменяем все "пустые ячейки" на ''.
        clean_data = [['' if str(j) == 'nan' else str(j) for j in i] for i in data.values if isinstance(i[0], int)]

        # Заменяем некоторые сокращения на полные их названия.
        clean_clean_data = []
        for i in clean_data:
            clean_clean_data_row = []
            for j in i:
                if j =='ДВТУ':
                    clean_clean_data_row.append('Дальневосточное таможенное управление')
                elif j == 'ПТУ':
                    clean_clean_data_row.append('Приволжское таможенное управление')
                elif j == 'СТУ':
                    clean_clean_data_row.append('Сибирское таможенное управление')
                elif j == 'СЗТУ':
                    clean_clean_data_row.append('Северо-Западное таможенное управление')
                elif j == 'УТУ':
                    clean_clean_data_row.append('Уральское таможенное управление')
                elif j == 'ЦТУ':
                    clean_clean_data_row.append('Центральное таможенное управление')
                elif j == 'ЮТУ':
                    clean_clean_data_row.append('Южное таможенное управление')
                elif j == 'СКТУ':
                    clean_clean_data_row.append('Северо-Кавказское таможенное управление')
                else:
                    clean_clean_data_row.append(j)
            clean_clean_data.append(clean_clean_data_row)
        
        del_flag = 'm'
        while not(del_flag=='y' or del_flag=='n'):
            del_flag = input('Удолять старую БД (y/n)?')
        print(del_flag)


        print(clean_clean_data[0])
        print(clean_clean_data[1])
        print('...')
        print(clean_clean_data[len(clean_clean_data)-2])
        print(clean_clean_data[len(clean_clean_data)-1])
                
