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

        def code_finder(array, row, f_number):
            """."""
            code = []
            # Если обрабатывается объект уровня 1 (РТУ)
            if f_number == 1:
                print(f'Работает code_finder, обработка поля РТУ, ищем в массиве значение {row[1]}')  # noqa
                for i in array:
                    if i[11] != 'основная':
                        continue
                    if (i[1] == row[1] and
                            i[2] == '' and
                            i[3] == '' and
                            i[8] == '4'):
                        code.append(i[4])
                if len(code) == 1:
                    print(f'code_finder: найден код для РТУ {row[1]}: {code[0]}')  # noqa
                    return code[0]
                elif len(code) > 1:
                    print(f'Внимание!! code_finder: найдено кодов для РТУ {row[1]} больше одного: {code}')  # noqa
                    return None
                else:
                    print(f'code_finder: для РТУ {row[1]} код так и не был найден')  # noqa
                    return None
            # Если обрабатывается объект уровня 2 (таможня)
            elif f_number == 2:
                print(f'Работает code_finder, обработка поля таможня, ищем в массиве значение {row[2]}')  # noqa
                for i in array:
                    if i[11] != 'основная':
                        continue
                    if (i[1] == row[1] and
                        i[2] == row[2] and
                        i[3] == '' and
                            i[8] == '3'):
                        code.append(i[4])
                if len(code) == 1:
                    print(f'code_finder: найден код для таможни {row[2]} при РТУ {row[1]}: {code[0]}')  # noqa
                    return code[0]
                elif len(code) > 1:
                    print(f'Внимание!! code_finder: найдено кодов для {row[2]} при РТУ {row[1]} больше одного: {code}')  # noqa
                    return None
                else:
                    print(f'code_finder: для таможни {row[2]} при РТУ {row[1]} код так и не был найден')  # noqa
                    return None
            # Если обрабатывается объект уровня 3 (пост)
            pass

        def field_processing(array, row, f_number):
            """Обработка отдельного поля с номером f_number в строке row.
            Возврат:
            0 - завершение без записи в БД;
            1 - завершение c записью в БД.
            """
            if row[f_number] == '':
                return 0

            # Если анализируется объект уровня 1 (РТУ)
            if f_number == 1:
                # Попытаться найти в array код искомого объекта РТУ  # noqa
                code_1 = code_finder(array, row, 1)
                if code_1 is None:
                    return 0
                print(f'field_processing: обработка РТУ {row[1]} с кодом {code_1}')  # noqa
                # Если в БД в таблице Rtu такого ещё нет
                if not Rtu.objects.filter(title=row[1], code=code_1).exists():  # noqa
                    print('создаем РТУ в БД1')
                    Rtu.objects.create(title=row[f_number], code=code_1, level=1)  # noqa
                # Если в БД в таблице CustPlace такого еще нет
                if not CustPlace.objects.filter(title=row[1], code=code_1).exists():  # noqa
                    print('создаем РТУ в БД2')
                    CustPlace.objects.create(title=row[1], code=code_1, level=1, upper_id=None)  # noqa
                return 1

            # Если анализируется объект уровня 2 (таможня)
            elif f_number == 2:
                # Попытаться найти в array коды
                # РТУ для искомой таможни или None для ТНП  # noqa
                if row[1] != '':
                    code_1 = code_finder(array, row, 1)
                    if code_1 is None:
                        return 0
                else:
                    code_1 = None
                # искомой таможни
                code_2 = code_finder(array, row, 2)
                if code_2 is None:
                    return 0
                print(f'field_processing: обработка таможни {row[2]} с кодом {code_2} при РТУ {row[1]} с кодом {code_1}')  # noqa
                # Над обработать два случая:
                # 1. code_1 is None and code_2 is not None (таможня ТНП)
                # 2. code_1 is not None and code_2 is not None (таможня не ТНП)
                # Случай 1.
                if code_1 is None:
                    # Если в БД в таблице CustHouse такого еще нет
                    if not CustHouse.objects.filter(title=row[2], code=code_2, upper_id=None).exists():  # noqa
                        print('создаем таможню в БД1')
                        CustHouse.objects.create(title=row[2], code=code_2, level=2, upper_id=None)  # noqa
                    # Если в БД в таблице CustPlace такого еще нет
                    if not CustPlace.objects.filter(title=row[2], code=code_2, upper_id=None).exists():  # noqa
                        print('создаем таможню в БД2')
                        CustPlace.objects.create(title=row[2], code=code_2, level=2, upper_id=None)  # noqa
                    return 1
                # Случай 2.
                else:
                    # По РТУ, если в БД в таблице Rtu такого ещё нет
                    if not Rtu.objects.filter(title=row[1], code=code_1).exists():  # noqa
                        print('создаем РТУ в БД1')
                        curr_rtu_1 = Rtu.objects.create(title=row[1], code=code_1, level=1)  # noqa
                    else:
                        print('получаем из БД1 объект РТУ, он уже был там')
                        curr_rtu_1 = Rtu.objects.get(title=row[1], code=code_1, level=1)  # noqa
                    # По РТУ, если в БД в таблице CustPlace такого еще нет
                    if not CustPlace.objects.filter(title=row[1], code=code_1).exists():  # noqa
                        print('создаем РТУ в БД2')
                        curr_rtu_2 = CustPlace.objects.create(title=row[1], code=code_1, level=1, upper_id=None)  # noqa
                    else:
                        print('получаем из БД2 объект РТУ, он уже был там')
                        curr_rtu_2 = CustPlace.objects.get(title=row[1], code=code_1, level=1, upper_id=None)  # noqa
                    # По таможне, если в БД в таблице CustHouse такой ещё нет
                    if not CustHouse.objects.filter(title=row[2], code=code_2, level=2, upper_id=curr_rtu_1).exists():  # noqa
                        print('создаем таможню в БД1')
                        CustHouse.objects.create(title=row[2], code=code_2, level=2, upper_id=curr_rtu_1)  # noqa
                    # По таможне, если в БД в таблице CustPlace такой еще нет
                    if not CustPlace.objects.filter(title=row[2], code=code_2, level=2, upper_id=curr_rtu_2).exists():  # noqa
                        print('создаем таможню в БД2')
                        CustPlace.objects.create(title=row[2], code=code_2, level=2, upper_id=curr_rtu_2)  # noqa
                    return 1

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

        for i in clean_data_second:

            if i[8] not in ['1', '2', '3', '4']:
                print(f'Строка {i[0]}, невалидный столбец "тип объекта".')
                continue

            # валидная строка

            # обработка названия РТУ, если есть
            if i[1] != '':
                print(f'Главный цикл. Строка {i[0]}, обработка поля РТУ, равного {i[1]}')  # noqa
                field_processing(clean_data_second, i, 1)

            # обработка названия таможни, если есть
            if i[2] != '':
                print(f'Главный цикл. Строка {i[0]}, обработка поля таможня, равного {i[2]}')  # noqa
                field_processing(clean_data_second, i, 2)

            # if i[0] == '6514':
            #     sys.exit()
            # обработка названия т.поста (если есть!)
            # field_processing(i, 3)
