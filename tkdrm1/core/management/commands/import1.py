"""."""
import math
import os
import sys
from tqdm import tqdm

import pandas  # type: ignore
from core.models import (
    Rtu,
    CustHouse,
    CustPost,
    CustPlace2,
    OtherTypes,
    # Owner,
    Device
)
from django.core.management.base import BaseCommand
from django.db import models


class Command(BaseCommand):
    """."""

    def handle(self, *args, **options):
        """."""

        def rtu_replace(list_in):
            """."""
            PATTERN = {  # noqa
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
            """Кодефайндер.

            Принимает список всех строк, одну (очередрую анализируемую)
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
            if len(code) > 1:
                print(f'Внимание!! code_finder: найдено кодов для поля уровня \'{f_number}\' со значением \'{row[f_number]}\' больше одного, а именно: {code}')  # noqa
                return 'found many'
            # print(f'code_finder: для поля уровня \'{f_number}\' со значением \'{row[f_number]}\' код так и не был найден')  # noqa
            return 'not found'

        def get_or_create_custom(model: models.Model, **kwargs):
            """."""
            try:
                return model.objects.get(**kwargs)
            except Exception:
                if model == Rtu:
                    new_target = model.objects.create(**kwargs)
                if model == CustHouse:
                    new_target = model.objects.create(**kwargs)
                if model == CustPost:
                    new_target = model.objects.create(**kwargs)
                return new_target

        def field_processing(array, row, f_number):
            """Филдпроцессинг.

            Обработка отдельного поля с номером f_number в строке row.
            Возврат:
            (0, 0, 0, 0, 0) - не найдено в БД и не смогло быть создано в БД.;
            (1, <объект БД1_1>, <объект БД1_2>, <объект БД2_1, <объект БД2_2>) - найдено или создано в БД.
            где объект _1 - реально найденный или созданный в БД,
            объект _2 - он же, либо принудительно повышенный до таможни, если _1 был пост.
            """
            FAIL = (0, 0, 0, 0, 0)  # noqa

            # print(f'field_processing: обработка поля уровня \'{f_number}\', значения \'{row[f_number]}\', с кодом \'{codes[f_number]}\'')  # noqa
            if row[f_number] == '':
                return FAIL

            codes = [None,]

            for i in range(1, 3 + 1):
                codes.append(code_finder(array, row, i))
                # Для всех уровней от 1 до текущего вкл-но проверка на (не None, но not found либо found many)  # noqa
                if i <= f_number and (codes[i] == 'not found' or codes[i] == 'found many'):  # noqa
                    return FAIL
            # для текущего уровня, кроме первого, проверка на None (не пуст, но не найден)  # noqa
            if f_number > 1 and codes[f_number] is None:
                return FAIL

            # Если анализируется объект уровня 1 (РТУ)
            if f_number == 1:
                # print(f'field_processing: обработка поля уровня \'{f_number}\', значения \'{row[f_number]}\', с кодом \'{codes[f_number]}\'')  # noqa
                # Надо обработать два случая:
                # 1. codes[1] is None     (что-то нижестоящее ТНП)
                # 2. codes[1] is not None (РТУ)
                if codes[1] is None:
                    curr_rtu_1 = get_or_create_custom(model=Rtu, title='ТНП')
                    curr_rtu_2 = CustPlace2.objects.get_or_create(title='ТНП')
                if codes[1] is not None:
                    curr_rtu_1 = get_or_create_custom(model=Rtu, title=row[1], code=codes[1])  # noqa
                    curr_rtu_2, _ = CustPlace2.objects.get_or_create(title=row[1], code=codes[1], level=1)  # noqa
                return (1, curr_rtu_1, curr_rtu_1, curr_rtu_2, curr_rtu_2)

            # Если анализируется объект уровня 2 (таможня)
            if f_number == 2:
                # print(f'field_processing: обработка поля уровня \'{f_number}\', значения \'{row[f_number]}\', с кодом \'{codes[f_number]}\'')  # noqa
                # Надо обработать два случая:
                # 1. codes[1] is None,     codes[2] id not None (таможня ТНП)
                # 2. codes[1] is not None, codes[2] is not None (таможня не ТНП)  # noqa
                if codes[1] is None:
                    curr_rtu_1 = get_or_create_custom(model=Rtu, title='ТНП')  # noqa
                    curr_rtu_2, _ = CustPlace2.objects.get_or_create(title='ТНП', level=1)  # noqa
                    curr_ch_1 = get_or_create_custom(model=CustHouse, title=row[2], code=codes[2], upper_id=curr_rtu_1)  # noqa
                    curr_ch_2, _ = CustPlace2.objects.get_or_create(title=row[2], code=codes[2], level=2, upper_id=curr_rtu_2)  # noqa
                # Случай 2.
                if codes[1] is not None:
                    curr_rtu_1 = get_or_create_custom(model=Rtu, code=codes[1])
                    curr_rtu_2, _ = CustPlace2.objects.get_or_create(title=row[1], code=codes[1], level=1)  # noqa
                    curr_ch_1 = get_or_create_custom(model=CustHouse, title=row[2], code=codes[2], upper_id=curr_rtu_1)  # noqa
                    curr_ch_2, _ = CustPlace2.objects.get_or_create(title=row[2], code=codes[2], level=2, upper_id=curr_rtu_2)  # noqa
                return (1, curr_ch_1, curr_ch_1, curr_ch_2, curr_ch_2)

            if f_number == 3:
                # print(f'field_processing: обработка поля уровня \'{f_number}\', значения \'{row[f_number]}\', с кодом \'{code_3}\'')  # noqa
                # Надо обработать четыре случая:
                # 1. codes[1] is None,     codes[2] is None,     codes[3] is not None (пост ТНП)  # noqa
                # 2. codes[1] is None,     codes[2] is not None, codes[3] is not None (пост таможни ТНП)  # noqa
                # 3. codes[1] is not None, codes[2] is None,     codes[3] is not None (пост РТУ)  # noqa
                # 4. codes[1] is not None, codes[2] is not None, codes[3] is not None (пост таможни РТУ)  # noqa
                # Честно: оптимизировать дальше лень.
                # Случай 1.
                if codes[1] is None and codes[2] is None:
                    curr_rtu_1 = get_or_create_custom(model=Rtu, title='ТНП')  # noqa
                    curr_rtu_2, _ = CustPlace2.objects.get_or_create(title='ТНП', level=1)  # noqa
                    curr_ch_1 = get_or_create_custom(model=CustHouse, title='ТНП')  # noqa
                    curr_ch_2, _ = CustPlace2.objects.get_or_create(title='ТНП', level=2)  # noqa
                    curr_post_1 = get_or_create_custom(model=CustPost, title=row[3], code=codes[3], upper_id=curr_ch_1)  # noqa
                    curr_post_2 = CustPlace2.objects.get_or_create(title=row[3], code=codes[3], level=3, upper_id=curr_ch_2)  # noqa
                # Случай 2.
                if codes[1] is None and codes[2] is not None:
                    curr_rtu_1 = get_or_create_custom(model=Rtu, title='ТНП')  # noqa
                    curr_rtu_2, _ = CustPlace2.objects.get_or_create(title='ТНП', level=1)  # noqa
                    curr_ch_1 = get_or_create_custom(model=CustHouse, title=row[2], code=codes[2], upper_id=curr_rtu_1)  # noqa
                    curr_ch_2, _ = CustPlace2.objects.get_or_create(title=row[2], code=codes[2], level=2, upper_id=curr_rtu_2)  # noqa
                    curr_post_1 = get_or_create_custom(model=CustPost, title=row[3], code=codes[3], upper_id=curr_ch_1)  # noqa
                    curr_post_2, _ = CustPlace2.objects.get_or_create(title=row[3], code=codes[3], level=3, upper_id=curr_ch_2)  # noqa
                # Случай 3.
                if codes[1] is not None and codes[2] is None:
                    curr_rtu_1 = get_or_create_custom(model=Rtu, title=row[1], code=codes[1])  # noqa
                    curr_rtu_2, _ = CustPlace2.objects.get_or_create(title=row[1], code=codes[1], level=1)  # noqa
                    curr_ch_1 = get_or_create_custom(model=CustHouse, title='ТНП')  # noqa
                    curr_ch_2, _ = CustPlace2.objects.get_or_create(title='ТНП', level=2)  # noqa
                    curr_post_1 = get_or_create_custom(model=CustPost, title=row[3], code=codes[3], upper_id=curr_ch_1)  # noqa
                    curr_post_2, _ = CustPlace2.objects.get_or_create(title=row[3], code=codes[3], level=3, upper_id=curr_ch_2)  # noqa
                #  Случай 4.
                if codes[1] is not None and codes[2] is not None:
                    curr_rtu_1 = get_or_create_custom(model=Rtu, title=row[1], code=codes[1])  # noqa
                    curr_rtu_2, _ = CustPlace2.objects.get_or_create(title=row[1], code=codes[1], level=1)  # noqa
                    curr_ch_1 = get_or_create_custom(model=CustHouse, title=row[2], code=codes[2], upper_id=curr_rtu_1)  # noqa
                    curr_ch_2, _ = CustPlace2.objects.get_or_create(title=row[2], code=codes[2], level=2, upper_id=curr_rtu_2)  # noqa
                    curr_post_1 = get_or_create_custom(model=CustPost, title=row[3], code=codes[3], upper_id=curr_ch_1)  # noqa
                    curr_post_2, _ = CustPlace2.objects.get_or_create(title=row[3], code=codes[3], level=3, upper_id=curr_ch_2)  # noqa

                return (1, curr_post_1, curr_ch_1, curr_post_2, curr_ch_2)

            return FAIL

        def pre_valid_tests(row):
            """."""
            if row[7] not in ['', 'А', 'В', 'Ж', 'М', 'ММПО', 'ОЭЗ', 'П', 'Р', 'С']:  # noqa
                print(f'Строка {row[0]}, \'тип п/п\' не из валидных вариантов, строка не будет обработана.')  # noqa
                return False
            if row[8] not in ['1', '2', '3', '4']:
                print(f'Строка {row[0]}, \'тип объекта\' не из вариантов \'1\', \'2\', \'3\', \'4\', строка не будет обработана.')  # noqa
                return False
            if row[11] not in ['основная', 'служебная']:
                print(f'Строка {row[0]}, \'статус строки\' не из вариантов \'основная\', \'служебная\', строка не будет обработана')  # noqa
                return False
            if row[14] not in ['', 'Там.орган', 'Росгранстрой-договор', 'Росгранстрой-акт', 'Росгранстрой-факт.пред.',  # noqa
                'Иной владелец-договор', 'Иной владелец-акт', 'Иной владелец-факт.пред.', '?']:  # noqa
                print(f'Строка {row[0]}, \'Собственник\' не из валидных вариантов, строка не будет обработана')  # noqa
                return False
            if row[8] == '1' and (row[5] == '' or row[7] == ''):
                print(f'Строка {row[0]}, невалидное сочетание столбцов 5, 7, 8, строка не будет обработана')  # noqa
                return False
            if row[7] == 'В' and row[6] != '':
                print(f'Строка {row[0]}, невалидное сочетание столбцов 6, 7, строка не будет обработана')  # noqa
                return False
            if (not ((row[11] == 'основная' and row[8] != '1' and row[4] != '') or  # noqa
                     (row[11] == 'основная' and row[8] == '1' and row[4] == '') or  # noqa
                     (row[11] == 'служебная' and row[4] == ''))):  # noqa
                print(f'Строка {row[0]}, невалидное сочетание столбцов 4, 8 и 11, строка не будет обработана')  # noqa
                return False
            if not ((row[11] == 'служебная' and row[12] != '') or (row[11] == 'основная' and row[12] == '')):  # noqa
                print(f'Строка {row[0]}, невалидное сочетание столбцов 11 и 12, строка не будет обработана')  # noqa
                return False
            if not ((row[11] == 'служебная' and row[14] != '') or (row[11] == 'основная' and row[14] == '')):  # noqa
                print(f'Строка {row[0]}, невалидное сочетание столбцов 11 и 14, строка не будет обработана')  # noqa
                return False
            return True

        # Main begin

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
                                 # usecols=range(0, 17),
                                 )

        clean_data_first = [['' if isinstance(j, float) and math.isnan(j) else str(j) for j in i] for i in data.values if isinstance(i[0], int)]  # noqa
        clean_data_second = rtu_replace(clean_data_first)

        del_flag = 't'
        while not (del_flag == 'y' or del_flag == 'n'):
            del_flag = input('Очищать таблицы в БД (y/n)?')  # noqa

        if del_flag == 'y':
            # delete
            Device.objects.all().delete()
            CustPost.objects.all().delete()
            CustHouse.objects.all().delete()
            Rtu.objects.all().delete()
            CustPlace2.objects.all().delete()
            OtherTypes.objects.all().delete()
            # create initial
            tnp_obj_1 = Rtu.objects.create(title='ТНП', code=None)
            CustHouse.objects.create(title='ТНП', code=None, upper_id=tnp_obj_1)  # noqa
            tnp_obj_2 = CustPlace2.objects.create(title='ТНП', code=None, level=1, upper_id=None)  # noqa
            CustPlace2.objects.create(title='ТНП', code=None, level=2, upper_id=tnp_obj_2)  # noqa
            OtherTypes.objects.create(title='Росгранстрой (по договору передачи в пользование)')  # noqa
            OtherTypes.objects.create(title='Росгранстрой (по акту передачи в пользование)')  # noqa
            OtherTypes.objects.create(title='Росгранстрой (по факту, без документа-основания)')  # noqa
            OtherTypes.objects.create(title='иной владелец (по договору передачи в пользование)')  # noqa
            OtherTypes.objects.create(title='иной владелец (по акту передачи в пользование)')  # noqa
            OtherTypes.objects.create(title='иной владелец (по факту, без документа-основания)')  # noqa

        for i in tqdm(clean_data_second):

            if not pre_valid_tests(i):
                continue

            # валидная строка
            # Обработка первых трех полей.
            # Если будет удачна (завершится кортежем (1, foo1_1, foo1_2, foo2_1, foo2_2)), то пополнится БД таможенных органов.  # noqa
            # Это будущие ссылки собственничества и пользования для "технических средств".  # noqa
            curr_cust_place = (0, 0, 0, 0, 0)
            for j in range(1, 3 + 1):
                if i[j] != '':
                    # print(f'Строка номер \'{i[0]}\', обработка поля номер \'{j}\', равного \'{i[j]}\'')  # noqa
                    temp_cust_place = field_processing(clean_data_second, i, j)
                    if temp_cust_place[0] == 1:
                        curr_cust_place = temp_cust_place
            if curr_cust_place == (0, 0, 0, 0, 0):
                print(f'Строка {i[0]}, первые три поля не дали валидный т.орган, строка не будет обработана')  # noqa
                continue

            print(curr_cust_place)

            if i[0] == '2':
                sys.exit()
