"""."""
import math
import os
import pandas
import sys
from tqdm import tqdm
from typing import Union
from django.core.management.base import BaseCommand

from core.constants import (
    PATTERN1,
    PATTERN2,
    STANDALONE_CODES,
    SOURCE_TITLES
)
from core.models import (CustHouse,
                         CustPlace2,
                         CustPost,
                         Device,
                         # LocationOfUse,
                         Ppr,
                         Mmpo,
                         Oez,
                         Ztk,
                         Rtu,
                         SourceTypes,
                         # CustPlace1Acc,
                         # CustPlace1Use,
                         CustPlaceToLocation,
                         RelToDev,
                         DevTypes,
                         DevCats)


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

        def clean_data_second(data_in: list[list[str]]):
            """."""
            data_out = []
            for row in data_in:
                temp_row = []
                for i in range(0, len(row)):
                    if i == 1:
                        temp_row.append(
                            replace_to_clean(
                                source=row[i],
                                pattern=PATTERN1
                            )
                        )
                    elif i == 4:
                        temp_row.append(
                            row[i].split('.')[0]
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
                data_out.append(temp_row)
            return data_out

        def clear_n_init():
            """."""
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
            tnp_obj_1 = Rtu.objects.create(
                title='ТНП',
                code=None
            )
            CustHouse.objects.create(
                title='ТНП',
                code=None,
                upper_id=tnp_obj_1
            )
            tnp_obj_2 = CustPlace2.objects.create(
                title='ТНП',
                code=None,
                level=1,
                upper_id=None)
            CustPlace2.objects.create(
                title='ТНП',
                code=None,
                level=2,
                upper_id=tnp_obj_2
            )
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
                ('Янтарь-1П', 'АКДРМ', True, False, [
                    '1П1',
                    '1П2',
                    '1П3',
                    '1У',
                    'ПБ'
                ]),
                ('Янтарь-2П', 'АКДРМ', True, False, [
                    '2П1',
                    '2П2',
                    '2П3'
                ]),
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

        def pre_valid_tests(row):
            """."""
            ERR_TEXT_1 = 'Строка {}, {} не из валидных вариантов {}, ' \
                         'строка не будет обработана.'
            ERR_TEXT_2 = 'Строка {}, невалидное сочетание столбцов {}, ' \
                         'строка не будет обработана.'
            if row[11] not in ['основная', 'служебная']:
                print(ERR_TEXT_1.format(
                    row[0],
                    '\'статус строки\'',
                    '\'основная\', \'служебная\'')
                )
                return False
            if row[8] not in ['1', '2', '3', '4']:
                print(ERR_TEXT_1.format(
                    row[0],
                    '\'тип объекта\'',
                    '\'1\', \'2\', \'3\', \'4\'')
                )
                return False
            if row[14] not in [
                '',
                'Там.орган',
                'Росгранстрой-договор',
                'Росгранстрой-акт',
                'Росгранстрой-факт.пред.',
                'Иной владелец-договор',
                'Иной владелец-акт',
                'Иной владелец-факт.пред.',
                '?'
            ]:
                print(ERR_TEXT_1.format(row[0], '\'Собственник\'', ''))
                return False
            if row[8] == '1' and (row[5] == '' or row[7] == ''):
                print(ERR_TEXT_2.format(row[0], '\'5\', \'7\', \'8\''))
                return False
            if (not ((
                row[11] == 'основная' and
                row[8] != '1' and
                row[4] != ''
                ) or (
                    row[11] == 'основная' and
                    row[8] == '1' and
                    row[4] == ''
                ) or (
                    row[11] == 'служебная' and
                    row[4] == ''
            ))):
                print(ERR_TEXT_2.format(row[0], '\'4\', \'8\' и \'11\''))
                return False
            if not ((
                row[11] == 'служебная' and
                row[12] != ''
                ) or (
                    row[11] == 'основная' and
                    row[12] == ''
            )):
                print(ERR_TEXT_2.format({row[0]}, '\'11\' и \'12\''))
                return False
            if not ((
                row[11] == 'служебная' and
                row[14] != ''
                ) or (
                    row[11] == 'основная' and
                    row[14] == ''
            )):
                print(ERR_TEXT_2.format({row[0]}, '\'11\' и \'14\''))
                return False
            return True

        def co_uniq_chk(data_in: list[Union[list[str], str]]) -> bool:
            """Проверка перечня там.органов на их уникальность.
            Принимает список из:
            номер_строки_исходных_данных,
            [список_названий,_даже_если_из_одного_элемента],
            код т.органа.
            Проверяет, что нет ни одного дубликата
            - ни среди [списков_названий]
            - ни среди кодов.
            """
            names_list = [item[1] for item in data_in]
            codes_list = [item[2] for item in data_in]
            counts_names_list = [names_list.count(item) for item in names_list]
            counts_codes_list = [codes_list.count(item) for item in codes_list]
            for item in zip(data_in, counts_names_list, counts_codes_list):
                if item[1] != 1:
                    print(f'Строка {item[0][0]}, \'основная\', '
                          'имя т.о.органа [если есть, то в сочетании с '
                          'вышестоящими] неуникально.')
                    return False
                if item[2] != 1:
                    print(f'Строка {item[0][0]}, \'основная\', '
                          'код т.органа неуникален.')
                    return False
            return True

        def bd_some_flags_update(data_in: tuple[
            Union[Rtu,
                  CustHouse,
                  CustPost,
                  CustPlace2]
        ]) -> tuple[Union[Rtu,
                          CustHouse,
                          CustPost,
                          CustPlace2
                          ]]:
            """."""
            data_out = []
            for item in data_in:
                if item.code in STANDALONE_CODES:
                    item.standalone_allowed = True
                    item.save()
                data_out.append(item)
            return (data_out[0], data_out[1])

        def get_or_create_rtu(
                data_in: list[Union[list[str], str]]
        ) -> tuple[Union[Rtu, CustPlace2]]:
            """."""
            curr_rtu_1, _ = Rtu.objects.get_or_create(
                title=data_in[1][0],
                code=data_in[2],
            )
            curr_rtu_1.address = data_in[3]
            curr_rtu_1.save()
            curr_rtu_2, _ = CustPlace2.objects.get_or_create(
                title=data_in[1][0],
                code=data_in[2],
                level=1,
                upper_id=None,
            )
            curr_rtu_2.address = data_in[3]
            curr_rtu_2.save()
            return bd_some_flags_update((curr_rtu_1, curr_rtu_2))

        def get_or_create_ch(
                data_in: list[Union[list[str], str]],
                upper_rtu_1: Rtu,
                upper_rtu_2: CustPlace2
        ) -> tuple[Union[CustHouse, CustPlace2]]:
            """."""
            curr_ch_1, _ = CustHouse.objects.get_or_create(
                title=data_in[1][1],
                code=data_in[2],
                upper_id=upper_rtu_1
            )
            curr_ch_1.address = data_in[3]
            curr_ch_1.save()
            curr_ch_2, _ = CustPlace2.objects.get_or_create(
                title=data_in[1][1],
                code=data_in[2],
                level=2,
                upper_id=upper_rtu_2,
            )
            curr_ch_2.address = data_in[3]
            curr_ch_2.save()
            return (bd_some_flags_update((curr_ch_1, curr_ch_2)))

        def get_rtu(
                data_in: list[Union[list[str],
                                    str]]
        ) -> tuple[Union[Rtu, CustPlace2]]:
            """."""
            if data_in[1][0] != '':
                upper_rtu_1_qs = Rtu.objects.filter(title=item[1][0])
                upper_rtu_2_qs = CustPlace2.objects.filter(
                    title=item[1][0],
                    level=1
                )
            else:
                upper_rtu_1_qs = Rtu.objects.filter(title='ТНП')
                upper_rtu_2_qs = CustPlace2.objects.filter(
                    title='ТНП',
                    level=1
                )
            if upper_rtu_1_qs.count() != 1 or upper_rtu_2_qs.count() != 1:
                return (None, None, False)
            return (upper_rtu_1_qs.first(), upper_rtu_2_qs.first(), True)

        def get_ch(
                data_in: list[Union[list[str],
                                    str]],
                upper_rtu_1: Rtu,
                upper_rtu_2: CustPlace2
        ) -> tuple[Union[CustHouse, CustPlace2]]:
            """."""
            if data_in[1][1] != '':
                upper_ch_1_qs = CustHouse.objects.filter(
                    title=item[1][1],
                    upper_id=upper_rtu_1
                )
                upper_ch_2_qs = CustPlace2.objects.filter(
                    title=item[1][1],
                    upper_id=upper_rtu_2,
                    level=2
                )
            else:
                upper_ch_1_qs = CustHouse.objects.filter(title='ТНП')
                upper_ch_2_qs = CustPlace2.objects.filter(
                    title='ТНП',
                    level=2
                )
            if upper_ch_1_qs.count() != 1 or upper_ch_2_qs.count() != 1:
                return (None, None, False)
            return (upper_ch_1_qs.first(), upper_ch_2_qs.first(), True)

        # Main begin
        current_excel_files_list = [x for x in os.listdir() if (
            x.endswith('.xlsx') or
            x.endswith('.xls') or
            x.endswith('.xlsm')
        )]

        if len(current_excel_files_list) != 1:
            print('Эксель-файлов в текущей папке не найдено или найдено больше одного.')  # noqa
            sys.exit()

        print('Excel-файл успешно найден и единственный.')

        try:
            data = pandas.read_excel(current_excel_files_list[0],
                                     skiprows=7,
                                     #  nrows=2,
                                     header=None,
                                     sheet_name='Новая база2',
                                     # usecols=range(0, 17),
                                     )
        except Exception:
            print('Ошибка формата файла.')
            sys.exit()

        data_2 = [
            [
                '' if isinstance(j, float) and math.isnan(j) else
                str(j) for j in i
                ]
            for i in data.values]

        data_3 = clean_data_second(data_2)

        del_flag = None
        while not (del_flag == 'y' or del_flag == 'n'):
            del_flag = input('Очищать таблицы в БД (y/n)?')  # noqa
        if del_flag == 'y':
            clear_n_init()

        print('Pre-valid тесты начаты.')
        for item in data_3:
            if not pre_valid_tests(item):
                print(f'Не прошла валидация строки {item[0]}!')
                sys.exit()
        print('Pre-valid тесты успешно завершены.')

        print('Начало создания/апдейта перечня РТУ.')
        rtu_pre_list = [
            [
                row[0],
                [row[1]],
                row[4],
                row[26]
            ] for row in data_3 if row[11] == 'основная' and row[8] == '4'
        ]
        if not (co_uniq_chk(rtu_pre_list)):
            print('Ошибка создания перечня РТУ по уникальности '
                  'либо названий, либо кодов, аварийный выход.')
            sys.exit()
        for item in rtu_pre_list:
            get_or_create_rtu(item)
        print('Успешное завершение создания/апдейта перечня РТУ.')

        print('Начало создания/апдейта перечня таможен.')
        ch_pre_list = [
            [
                row[0],
                [row[1], row[2]],
                row[4],
                row[26]
            ] for row in data_3 if row[11] == 'основная' and row[8] == '3'
        ]
        if not (co_uniq_chk(ch_pre_list)):
            print('Ошибка создания перечня таможен по уникальности '
                  'либо названий, либо кодов, аварийный выход.')
            sys.exit()
        for item in tqdm(ch_pre_list):
            upper_rtu_1, upper_rtu_2, flag = get_rtu(item)
            if not flag:
                print(f'Строка {item[0]}, ошибка создания перечня таможен, '
                      'на запросе вышестоящего РТУ.')
                sys.exit()
            get_or_create_ch(item, upper_rtu_1, upper_rtu_2)
        print('Успешное завершение создания/апдейта перечня таможен.')

        print('Начало создания/апдейта перечня т.постов.')
        cp_pre_list = [
            [
                row[0],
                [row[1], row[2], row[3]],
                row[4],
                row[26]
            ] for row in data_3 if row[11] == 'основная' and row[8] == '2'
        ]
        if not (co_uniq_chk(cp_pre_list)):
            print('Ошибка создания перечня т.постов по уникальности '
                  'либо названий, либо кодов, аварийный выход.')
            sys.exit()
        for item in tqdm(cp_pre_list):
            upper_rtu_1, upper_rtu_2, flag = get_rtu(item)
            if not flag:
                print(f'Строка {item[0]}, ошибка создания перечня т.постов, '
                      'на запросе вышестоящего РТУ.')
                sys.exit()
            upper_ch_1, upper_ch_2, flag = get_ch(
                item, upper_rtu_1, upper_rtu_2
            )
            if not flag:
                print(f'Строка {item[0]}, ошибка создания перечня т.постов, '
                      'на запросе вышестоящей таможни.')
                sys.exit()
            curr_cp_1, _ = CustPost.objects.get_or_create(
                title=item[1][2],
                code=item[2],
                upper_id=upper_ch_1
            )
            curr_cp_1.address = item[3]
            curr_cp_1.save()
            curr_cp_2, _ = CustPlace2.objects.get_or_create(
                title=item[1][2],
                code=item[2],
                level=2,
                upper_id=upper_ch_2,
            )
            curr_cp_2.address = item[3]
            curr_cp_2.save()
            bd_some_flags_update((curr_cp_1, curr_cp_2))
        print('Успешное завершение создания/апдейта перечня т.постов.')
