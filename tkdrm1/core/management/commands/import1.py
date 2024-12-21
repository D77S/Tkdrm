import os
import sys
from django.core.management.base import BaseCommand
import math
import pandas

from core.models import CustPlace, Rtu, CustHouse, CustPost


class Command(BaseCommand):

    def handle(self, *args, **options):

        def rtu_replace(list_in):
            list_out = []
            for i in list_in:
                data_row = []
                for j in i:
                    if j == 'ДВТУ':
                        data_row.append('Дальневосточное таможенное управление')  # noqa
                    elif j == 'ПТУ':
                        data_row.append('Приволжское таможенное управление')
                    elif j == 'СТУ':
                        data_row.append('Сибирское таможенное управление')
                    elif j == 'СЗТУ':
                        data_row.append('Северо-Западное таможенное управление')  # noqa
                    elif j == 'УТУ':
                        data_row.append('Уральское таможенное управление')
                    elif j == 'ЦТУ':
                        data_row.append('Центральное таможенное управление')
                    elif j == 'ЮТУ':
                        data_row.append('Южное таможенное управление')
                    elif j == 'СКТУ':
                        data_row.append('Северо-Кавказское таможенное управление')  # noqa
                    elif j == 'ТНП':
                        data_row.append('')
                    else:
                        data_row.append(j)
                list_out.append(data_row)
            return list_out

        # def code_finder():
        #     """."""
        #     code = codes.get(title, None)
        #     if code is None:
        #         temp_post = title.find('Таможенный пост')
        #         if temp_post != -1:
        #             temp_title_1 = title.replace('Таможенный пост', '')
        #             temp_title_1 = temp_title_1.strip()
        #             temp_code_2 = codes.get('Таможенный пост ' + temp_title_1, None)  # noqa
        #             if temp_code_2 is not None:
        #                 return temp_code_2
        #             temp_code_3 = codes.get(temp_title_1 + ' таможенный пост', None)  # noqa
        #             if temp_code_3 is not None:
        #                 return temp_code_3
        #         temp_post = title.find('таможенный пост')
        #         if temp_post != -1:
        #             temp_title_1 = title.replace('таможенный пост', '')
        #             temp_title_1 = temp_title_1.strip()
        #             temp_code_2 = codes.get('Таможенный пост ' + temp_title_1, None)  # noqa
        #             if temp_code_2 is not None:
        #                 return temp_code_2
        #             temp_code_3 = codes.get(temp_title_1 + ' таможенный пост', None)  # noqa
        #             if temp_code_3 is not None:
        #                 return temp_code_3
        #         return code
        #     return code

        # def make_flags_1_4(row):
        #     """Создание массива битовых флагов полей 1-3."""
        #     row_flags = []
        #     for j in range(1, 4):
        #         if i[j] == '':
        #             row_flags.append(False)
        #         else:
        #             row_flags.append(True)
        #     return row_flags

        # def field_processing(row, f_number):
        #     """Обработка отдельного поля с номером f_number в строке row.
        #     Возврат:
        #     0 - штатное завершение без записи в БД;
        #     1 - аварийное завершение без записи в БД;
        #     2 - штатное завершение.
        #     """
        #     if row[f_number] == 'ТНП' or row[f_number] == '':
        #         return 0
        #     # Попытка поиска кода т.органа
        #     code = code_finder(clean_codes, row[f_number])
        #     if code is None:
        #         # ошибка по коду т.органа, аварийное завершение обработки строки  # noqa
        #         print(f'Строка {i[0]}, не найден код т.органа для {row[f_number]}.')  # noqa
        #         return 1
        #     # Попытка поиска наличия в БД данного поля в одной из таблиц
        #     # и запись в БД, если там ещё нет.
        #     if f_number == 1:
        #         if not Rtu.objects.filter(title=row[1]).exists():
        #             Rtu.objects.create(title=row[1], code=code, level=1)
        #         if not CustPlace.objects.filter(title=row[1]).exists():
        #             CustPlace.objects.create(title=row[1], code=code, level=1, upper_id=None)  # noqa
        #         return 2
        #     elif f_number == 2:
        #         if row[1] == 'ТНП':
        #             if not CustHouse.objects.filter(title=row[2]).exists():
        #                 CustHouse.objects.create(title=row[2], code=code, level=2, upper_id=None)  # noqa
        #             if not CustPlace.objects.filter(title=row[2]).exists():
        #                 CustPlace.objects.create(title=row[2], code=code, level=2, upper_id=None)  # noqa
        #         else:
        #             if not CustHouse.objects.filter(title=row[2]).exists():
        #                 if Rtu.objects.filter(title=row[1]).exists():
        #                     upper_id = Rtu.objects.get(title=row[1])
        #                     CustHouse.objects.create(title=row[2], code=code, level=2, upper_id=upper_id)  # noqa
        #                 else:
        #                     print(f'Строка {i[0]}, в БД1 не найден вышестоящий т.о. для {row[2]}.')  # noqa
        #             if not CustPlace.objects.filter(title=row[2]).exists():
        #                 if CustPlace.objects.filter(title=row[1]).exists():
        #                     upper_id = CustPlace.objects.get(title=row[1])
        #                     CustPlace.objects.create(title=row[2], code=code, level=2, upper_id=upper_id)  # noqa
        #                 else:
        #                     print(f'Строка {i[0]}, в БД2 не найден вышестоящий т.о. для {row[2]}.')  # noqa
        #         return 2

        #     elif f_number == 3:
        #         if not CustPost.objects.filter(title=row[3]).exists():
        #             if CustHouse.objects.filter(title=row[2]).exists():
        #                 upper_id = CustHouse.objects.get(title=row[2])
        #                 CustPost.objects.create(title=row[3], code=code, level=3, upper_id=upper_id)  # noqa
        #             else:
        #                 print(f'Строка {i[0]}, в БД1 не найден вышестоящий т.о. для {row[3]}.')  # noqa
        #         if not CustPlace.objects.filter(title=row[3]).exists():
        #             if CustPlace.objects.filter(title=row[2]).exists():
        #                 upper_id = CustPlace.objects.get(title=row[2])
        #                 CustPlace.objects.create(title=row[3], code=code, level=3, upper_id=upper_id)  # noqa
        #             else:
        #                 print(f'Строка {i[0]}, в БД2 не найден вышестоящий т.о. для {row[3]}.')  # noqa

        #     return 2

        current_excel_files_list = [x for x in os.listdir() if (
            x.endswith('.xlsx') or
            x.endswith('.xls') or
            x.endswith('.xlsm')
        )]
        if len(current_excel_files_list) == 0:
            print('Эксель-файлов в текущей папке не найдено.')
            sys.exit()
        data = pandas.read_excel(current_excel_files_list[0],
                                 # skiprows=0,
                                 # nrows=2,
                                 header=None,
                                 sheet_name='Новая база2',
                                 usecols=range(0, 17),
                                 )

        clean_data_first = [['' if isinstance(j, float) and math.isnan(j) else str(j) for j in i] for i in data.values if isinstance(i[0], int)]  # noqa
        clean_data_second = rtu_replace(clean_data_first)

        del_flag = 't'
        while not (del_flag == 'y' or del_flag == 'n'):
            del_flag = input('Удолять в БД проекта таблицы таможенных органов (y/n)?')  # noqa

        if del_flag == 'y':
            CustPlace.objects.all().delete()
            CustPost.objects.all().delete()
            CustHouse.objects.all().delete()
            Rtu.objects.all().delete()

        print(clean_data_second[0])
        print(clean_data_second[1])
        print('...')
        print(clean_data_second[len(clean_data_second)-2])
        print(clean_data_second[len(clean_data_second)-1])

        sys.exit()

        for i in clean_data_second:

            row_flags = make_flags_1_4(i)

            if i[7] not in ['1', '2', '3', '4']:
                print(f'Строка {i[0]}, невалидный столбец 8.')
                continue

            if i[7] == '1' and (row_flags == [True, True, True] or row_flags == [True, True, False]):  # noqa
                # валидная строка, пункт пропуска
                # обработка названия РТУ
                field_processing(i, 1)
                # обработка названия таможни
                field_processing(i, 2)
                # обработка названия т.поста (если есть!)
                field_processing(i, 3)
                continue

            if i[7] == '2' and (row_flags == [True, True, True] or row_flags == [True, False, True]):  # noqa
                # валидная строка, пост
                # обработка названия РТУ
                field_processing(i, 1)
                # обработка названия таможни (если есть!)
                field_processing(i, 2)
                # обработка названия т.поста (если есть!)
                field_processing(i, 3)

                continue

            if i[7] == '3' and row_flags == [True, True, False]:
                # валидная строка, таможня
                # обработка названия РТУ
                field_processing(i, 1)
                # обработка названия таможни
                field_processing(i, 2)
                continue
            if i[7] == '4' and row_flags == [True, False, False]:
                # валидная строка, РТУ
                # обработка названия РТУ
                field_processing(i, 1)
                continue

            print(f'Строка {i[0]}, невалидное сочетание столбцов 2, 3, 4, 8.')
