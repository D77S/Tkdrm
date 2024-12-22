import os
import sys
from django.core.management.base import BaseCommand
import math
import pandas

from core.models import CustPlace, Rtu, CustHouse, CustPost


class Command(BaseCommand):

    def handle(self, *args, **options):

        def rtu_replace(list_in):
            """Принимает список строк.
            В каждой строке принятого списка смотрит второй элемент,
            если там аббревиатура - то заменяет её на полное имя по словарю.
            Возвращает измененный список."""
            PATTERN = {
                'ДВТУ': 'Дальневосточное таможенное управление',
                'ПТУ': 'Приволжское таможенное управление',
                'СТУ': 'Сибирское таможенное управление',
                'СЗТУ': 'Северо-Западное таможенное управление',
                'УТУ': 'Уральское таможенное управление',
                'ЦТУ': 'Центральное таможенное управление',
                'ЮТУ': 'Южное таможенное управление',
                'СКТУ': 'Северо-Кавказское таможенное управление',
                'ТНП': ''
            }
            list_out = []
            for i in list_in:
                data_row = i
                if data_row[1] in PATTERN.keys():
                    data_row[1] = PATTERN.get(data_row[1])
                list_out.append(data_row)
            return list_out

        def code_finder(array, row, f_number):
            """Принимает список всех строк, одну (очередрую анализируемую)
            из него же, и номер поля в ней.
            В этом списке возможно есть строки, в которых в поле 4 есть код.
            Из строки row извлекается поле номер f_number,
            затем по списку array перебираются строки в поисках такой,
            у которой выполняются все условия:
            - все поля от 1-го по f_number совпадают с полями в row
              тех же номеров;
            - в поле 11 текст "основная";
            - значение поля 8, сложенное со значением f_number, равно 5.
            Найденных строк с данными условиями должна быть ровано одна.
            Из найденной извлекается код из поля 4 и возвращается.
            Если значение f_number не равно 1 или 2 или 3 - возвращается None.
            Если в row поле f_number пусто - возвращается None.
            Если не найдено - возвращается 'not found'.
            Если найдено более одной такой - возвращается 'found many'.
            """
            # print(f'code_finder: обработка поля уровня \'{f_number}\', ищем в массиве значение \'{row[f_number]}\'')  # noqa
            if (f_number not in [1, 2, 3]) or row[f_number] == '':
                return None
            code = []
            temp_row = []
            for j in range(1, 3 + 1):
                if j <= f_number:
                    temp_row.append(row[j])
                else:
                    temp_row.append('')

            for i in array:
                if i[11] != 'основная':
                    continue
                if i[1:4] == temp_row and (f_number + int(i[8]) == 5):
                    code.append(i[4])

            if len(code) == 1:
                # print(f'code_finder: найден код для поля уровня \'{f_number}\' со значением \'{row[f_number]}\': \'{code[0]}\'')  # noqa
                return code[0]
            elif len(code) > 1:
                print(f'Внимание!! code_finder: найдено кодов для поля уровня \'{f_number}\' со значением \'{row[f_number]}\' больше одного, а именно: {code}')  # noqa
                return 'found many'
            else:
                # print(f'code_finder: для поля уровня \'{f_number}\' со значением \'{row[f_number]}\' код так и не был найден')  # noqa
                return 'not found'

        def field_processing(array, row, f_number):
            """Обработка отдельного поля с номером f_number в строке row.
            Возврат:
            (0, 0, 0) - завершение без записи в БД;
            (1, <объект БД1>, <объект БД2) - завершение c записью в БД.
            """
            FAIL = (0, 0, 0)
            if row[f_number] == '':
                return FAIL

            # Если анализируется объект уровня 1 (РТУ)
            if f_number == 1:
                # Попытаться найти в array код искомого РТУ
                code_1 = code_finder(array, row, 1)
                # Для всех уровней от 1 до текущего (тут: 1)
                # проверка на not found и found many
                if code_1 == 'not found' or code_1 == 'found many':
                    return FAIL
                # для текущего уровня проверка на None (не пуст, но не найден)
                if code_1 is None:
                    return FAIL

                # print(f'field_processing: обработка поля уровня \'{f_number}\', значения \'{row[f_number]}\', с кодом \'{code_1}\'')  # noqa
                # Если в БД в таблице Rtu такого ещё нет
                f1 = f2 = False
                if not Rtu.objects.filter(title=row[1], code=code_1).exists():  # noqa
                    f1 = True
                    curr_1 = Rtu.objects.create(title=row[f_number], code=code_1, level=1)  # noqa
                # Если в БД в таблице CustPlace такого еще нет
                if not CustPlace.objects.filter(title=row[1], code=code_1).exists():  # noqa
                    f2 = True
                    curr_2 = CustPlace.objects.create(title=row[1], code=code_1, level=1, upper_id=None)  # noqa
                if f1 and f2:
                    return (1, curr_1, curr_2)
                else:
                    return FAIL

            # Если анализируется объект уровня 2 (таможня)
            elif f_number == 2:
                # Попытаться найти в array коды РТУ для искомой таможни или None для ТНП  # noqa
                code_1 = code_finder(array, row, 1)
                # искомой таможни
                code_2 = code_finder(array, row, 2)
                # Для всех уровней от 1 до текущего (тут: 2)
                # проверка на not found и found many
                if code_1 == 'not found' or code_1 == 'found many':
                    return FAIL
                if code_2 == 'not found' or code_2 == 'found many':
                    return FAIL
                # для текущего уровня проверка на None (не пуст, но не найден)
                if code_2 is None:
                    return FAIL

                # print(f'field_processing: обработка поля уровня \'{f_number}\', значения \'{row[f_number]}\', с кодом \'{code_2}\'')  # noqa
                # Над обработать два случая:
                # 1. code_1 is None,     code_2 is not None (таможня ТНП)
                # 2. code_1 is not None, code_2 is not None (таможня не ТНП)
                # Случай 1.
                if code_1 is None:
                    # По текущему уровню, если в БД1 такой ещё нет
                    f1 = f2 = False
                    if not CustHouse.objects.filter(title=row[2], code=code_2, upper_id=None, upper_level=None).exists():  # noqa
                        f1 = True
                        curr_1 = CustHouse.objects.create(title=row[2], code=code_2, level=2, upper_id=None, upper_level=None)  # noqa
                    # По текущему уровню, если в БД2 такой еще нет
                    if not CustPlace.objects.filter(title=row[2], code=code_2, upper_id=None).exists():  # noqa
                        f2 = True
                        curr_2 = CustPlace.objects.create(title=row[2], code=code_2, level=2, upper_id=None)  # noqa
                    if f1 and f2:
                        return (1, curr_1, curr_2)
                    else:
                        return FAIL
                # Случай 2.
                if code_1 is not None:
                    # По уровню, вышестоящему к текущему, если в БД1 такого ещё нет  # noqa
                    if not Rtu.objects.filter(title=row[1], code=code_1).exists():  # noqa
                        curr_rtu_1 = Rtu.objects.create(title=row[1], code=code_1, level=1)  # noqa
                    else:
                        curr_rtu_1 = Rtu.objects.get(title=row[1], code=code_1, level=1)  # noqa
                    # По уровню, вышестоящему к текущему, если в БД2 такого ещё нет  # noqa
                    if not CustPlace.objects.filter(title=row[1], code=code_1).exists():  # noqa
                        curr_rtu_2 = CustPlace.objects.create(title=row[1], code=code_1, level=1, upper_id=None)  # noqa
                    else:
                        curr_rtu_2 = CustPlace.objects.get(title=row[1], code=code_1, level=1, upper_id=None)  # noqa
                    # По текущему уровню, если в БД1 такой ещё нет
                    f1 = f2 = False
                    if not CustHouse.objects.filter(title=row[2], code=code_2, level=2, upper_id=curr_rtu_1, upper_level='1').exists():  # noqa
                        f1 = True
                        curr_1 = CustHouse.objects.create(title=row[2], code=code_2, level=2, upper_id=curr_rtu_1, upper_level='1')  # noqa
                    # По текущему уровню, если в БД2 такой еще нет
                    if not CustPlace.objects.filter(title=row[2], code=code_2, level=2, upper_id=curr_rtu_2).exists():  # noqa
                        f2 = True
                        curr_2 = CustPlace.objects.create(title=row[2], code=code_2, level=2, upper_id=curr_rtu_2)  # noqa
                    if f1 and f2:
                        return (1, curr_1, curr_2)
                    else:
                        return FAIL

            elif f_number == 3:
                # Попытаться найти в array коды РТУ для искомого поста таможни или None для ТНП  # noqa
                code_1 = code_finder(array, row, 1)
                # искомой таможни
                code_2 = code_finder(array, row, 2)
                # искомого поста
                code_3 = code_finder(array, row, 3)
                # Для всех уровней от 1 до текущего (тут: 3)
                # проверка на not found и found many
                if code_1 == 'not found' or code_1 == 'found many':
                    return FAIL
                if code_2 == 'not found' or code_2 == 'found many':
                    return FAIL
                if code_3 == 'not found' or code_3 == 'found many':
                    return FAIL
                # для текущего уровня проверка на None (не пуст, но не найден)
                if code_3 is None:
                    return FAIL

                # print(f'field_processing: обработка поля уровня \'{f_number}\', значения \'{row[f_number]}\', с кодом \'{code_3}\'')  # noqa
                # Над обработать четыре случая:
                # 1. code_1 is None,     code_2 is None,     code_3 is not None (пост ТНП)  # noqa
                # 2. code_1 is None,     code_2 is not None, code_3 is not None (пост таможни ТНП)  # noqa
                # 3. code_1 is not None, code_2 is None,     code_3 is not None (пост РТУ)  # noqa
                # 4. code_1 is not None, code_2 is not None, code_3 is not None (пост таможни РТУ)  # noqa
                # Случай 1.
                if code_1 is None and code_2 is None:
                    # По уровню 3, если в БД1 такой ещё нет
                    f1 = f2 = False
                    if not CustPost.objects.filter(title=row[3], code=code_3, upper_id=None, upper_level=None).exists():  # noqa
                        f1 = True
                        curr_1 = CustPost.objects.create(title=row[3], code=code_3, upper_id=None, upper_level=None)  # noqa
                    # По уровню 3, если в БД2 такой еще нет
                    if not CustPlace.objects.filter(title=row[3], code=code_3, upper_id=None).exists():  # noqa
                        f2 = True
                        curr_2 = CustPlace.objects.create(title=row[3], code=code_3, upper_id=None)  # noqa
                    if f1 and f2:
                        return (1, curr_1, curr_2)
                    else:
                        return FAIL
                # Случай 2.
                if code_1 is None and code_2 is not None:
                    # По уровню, вышестоящему к текущему, если в БД1 такого ещё нет  # noqa
                    if not CustHouse.objects.filter(title=row[2], code=code_2).exists():  # noqa
                        curr_ch_1 = CustHouse.objects.create(title=row[2], code=code_2, level=2, upper_id=None, upper_level=None)  # noqa
                    else:
                        curr_ch_1 = CustHouse.objects.get(title=row[2], code=code_2)  # noqa
                    # По уровню, вышестоящему к текущему, если в БД2 такого ещё нет  # noqa
                    if not CustPlace.objects.filter(title=row[2], code=code_2).exists():  # noqa
                        curr_ch_2 = CustPlace.objects.create(title=row[2], code=code_2, level=2, upper_id=None)  # noqa
                    else:
                        curr_ch_2 = CustPlace.objects.get(title=row[2], code=code_2)  # noqa
                    # По текущему уровню, если в БД1 такой еще нет
                    f1 = f2 = False
                    if not CustPost.objects.filter(title=row[3], code=code_3, level=3, upper_id=curr_ch_1, upper_level='2').exists():  # noqa
                        f1 = True
                        curr_1 = CustPost.objects.create(title=row[3], code=code_3, level=3, upper_id=curr_ch_1, upper_level='2')  # noqa
                    # По текущему уровню, если в БД2 такой еще нет
                    if not CustPlace.objects.filter(title=row[3], code=code_3).exists():  # noqa
                        f2 = True
                        curr_2 = CustPlace.objects.create(title=row[3], code=code_3, level=3, upper_id=curr_ch_2)  # noqa
                    if f1 and f2:
                        return (1, curr_1, curr_2)
                    else:
                        return FAIL
                # Случай 3.
                if code_1 is not None and code_2 is None:
                    # По уровню, вышестоящему к текущему, если в БД1 такого ещё нет  # noqa
                    if not Rtu.objects.filter(title=row[1], code=code_1).exists():  # noqa
                        curr_rtu_1 = Rtu.objects.create(title=row[1], code=code_1, level=1)  # noqa
                    else:
                        curr_rtu_1 = Rtu.objects.get(title=row[1], code=code_1)  # noqa
                    # По уровню, вышестоящему к текущему, если в БД2 такого ещё нет  # noqa
                    if not CustPlace.objects.filter(title=row[1], code=code_1).exists():  # noqa
                        curr_rtu_2 = CustPlace.objects.create(title=row[1], code=code_1, level=1, upper_id=None)  # noqa
                    else:
                        curr_rtu_2 = CustPlace.objects.get(title=row[1], code=code_1)  # noqa
                    # По текущему уровню, если в БД1 такой еще нет
                    f1 = f2 = False
                    if not CustPost.objects.filter(title=row[3], code=code_3, level=3, upper_id=curr_rtu_1, upper_level='1').exists():  # noqa
                        f1 = True
                        curr_1 = CustPost.objects.create(title=row[3], code=code_3, level=3, upper_id=curr_rtu_1, upper_level='1')  # noqa
                    # По текущему уровню, если в БД2 такой еще нет
                    if not CustPlace.objects.filter(title=row[3], code=code_3).exists():  # noqa
                        f2 = True
                        curr_2 = CustPlace.objects.create(title=row[3], code=code_3, level=3, upper_id=curr_rtu_2)  # noqa
                    if f1 and f2:
                        return (1, curr_1, curr_2)
                    else:
                        return FAIL
                #  Случай 4.
                if code_1 is not None and code_2 is not None:
                    # По уровню, самому вышестоящему к текущему, если в БД1 такого ещё нет  # noqa
                    if not Rtu.objects.filter(title=row[1], code=code_1).exists():  # noqa
                        curr_rtu_1 = Rtu.objects.create(title=row[1], code=code_1, level=1)  # noqa
                    else:
                        curr_rtu_1 = Rtu.objects.get(title=row[1], code=code_1)  # noqa
                    # По уровню, самому вышестоящему к текущему, если в БД2 такого ещё нет  # noqa
                    if not CustPlace.objects.filter(title=row[1], code=code_1).exists():  # noqa
                        curr_rtu_2 = CustPlace.objects.create(title=row[1], code=code_1, level=1, upper_id=None)  # noqa
                    else:
                        curr_rtu_2 = CustPlace.objects.get(title=row[1], code=code_1)  # noqa
                    # По уровню, вышестоящему к текущему, если в БД1 такого ещё нет  # noqa
                    if not CustHouse.objects.filter(title=row[2], code=code_2).exists():  # noqa
                        curr_ch_1 = CustHouse.objects.create(title=row[2], code=code_2, level=1, upper_id=curr_rtu_1, upper_level='1')  # noqa
                    else:
                        curr_ch_1 = CustHouse.objects.get(title=row[2], code=code_2)  # noqa
                    # По уровню, вышестоящему к текущему, если в БД2 такого ещё нет  # noqa
                    if not CustPlace.objects.filter(title=row[2], code=code_2).exists():  # noqa
                        curr_ch_2 = CustPlace.objects.create(title=row[2], code=code_2, level=2, upper_id=curr_rtu_1)  # noqa
                    else:
                        curr_ch_2 = CustPlace.objects.get(title=row[2], code=code_2)  # noqa
                    # По текущему уровню, если в БД1 такой еще нет
                    f1 = f2 = False
                    if not CustPost.objects.filter(title=row[3], code=code_3, level=3, upper_id=curr_ch_1, upper_level='2').exists():  # noqa
                        f1 = True
                        curr_1 = CustPost.objects.create(title=row[3], code=code_3, level=3, upper_id=curr_ch_1, upper_level='2')  # noqa
                    # По текущему уровню, если в БД2 такой еще нет
                    if not CustPlace.objects.filter(title=row[3], code=code_3).exists():  # noqa
                        f2 = True
                        curr_2 = CustPlace.objects.create(title=row[3], code=code_3, level=3, upper_id=curr_ch_2)  # noqa
                    if f1 and f2:
                        return (1, curr_1, curr_2)
                    else:
                        return FAIL

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
                # print(f'Главный цикл. Строка \'{i[0]}\', обработка поля уровня \'{1}\', равного \'{i[1]}\'')  # noqa
                field_processing(clean_data_second, i, 1)

            # обработка названия таможни, если есть
            if i[2] != '':
                # print(f'Главный цикл. Строка \'{i[0]}\', обработка поля уровня \'{2}\', равного \'{i[2]}\'')  # noqa
                field_processing(clean_data_second, i, 2)

            # обработка названия т.поста, если есть
            if i[3] != '':
                # print(f'Главный цикл. Строка \'{i[0]}\', обработка поля уровня \'{3}\', равного \'{i[3]}\'')  # noqa
                field_processing(clean_data_second, i, 3)

            # if i[0] == '1':
            #     sys.exit()
