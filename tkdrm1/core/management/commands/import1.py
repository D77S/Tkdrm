"""."""
import math
import os
import sys

import pandas  # type: ignore
from core.models import (CustHouse, CustPlace2, CustPost, Device,  # Owner,
                         Ppr, Rtu, SourceTypes)
from django.core.management.base import BaseCommand
from django.db import models
from tqdm import tqdm  # type: ignore


class Command(BaseCommand):
    """."""

    def handle(self, *args, **options):
        """."""

        def replace_to_clean(list_in):
            """."""
            PATTERN1 = {  # noqa
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
            PATTERN2 = {  # noqa
                'А': 'АПП',
                'В': 'ВПП',
                'Ж': 'ЖДПП',
                'М': 'МПП',
                'П': 'ППП',
                'Р': 'РПП',
                'С': 'СПП'
            }
            list_out = []
            for i in list_in:
                data_row = i
                if data_row[1] in PATTERN1.keys():
                    data_row[1] = PATTERN1.get(data_row[1])
                if data_row[7] in PATTERN2.keys():
                    data_row[7] = PATTERN2.get(data_row[7])
                list_out.append(data_row)
            return list_out

        def code_finder(array: list[str], row, f_number):
            """Кодефайндер.

            Принимает список всех строк, одну (очередную анализируемую)
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
            # print(f'code_finder: строка \'{row}\', обработка поля уровня \'{f_number}\', ищем в массиве значение \'{row[f_number]}\'')  # noqa

            if (f_number not in [1, 2, 3]) or row[f_number] == '':
                return None
            code = []
            temp_row = row[1:f_number + 1] + ['' for i in range(0, 3 - f_number)]  # noqa

            for i in array:
                if i[11] != 'основная':
                    continue
                if i[1:4] == temp_row and (f_number + int(i[8]) == 5):
                    code.append(i[4].strip().split('.')[0])

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

        def get_or_create_pp(row):
            """."""
            country = row[1] if row[1] != '' else None
            try:
                return Ppr.objects.get(pptype=row[2], title=row[0], tow_country=country)  # noqa
            except Exception:
                return Ppr.objects.create(pptype=row[2], title=row[0], tow_country=country)  # noqa

        def field_processing_1(array, row, f_number):
            """Парсер полей строки с 1 по 3.

            Обработка отдельного поля с номером f_number в строке row.
            Возврат:
            None - не найдено в БД и не смогло быть создано в БД;
            (<объект БД1_1>, <объект БД1_2>, <объект БД2_1, <объект БД2_2>) - найдено или создано в БД.  # noqa
            где объект _1 - реально найденный или созданный в БД,
            объект _2 - он же, либо принудительно повышенный до таможни, если _1 был пост.
            """
            if row[f_number] == '':
                return None

            codes = [None,]

            for i in range(1, f_number + 1):
                codes.append(code_finder(array, row, i))
                # Для всех уровней от 1 до текущего вкл-но проверка на (не None, но not found либо found many)  # noqa
                if i <= f_number and (codes[i] == 'not found' or codes[i] == 'found many'):  # noqa
                    return None
            # для текущего уровня, кроме первого, проверка на None (не пуст, но не найден)  # noqa
            if f_number > 1 and codes[f_number] is None:
                return None

            # print(f'Парсер № 1 группы полей строки: обработка поля уровня \'{f_number}\', значения \'{row[f_number]}\', с кодом \'{codes[f_number]}\'')  # noqa

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
                return (curr_rtu_1, curr_rtu_1, curr_rtu_2, curr_rtu_2)

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
                return (curr_ch_1, curr_ch_1, curr_ch_2, curr_ch_2)

            if f_number == 3:
                # print(f'field_processing: обработка поля уровня \'{f_number}\', значения \'{row[f_number]}\', с кодом \'{code_3}\'')  # noqa
                # Надо обработать четыре случая:
                # 1. codes[1] is None,     codes[2] is None,     codes[3] is not None (пост ТНП)  # noqa
                # 2. codes[1] is None,     codes[2] is not None, codes[3] is not None (пост таможни ТНП)  # noqa
                # 3. codes[1] is not None, codes[2] is None,     codes[3] is not None (пост РТУ)  # noqa
                # 4. codes[1] is not None, codes[2] is not None, codes[3] is not None (пост таможни РТУ)  # noqa
                if codes[1] is None:
                    curr_rtu_1 = get_or_create_custom(model=Rtu, title='ТНП')  # noqa
                    curr_rtu_2, _ = CustPlace2.objects.get_or_create(title='ТНП', level=1)  # noqa
                else:
                    curr_rtu_1 = get_or_create_custom(model=Rtu, title=row[1], code=codes[1])  # noqa
                    curr_rtu_2, _ = CustPlace2.objects.get_or_create(title=row[1], code=codes[1], level=1)  # noqa

                if codes[2] is None:
                    curr_ch_1 = get_or_create_custom(model=CustHouse, title='ТНП')  # noqa
                    curr_ch_2, _ = CustPlace2.objects.get_or_create(title='ТНП', level=2)  # noqa
                else:
                    curr_ch_1 = get_or_create_custom(model=CustHouse, title=row[2], code=codes[2], upper_id=curr_rtu_1)  # noqa
                    curr_ch_2, _ = CustPlace2.objects.get_or_create(title=row[2], code=codes[2], level=2, upper_id=curr_rtu_2)  # noqa

                curr_post_1 = get_or_create_custom(model=CustPost, title=row[3], code=codes[3], upper_id=curr_ch_1)  # noqa
                curr_post_2, _ = CustPlace2.objects.get_or_create(title=row[3], code=codes[3], level=3, upper_id=curr_ch_2)  # noqa

                return (curr_post_1, curr_ch_1, curr_post_2, curr_ch_2)

            return None

        def field_processing_2(row):
            """Парсер полей строки 5-8.

            Возврат:
            None - не найдено в БД и не смогло быть создано в БД;
            <объект БД> - найдено или создано в БД.
            """
            temp_row = row[5:9]
            # print(f'Парсер № 2 группы полей строки 2. row[5:8]={temp_row}')
            if temp_row[3] != '1':
                return None
            if temp_row[2] not in ['АПП', 'ВПП', 'ЖДПП', 'МПП', 'ММПО', 'ОЭЗ', 'ППП', 'РПП', 'СПП']:  # noqa
                print(f'Строка {row[0]}, \'тип п/п\' не из валидных вариантов, строка не будет обработана.')  # noqa
                return None
            if temp_row[2] in ['ВПП', 'МПП', 'ММПО', 'ОЭЗ'] and temp_row[1] != '':  # noqa
                print(f'Строка {row[0]}, невалидное сочетание столбцов \'тип п/п\' и \'сопредельное гос-во\', строка не будет обработана.')  # noqa
                return None
            if temp_row[2] in ['АПП', 'ЖДПП', 'ППП', 'РПП', 'СПП'] and temp_row[1] == '':  # noqa
                print(f'Строка {row[0]}, невалидное сочетание столбцов \'тип п/п\' и \'сопредельное гос-во\', строка не будет обработана.')  # noqa
                return None
            # Сочетание полей валидно.
            if temp_row[2] in ['АПП', 'ВПП', 'ЖДПП', 'МПП', 'ППП', 'РПП', 'СПП']:  # noqa
                return get_or_create_pp(temp_row)
            return None

        def pre_valid_tests(row):
            """."""
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
                                 skiprows=7,
                                 #  nrows=2,
                                 header=None,
                                 sheet_name='Новая база2',
                                 # usecols=range(0, 17),
                                 )

        clean_data_first = [['' if isinstance(j, float) and math.isnan(j) else str(j) for j in i] for i in data.values if isinstance(i[0], int)]  # noqa
        clean_data_second = replace_to_clean(clean_data_first)

        del_flag = 't'
        while not (del_flag == 'y' or del_flag == 'n'):
            del_flag = input('Очищать таблицы в БД (y/n)?')  # noqa

        if del_flag == 'y':
            # delete
            Device.objects.all().delete()
            Ppr.objects.all().delete()
            CustPost.objects.all().delete()
            CustHouse.objects.all().delete()
            Rtu.objects.all().delete()
            CustPlace2.objects.all().delete()
            SourceTypes.objects.all().delete()
            # create initial
            tnp_obj_1 = Rtu.objects.create(title='ТНП', code=None)
            CustHouse.objects.create(title='ТНП', code=None, upper_id=tnp_obj_1)  # noqa
            tnp_obj_2 = CustPlace2.objects.create(title='ТНП', code=None, level=1, upper_id=None)  # noqa
            CustPlace2.objects.create(title='ТНП', code=None, level=2, upper_id=tnp_obj_2)  # noqa
            SourceTypes.objects.create(title='Росгранстрой (по договору передачи в пользование)')  # noqa
            SourceTypes.objects.create(title='Росгранстрой (по акту передачи в пользование)')  # noqa
            SourceTypes.objects.create(title='Росгранстрой (по факту, без документа-основания)')  # noqa
            SourceTypes.objects.create(title='иной владелец (по договору передачи в пользование)')  # noqa
            SourceTypes.objects.create(title='иной владелец (по акту передачи в пользование)')  # noqa
            SourceTypes.objects.create(title='иной владелец (по факту, без документа-основания)')  # noqa

        for i in tqdm(clean_data_second):  # noqa
        # for i in clean_data_second:  # noqa

            if not pre_valid_tests(i):
                continue

            # Валидная строка
            # print(f'Строка номер {i[0]}')

            # Обработка первых трех полей.
            # Намеренно повторяющийся код, для облегчения понимания логики.
            curr_cust_place = None
            if i[1] != '':
                # print(f'Обработка поля номер 1, равного \'{i[1]}\'')  # noqa
                temp_cust_place = field_processing_1(clean_data_second, i, 1)  # noqa
                if temp_cust_place is not None:
                    curr_cust_place = temp_cust_place
            if i[2] != '':
                # print(f'Обработка поля номер 2, равного \'{i[2]}\'')  # noqa
                temp_cust_place = field_processing_1(clean_data_second, i, 2)  # noqa
                if temp_cust_place is not None:
                    curr_cust_place = temp_cust_place
            if i[3] != '':
                # print(f'Обработка поля номер 3, равного \'{i[3]}\'')  # noqa
                temp_cust_place = field_processing_1(clean_data_second, i, 3)  # noqa
                if temp_cust_place is not None:
                    curr_cust_place = temp_cust_place

            if curr_cust_place is None:
                print(f'Строка {i[0]}, первые три поля не дали валидный т.орган, строка не будет обработана')  # noqa
                continue
            # По результатам обработки первых трех полей текущей строки вернулся валидный результат:  # noqa
            # кортеж четырех объектов ([0], [1], [2], [3])
            # субъект эксплуатации т.с. (реагирования на срабатывание):
            #    curr_cust_place[0], curr_cust_place[2]
            # субъект балансового учета т.с.:
            #    curr_cust_place[1], curr_cust_place[3]
            # Справочно: если row[14] == "Там. орган", то объект предоставлен РФ.  # noqa
            # Иначе - тем, кто в row[14].

            # print(curr_cust_place)
            curr_adm_place = field_processing_2(i)

            # if i[0] == '50':
            #     sys.exit()
