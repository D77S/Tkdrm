"""."""
import math
import os
import sys
from typing import Union

import pandas  # type: ignore
from core.models import (CustHouse, CustPlace2, CustPost, Device,
                         LocationOfUse,  Ppr, Mmpo, Oez, Ztk, Rtu,
                         SourceTypes, CustPlace1Acc, CustPlace1Use,
                         CustPlaceToLocation, RelToDev, DevTypes,
                         DevCats)
from django.core.management.base import BaseCommand
from django.db import models
from tqdm import tqdm  # type: ignore

from core.constants import (
    PATTERN1,
    PATTERN2,
    PATTERN3,
    STANDALONE_CODES,
    SOURCE_TITLES,
    # CUSTCHOICES,
    PPTYPESCHOICES,
    # SERIAL_NUM_CHOICES
)


class Command(BaseCommand):
    """."""

    def handle(self, *args, **options):
        """."""

        def replace_to_clean(source: str, pattern: dict):
            """."""
            if source in pattern.keys():
                to_out = pattern.get(source)
            else:
                to_out = source
            return to_out

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

        def get_or_create_pp(row):
            """."""
            country = row[1] if row[1] != '' else None
            pptype = [i for i, item in enumerate(PPTYPESCHOICES, start=1) if item[1] == row[2]][0]  # noqa
            return Ppr.objects.get_or_create(
                pptype=pptype,
                title=row[0],
                tow_country=country
            )[0]

        def get_or_create_mmpo_oez_ztk(model: models.Model, row):
            """."""
            try:
                return model.objects.get(title=row[0])
            except Exception:
                return model.objects.create(title=row[0])

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
                    curr_rtu_1, _ = Rtu.objects.get_or_create(
                        title='ТНП',
                        code=None
                    )
                    curr_rtu_2, _ = CustPlace2.objects.get_or_create(
                        title='ТНП',
                        code=None,
                        level=1,
                        upper_id=None,
                    )
                if codes[1] is not None:
                    curr_rtu_1, _ = Rtu.objects.get_or_create(
                        title=row[1],
                        code=codes[1]
                    )
                    curr_rtu_2, _ = CustPlace2.objects.get_or_create(
                        title=row[1],
                        code=codes[1],
                        level=1,
                        upper_id=None,
                    )
                return (curr_rtu_1, curr_rtu_1, curr_rtu_2, curr_rtu_2)

            # Если анализируется объект уровня 2 (таможня)
            if f_number == 2:
                # print(f'field_processing: обработка поля уровня \'{f_number}\', значения \'{row[f_number]}\', с кодом \'{codes[f_number]}\'')  # noqa
                # Надо обработать два случая:
                # 1. codes[1] is None,     codes[2] id not None (таможня ТНП)
                # 2. codes[1] is not None, codes[2] is not None (таможня не ТНП)  # noqa
                if codes[1] is None:
                    curr_rtu_1, _ = Rtu.objects.get_or_create(title='ТНП')
                    curr_rtu_2, _ = CustPlace2.objects.get_or_create(
                        title='ТНП',
                        code=None,
                        level=1,
                        upper_id=None,
                    )
                    curr_ch_1, _ = CustHouse.objects.get_or_create(
                        title=row[2],
                        code=codes[2],
                        upper_id=curr_rtu_1
                    )
                    curr_ch_2, _ = CustPlace2.objects.get_or_create(
                        title=row[2],
                        code=codes[2],
                        level=2,
                        upper_id=curr_rtu_2,
                    )
                # Случай 2.
                if codes[1] is not None:
                    curr_rtu_1, _ = Rtu.objects.get_or_create(code=codes[1])
                    curr_rtu_2, _ = CustPlace2.objects.get_or_create(
                        title=row[1],
                        code=codes[1],
                        level=1,
                    )
                    curr_ch_1, _ = CustHouse.objects.get_or_create(
                        title=row[2],
                        code=codes[2],
                        upper_id=curr_rtu_1
                    )
                    curr_ch_2, _ = CustPlace2.objects.get_or_create(
                        title=row[2],
                        code=codes[2],
                        level=2,
                        upper_id=curr_rtu_2,
                    )
                return (curr_ch_1, curr_ch_1, curr_ch_2, curr_ch_2)

            if f_number == 3:
                # print(f'field_processing: обработка поля уровня \'{f_number}\', значения \'{row[f_number]}\', с кодом \'{code_3}\'')  # noqa
                # Надо обработать четыре случая:
                # 1. codes[1] is None,     codes[2] is None,     codes[3] is not None (пост ТНП)  # noqa
                # 2. codes[1] is None,     codes[2] is not None, codes[3] is not None (пост таможни ТНП)  # noqa
                # 3. codes[1] is not None, codes[2] is None,     codes[3] is not None (пост РТУ)  # noqa
                # 4. codes[1] is not None, codes[2] is not None, codes[3] is not None (пост таможни РТУ)  # noqa
                if codes[1] is None:
                    curr_rtu_1, _ = Rtu.objects.get_or_create(title='ТНП')
                    curr_rtu_2, _ = CustPlace2.objects.get_or_create(
                        title='ТНП',
                        code=None,
                        level=1,
                        upper_id=None,
                    )
                else:
                    curr_rtu_1, _ = Rtu.objects.get_or_create(
                        title=row[1],
                        code=codes[1]
                    )
                    curr_rtu_2, _ = CustPlace2.objects.get_or_create(
                        title=row[1],
                        code=codes[1],
                        level=1,
                        upper_id=None,
                    )

                if codes[2] is None:
                    curr_ch_1, _ = CustHouse.objects.get_or_create(
                        title='ТНП',
                        upper_id=curr_rtu_1,
                    )
                    curr_ch_2, _ = CustPlace2.objects.get_or_create(
                        title='ТНП',
                        level=2,
                        upper_id=curr_rtu_2,
                    )
                else:
                    curr_ch_1, _ = CustHouse.objects.get_or_create(
                        title=row[2],
                        code=codes[2],
                        upper_id=curr_rtu_1
                    )
                    curr_ch_2, _ = CustPlace2.objects.get_or_create(
                        title=row[2],
                        code=codes[2],
                        level=2,
                        upper_id=curr_rtu_2,
                    )

                curr_post_1, _ = CustPost.objects.get_or_create(
                    title=row[3],
                    code=codes[3],
                    upper_id=curr_ch_1
                )
                curr_post_2, _ = CustPlace2.objects.get_or_create(
                    title=row[3],
                    code=codes[3],
                    level=3,
                    upper_id=curr_ch_2,
                )

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
            if temp_row[2] not in ['АПП', 'ВПП', 'ЖДПП', 'МПП', 'ММПО', 'ОЭЗ', 'ЗТК', 'ППП', 'РПП', 'СПП']:  # noqa
                print(f'Строка {row[0]}, \'тип п/п\' не из валидных вариантов, строка не будет обработана.')  # noqa
                return None
            if temp_row[2] in ['ВПП', 'МПП', 'ММПО', 'ОЭЗ', 'ЗТК'] and temp_row[1] != '':  # noqa
                print(f'Строка {row[0]}, невалидное сочетание столбцов \'тип п/п\' и \'сопредельное гос-во\', строка не будет обработана.')  # noqa
                return None
            if temp_row[2] in ['АПП', 'ЖДПП', 'ППП', 'РПП', 'СПП'] and temp_row[1] == '':  # noqa
                print(f'Строка {row[0]}, невалидное сочетание столбцов \'тип п/п\' и \'сопредельное гос-во\', строка не будет обработана.')  # noqa
                return None
            # Сочетание полей валидно.
            if temp_row[2] in ['АПП', 'ВПП', 'ЖДПП', 'МПП', 'ППП', 'РПП', 'СПП']:  # noqa
                return get_or_create_pp(temp_row)
            if temp_row[2] == 'ММПО':
                return get_or_create_mmpo_oez_ztk(model=Mmpo, row=temp_row)
            if temp_row[2] == 'ОЭЗ':
                return get_or_create_mmpo_oez_ztk(model=Oez, row=temp_row)
            if temp_row[2] == 'ЗТК':
                return get_or_create_mmpo_oez_ztk(model=Ztk, row=temp_row)
            return None

        def get_curr_cust_place(i, data):
            curr_cust_place = None
            if i[1] != '':
                # print(f'Обработка поля номер 1, равного \'{i[1]}\'')  # noqa
                temp_cust_place = field_processing_1(data, i, 1)  # noqa
                if temp_cust_place != [] and temp_cust_place is not None:
                    curr_cust_place = temp_cust_place
            if i[2] != '':
                # print(f'Обработка поля номер 2, равного \'{i[2]}\'')  # noqa
                temp_cust_place = field_processing_1(data, i, 2)  # noqa
                if temp_cust_place != [] and temp_cust_place is not None:
                    curr_cust_place = temp_cust_place
            if i[3] != '':
                # print(f'Обработка поля номер 3, равного \'{i[3]}\'')  # noqa
                temp_cust_place = field_processing_1(data, i, 3)  # noqa
                if temp_cust_place != [] and temp_cust_place is not None:
                    curr_cust_place = temp_cust_place
            return curr_cust_place

        def get_curr_pl_1_acc(curr_cust_place):
            curr_pl_1_acc = None
            if isinstance(curr_cust_place[1], Rtu):
                curr_pl_1_acc = CustPlace1Acc.objects.get(rtu=curr_cust_place[1])  # noqa
            if isinstance(curr_cust_place[1], CustHouse):
                curr_pl_1_acc = CustPlace1Acc.objects.get(custhouse=curr_cust_place[1])  # noqa
            if isinstance(curr_cust_place[1], CustPost):
                curr_pl_1_acc = CustPlace1Acc.objects.get(custpost=curr_cust_place[1])  # noqa
            return curr_pl_1_acc

        def get_curr_pl_1_use(curr_cust_place):
            curr_pl_1_use = None
            if isinstance(curr_cust_place[0], Rtu):
                curr_pl_1_use = CustPlace1Use.objects.get(rtu=curr_cust_place[0])  # noqa
            if isinstance(curr_cust_place[0], CustHouse):
                curr_pl_1_use = CustPlace1Use.objects.get(custhouse=curr_cust_place[0])  # noqa
            if isinstance(curr_cust_place[0], CustPost):
                curr_pl_1_use = CustPlace1Use.objects.get(custpost=curr_cust_place[0])  # noqa
            return curr_pl_1_use

        def get_curr_loc_use(curr_site):
            curr_loc_use = None
            if isinstance(curr_site, Ppr):
                curr_loc_use = LocationOfUse.objects.get(ppr=curr_site)
            if isinstance(curr_site, Mmpo):
                curr_loc_use = LocationOfUse.objects.get(mmpo=curr_site)
            if isinstance(curr_site, Oez):
                curr_loc_use = LocationOfUse.objects.get(oez=curr_site)
            if isinstance(curr_site, Ztk):
                curr_loc_use = LocationOfUse.objects.get(ztk=curr_site)
            return curr_loc_use

        def bd_some_flags_update(curr_cust_place: tuple[Union[Rtu,
                                                              CustHouse,
                                                              CustPost,
                                                              CustPlace2]]):
            for i in curr_cust_place:
                if i.code in STANDALONE_CODES and i.standalone_allowed is False:  # noqa
                    i.standalone_allowed = True
                    i.save()
            return curr_cust_place

        def get_curr_dev(curr_row, curr_pl_1_acc, curr_pl_2_acc):
            """."""
            curr_subtype = curr_row[13] if curr_row[13] != '' else None  # noqa

            try:
                curr_dev_type = DevTypes.objects.get(
                    title=curr_row[12]
                )
            except Exception:
                # print(f'строка {curr_row[0]}, названия прибора нет в БД. Не обработан.')  # noqa
                return None

            serial_field = 17 if curr_dev_type.title[:2] == 'ВН' else 16

            if curr_row[serial_field] == '' or curr_row[serial_field] == 'б/н':
                curr_serial = None
            else:
                curr_serial = curr_row[serial_field]

            curr_sour_type_temp = replace_to_clean(
                source=curr_row[14],
                pattern=PATTERN3
            )

            try:
                curr_sour_type = SourceTypes.objects.get(
                    title=curr_sour_type_temp
                )
            except Exception:
                # print(f'строка {curr_row[0]}, названия собственника нет в БД. Не обработан.')  # noqa
                return None

            if ((curr_serial is not None) and (curr_dev_type.serial_flag is False)):  # noqa
                # print(f'строка {curr_row[0]}, наличие серийного номера невалидно. Не обработан.')  # noqa
                return None

            if ((curr_serial is None) and (curr_dev_type.serial_flag is True)):
                # print(f'строка {curr_row[0]}, отсутствие серийного номера невалидно. Не обработан.')  # noqa
                return None

            if ((curr_subtype is not None) and
                (curr_dev_type.sub_types is not None) and
                    (curr_subtype not in curr_dev_type.sub_types)):
                # print(f'строка {curr_row[0]}, curr_subtype={curr_subtype}, curr_dev_type.sub_types={curr_dev_type.sub_types}')  # noqa
                # print(f'строка {curr_row[0]}, подтип прибора невалидный. Не обработан.')  # noqa
                return None

            curr_upper_id = None
            if curr_dev_type.upper_dev_flag:
                temp_dev = Device.objects.filter(
                    type__title__regex=r'Янтарь*',
                    cp1_acc=curr_pl_1_acc,
                    cp2_acc=curr_pl_2_acc,
                    serial=curr_row[16]
                )
                if temp_dev.exists():
                    curr_upper_id = temp_dev.first()

            curr_dev, _ = Device.objects.get_or_create(
                type=curr_dev_type,
                serial=curr_serial,
                cp1_acc=curr_pl_1_acc,
                cp2_acc=curr_pl_2_acc,
                sour_type=curr_sour_type,
                sub_type=curr_subtype,
                upper_id=curr_upper_id
            )

            return curr_dev

        # Main begin

        current_excel_files_list = [x for x in os.listdir() if (
            x.endswith('.xlsx') or
            x.endswith('.xls') or
            x.endswith('.xlsm')
        )]

        if len(current_excel_files_list) != 1:
            print('Эксель-файлов в текущей папке не найдено или найдено больше одного.')  # noqa
            sys.exit()

        try:
            data = pandas.read_excel(current_excel_files_list[0],
                                     skiprows=6,
                                     #  nrows=2,
                                     header=None,
                                     sheet_name='Новая база2',
                                     # usecols=range(0, 17),
                                     )
        except Exception:
            print('Ошибка формата файла.')
            sys.exit()

        clean_data_first = [['' if isinstance(j, float) and math.isnan(j) else str(j) for j in i] for i in data.values if isinstance(i[0], int)]  # noqa

        clean_data_second = []

        for row in clean_data_first:
            temp_row = []
            for i in range(0, len(row)):
                if i == 1:
                    temp_row.append(
                        replace_to_clean(
                            source=row[i],
                            pattern=PATTERN1
                        )
                    )
                elif i == 7:
                    temp_row.append(
                        replace_to_clean(
                            source=row[i],
                            pattern=PATTERN2
                        )
                    )
                else:
                    temp_row.append(row[i])
            clean_data_second.append(temp_row)

        del_flag = 't'
        while not (del_flag == 'y' or del_flag == 'n'):
            del_flag = input('Очищать таблицы в БД (y/n)?')  # noqa

        if del_flag == 'y':
            # delete
            RelToDev.objects.all().delete()
            Device.objects.all().delete()
            DevTypes.objects.all().delete()
            DevCats.objects.all().delete()
            CustPlaceToLocation.objects.all().delete()
            Ppr.objects.all().delete()
            Mmpo.objects.all().delete()
            Oez.objects.all().delete()
            Ztk.objects.all().delete()
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
            source_objs = [SourceTypes(title=i) for i in SOURCE_TITLES]
            SourceTypes.objects.bulk_create(objs=source_objs)
            dev_cats_titles = [
                'АКДРМ',
                'дозиметры',
                'поисковые',
                'радиометры-спектрометры',
                'спектрометры',
                'СИЗ'
            ]
            dev_cats_objs = [DevCats(title=i) for i in dev_cats_titles]
            DevCats.objects.bulk_create(objs=dev_cats_objs)
            dev_types = [
                ('Янтарь-1С', 'АКДРМ', True, False, None),
                ('Янтарь-1СН', 'АКДРМ', True, False, None),
                ('Янтарь-2С', 'АКДРМ', True, False, None),
                ('Янтарь-2СН', 'АКДРМ', True, False, None),
                ('ВН-СН', 'АКДРМ', None, True, None),
                ('Янтарь-1А', 'АКДРМ', True, False, None),
                ('Янтарь-2А', 'АКДРМ', True, False, None),
                ('ВН-А', 'АКДРМ', None, True, None),
                ('Янтарь-1П', 'АКДРМ', True, False, ['1П1', '1П2', '1П3', '1У', 'ПБ']),  # noqa
                ('Янтарь-2П', 'АКДРМ', True, False, ['2П1', '2П2', '2П3']),  # noqa
                ('ВН-П', 'АКДРМ', None, True, None),
                ('Янтарь-ПБ', 'АКДРМ', True, False, None),
                ('ВН-ПБ', 'АКДРМ', None, True, None),
                ('Янтарь-1Ж', 'АКДРМ', True, False, None),
                ('Янтарь-1Ж2', 'АКДРМ', True, False, None),
                ('Янтарь-2Ж', 'АКДРМ', True, False, None),
                ('Янтарь-2Ж2', 'АКДРМ', True, False, None),
                ('ВН-Ж', 'АКДРМ', None, True, None),
                ('ССД', 'АКДРМ', None, False, None),
                ('АРМ', 'АКДРМ', None, False, None),
                ('ССД/АРМ', 'АКДРМ', None, False, None),
            ]
            dev_types_objs = [DevTypes(
                title=i[0],
                category=DevCats.objects.get(title=i[1]),
                serial_flag=i[2],
                upper_dev_flag=i[3],
                sub_types=i[4]
            ) for i in dev_types]
            DevTypes.objects.bulk_create(objs=dev_types_objs)

        for i in tqdm(clean_data_second):  # noqa
        # for i in clean_data_second:  # noqa
            # if int(i[0]) < 594:
            #     continue

            # print(f'!!!!!!!!!!!!Строка номер {i[0]}!!!!!!!!!\n')

            if not pre_valid_tests(i):
                print('Не прошла валидация строки. Переход к следующей.')
                continue

            # Предварительно валидная строка
            # Обработка первых трех полей.
            curr_cust_place = get_curr_cust_place(
                i=i,
                data=clean_data_second
            )
            # Апдейт в ручном режиме некоторых флагов standalone_allowed и/или ztk_allowed  # noqa
            curr_cust_place = bd_some_flags_update(curr_cust_place)

            if curr_cust_place == [] or curr_cust_place is None:
                print(f'Строка {i[0]}, первые три поля не дали валидный т.орган, строка не будет обработана')  # noqa
                continue

            # print(f'Субъекты т.органов: 1-го типа пользования, 1-го типа баланс, 2-го типа пользователь ,2-го типа баланс={curr_cust_place}\n')  # noqa

            # Объект модели "Модель субъекта (за)баланса для объектов т.органа 1-го типа"  # noqa
            curr_pl_1_acc = get_curr_pl_1_acc(curr_cust_place)
            # print(f'Объект модели \'Модель субъекта (за)баланса для объектов т.органа 1-го типа\', CustPlace1Acc: {curr_pl_1_acc}\n')  # noqa

            # Объект модели "Модель субъекта пользования для объектов т.органа 1-го типа."  # noqa
            curr_pl_1_use = get_curr_pl_1_use(curr_cust_place)
            # print(f'Объект модели \'Модель субъекта пользования для объектов т.органа 1-го типа\', CustPlace1Use: {curr_pl_1_use}\n')  # noqa

            curr_site = field_processing_2(i)

            # print(f'Субъект пользователя (пункт пропуска, почтамт, и т.п.): {curr_site}\n')  # noqa

            curr_loc_use = get_curr_loc_use(curr_site)
            # print(f'Объект модели \'Модель субъекта пользования\', LocationOfUse={curr_loc_use}\n')  # noqa

            if i[11] != 'служебная':
                # print(f'Строка {i[0]} не содержит инф-ции о единице т.с. , переход к следующей')  # noqa
                continue

            if curr_cust_place[0].standalone_allowed is False and curr_loc_use is None:  # noqa
                print(f'Строка {i[0]}. Некорректное сочетаение флага standalone_allowed и наличия субъекта эксплуатации. Строка будет пропущена.')  # noqa
                continue
            if curr_cust_place[0].ztk_allowed is False and isinstance(curr_site, Ztk):  # noqa
                print('Некорректное сочетание флага ztk_allowed и типа субъекта эксплуатации. Строка будет пропущена.')  # noqa
                continue

            temp_cp_to_loc = CustPlaceToLocation.objects.filter(
                cust_pl1=curr_pl_1_use,
                cust_pl2=curr_cust_place[2]
            )
            if not temp_cp_to_loc.exists():
                curr_cp_to_loc = CustPlaceToLocation.objects.create(
                    cust_pl1=curr_pl_1_use,
                    cust_pl2=curr_cust_place[2],
                    loc=curr_loc_use,
                    is_main_for_cust=True
                    )
            else:
                temp2_cp_to_loc = temp_cp_to_loc.filter(loc=curr_loc_use)
                if not temp2_cp_to_loc.exists():
                    curr_cp_to_loc = CustPlaceToLocation.objects.create(
                        cust_pl1=curr_pl_1_use,
                        cust_pl2=curr_cust_place[2],
                        loc=curr_loc_use,
                        is_main_for_cust=False
                    )
                else:
                    curr_cp_to_loc = temp2_cp_to_loc.first()

            curr_dev = get_curr_dev(
                i,
                curr_pl_1_acc,
                curr_cust_place[3]
            )

            if curr_dev is None:  # noqa
                print(f'Строка {i[0]}. Прибор не распознан. Строка будет пропущена.')  # noqa
                continue

            temp_rel_to_dev = RelToDev.objects.filter(to_dev=curr_dev)  # noqa
            if not temp_rel_to_dev.exists():
                RelToDev.objects.create(
                    to_rel=curr_cp_to_loc,
                    to_dev=curr_dev,
                    is_main_for_dev=True
                )
            else:
                temp2_rel_to_dev = temp_rel_to_dev.filter(to_rel=curr_cp_to_loc)  # noqa
                if not temp2_rel_to_dev.exists():
                    RelToDev.objects.create(
                        to_rel=curr_cp_to_loc,
                        to_dev=curr_dev,
                        is_main_for_dev=False
                    )
                # else:
                #     curr_rel_to_dev = temp2_rel_to_dev.first()

            # if int(i[0]) > 6:
            #     sys.exit()
