"""."""
import math
import os
import pandas
import re
import sys
from tqdm import tqdm
from typing import Union
from django.core.management.base import BaseCommand
from django.db.models import QuerySet

from core.constants import (
    PATTERN1,
    PATTERN2,
    PATTERN3,
    PATTERN4,
    STANDALONE_CODES,
    SOURCE_TITLES,
    SERVICE_TITLES,
    STATUS_TITLES
)
from core.models import (CustHouse,
                         CustPost,
                         Contracts,
                         DevToContrs,
                         Device,
                         LocationOfUse,
                         Ppr,
                         PprType,
                         Mmpo,
                         Oez,
                         Ztk,
                         Rtu,
                         SourceTypes,
                         ServiceTypes,
                         CustPlace1Acc,
                         CustPlace1Use,
                         CustPlaceToLocation,
                         RelToDev,
                         DevTypes,
                         StatusTypes,
                         DevCatsL2,
                         DevCatsL1)


class Command(BaseCommand):
    """."""

    def handle(self, *args, **options):
        """."""

        def get_frame() -> pandas.DataFrame:
            """."""
            current_excel_files_list = [x for x in os.listdir() if (
                x.endswith('.xlsx') or
                x.endswith('.xls') or
                x.endswith('.xlsm')
            )]
            if len(current_excel_files_list) != 1:
                print('Excel-файлов в текущей папке не найдено '
                      'или найдено больше одного.')
                sys.exit()
            print('Excel-файл успешно найден и единственный.')
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
            return data

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
                    elif (i == 4 or
                          i == 20 or
                          i == 21 or
                          i == 24
                          ):
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
            DevToContrs.objects.all().delete()
            Contracts.objects.all().delete()
            Device.objects.all().delete()
            DevTypes.objects.all().delete()
            DevCatsL2.objects.all().delete()
            DevCatsL1.objects.all().delete()
            CustPlaceToLocation.objects.all().delete()
            Ppr.objects.all().delete()
            Mmpo.objects.all().delete()
            Oez.objects.all().delete()
            Ztk.objects.all().delete()
            PprType.objects.all().delete()
            CustPost.objects.all().delete()
            CustHouse.objects.all().delete()
            Rtu.objects.all().delete()
            SourceTypes.objects.all().delete()
            StatusTypes.objects.all().delete()
            ServiceTypes.objects.all().delete()
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

            source_objs = [SourceTypes(title=i) for i in SOURCE_TITLES]
            SourceTypes.objects.bulk_create(objs=source_objs)

            service_objs = [ServiceTypes(title=i) for i in SERVICE_TITLES]
            ServiceTypes.objects.bulk_create(objs=service_objs)

            status_objs = [StatusTypes(title=i) for i in STATUS_TITLES]
            StatusTypes.objects.bulk_create(objs=status_objs)

            DevCatsL1.objects.create(title='Стационарные')
            DevCatsL1.objects.create(title='Переносные')
            dev_cats_l2_titles = [
                ['СТСО', DevCatsL1.objects.get(title='Стационарные')],
                ['ВН', DevCatsL1.objects.get(title='Стационарные')],
                ['Телеком', DevCatsL1.objects.get(title='Стационарные')],
                ['Дозиметры', DevCatsL1.objects.get(title='Переносные')],
                ['Поисковые', DevCatsL1.objects.get(title='Переносные')],
                ['Радиометры-спектрометры', DevCatsL1.objects.get(
                    title='Переносные')],
                ['Спектрометры', DevCatsL1.objects.get(title='Переносные')],
                ['СИЗ', DevCatsL1.objects.get(title='Переносные')],
            ]
            dev_cats_l2_objs = [
                DevCatsL2(title=item[0],
                          cat_l1=item[1]) for item in dev_cats_l2_titles]
            DevCatsL2.objects.bulk_create(objs=dev_cats_l2_objs)

            dev_types_titles = [
                [
                    'Янтарь-1С',  # title
                    DevCatsL2.objects.get(title='СТСО'),  # category
                    12,  # lifetime
                    True,  # serail_flag
                    False,  # upper_dev_flag
                    True,  # si_flag
                    None  # sub_types
                ],
                ['Янтарь-1СН', DevCatsL2.objects.get(title='СТСО'), 12,
                 True, False, True, None],
                ['Янтарь-2С', DevCatsL2.objects.get(title='СТСО'), 12,
                 True, False, True, None],
                ['Янтарь-2СН', DevCatsL2.objects.get(title='СТСО'), 12,
                 True, False, True, None],
                ['ВН-СН', DevCatsL2.objects.get(title='ВН'), 2,
                 None, True, False, None],
                ['Янтарь-1А', DevCatsL2.objects.get(title='СТСО'), 12,
                 True, False, True, None],
                ['Янтарь-2А', DevCatsL2.objects.get(title='СТСО'), 12,
                 True, False, True, None],
                ['ВН-А', DevCatsL2.objects.get(title='ВН'), 2,
                 None, True, False, None],
                ['Янтарь-1П', DevCatsL2.objects.get(title='СТСО'), 12,
                 True, False, True, None],
                ['Янтарь-1П1', DevCatsL2.objects.get(title='СТСО'), 12,
                 True, False, True, None],
                ['Янтарь-1П2', DevCatsL2.objects.get(title='СТСО'), 12,
                 True, False, True, None],
                ['Янтарь-1П3', DevCatsL2.objects.get(title='СТСО'), 12,
                 True, False, True, None],
                ['Янтарь-1У', DevCatsL2.objects.get(title='СТСО'), 12,
                 True, False, True, None],
                ['Янтарь-ПБ', DevCatsL2.objects.get(title='СТСО'), 12,
                 True, False, True, None],
                ['Янтарь-2П', DevCatsL2.objects.get(title='СТСО'), 12,
                 True, False, True, None],
                ['Янтарь-2П1', DevCatsL2.objects.get(title='СТСО'), 12,
                 True, False, True, None],
                ['Янтарь-2П2', DevCatsL2.objects.get(title='СТСО'), 12,
                 True, False, True, None],
                ['Янтарь-2П3', DevCatsL2.objects.get(title='СТСО'), 12,
                 True, False, True, None],
                ['ВН-П', DevCatsL2.objects.get(title='ВН'), 2,
                 None, True, False, None],
                ['ВН-ПБ', DevCatsL2.objects.get(title='ВН'), 2,
                 None, True, False, None],
                ['Янтарь-1Ж', DevCatsL2.objects.get(title='СТСО'), 12,
                 True, False, True, None],
                ['Янтарь-1Ж2', DevCatsL2.objects.get(title='СТСО'), 12,
                 True, False, True, None],
                ['Янтарь-2Ж', DevCatsL2.objects.get(title='СТСО'), 12,
                 True, False, True, None],
                ['Янтарь-2Ж2', DevCatsL2.objects.get(title='СТСО'), 12,
                 True, False, True, None],
                ['ВН-Ж', DevCatsL2.objects.get(title='ВН'), 2,
                 None, True, False, None],
                ['ССД', DevCatsL2.objects.get(title='Телеком'), 2,
                 None, False, False, None],
                ['АРМ', DevCatsL2.objects.get(title='Телеком'), 2,
                 None, False, False, None],
                ['АРМ/ССД', DevCatsL2.objects.get(title='Телеком'), 2,
                 None, False, False, None],
            ]
            dev_types_objs = [DevTypes(
                title=item[0],
                category=item[1],
                lifetime=item[2],
                serial_flag=item[3],
                upper_dev_flag=item[4],
                si_flag=item[5],
                sub_types=item[6]
            ) for item in dev_types_titles]
            DevTypes.objects.bulk_create(objs=dev_types_objs)

            ppr_types_titles = ['АПП', 'ВПП', 'ЖДПП', 'МПП',
                                'ППП', 'РПП', 'СПП']
            ppr_types_objs = [PprType(title=item) for item in ppr_types_titles]
            PprType.objects.bulk_create(objs=ppr_types_objs)

        def pre_valid_tests(row):
            """."""
            ERR_TEXT_1 = 'Строка {}, {} не из валидных вариантов {}, ' \
                         'строка не будет обработана.'
            ERR_TEXT_2 = 'Строка {}, невалидное сочетание столбцов {}, ' \
                         'строка не будет обработана.'
            if not (row[4] == '' or re.fullmatch(r'^1\d{7}$', row[4])):
                print(ERR_TEXT_1.format(row[0], '\'код\'', ''))
                return False
            if row[7] not in [
                '', 'АПП', 'ВПП', 'ЖДПП', 'МПП',
                'ППП', 'РПП', 'СПП', 'ММПО', 'ОЭЗ', 'ЗТК'
            ]:
                print(ERR_TEXT_1.format(row[0], '\'тип ПП, ММПО и т.п.\'', ''))
                return False
            if row[8] not in ['1', '2', '3', '4']:
                print(ERR_TEXT_1.format(
                    row[0],
                    '\'тип объекта\'',
                    '\'1\', \'2\', \'3\', \'4\'')
                )
                return False
            if row[11] not in ['основная', 'служебная']:
                print(ERR_TEXT_1.format(
                    row[0],
                    '\'статус строки\'',
                    '\'основная\', \'служебная\'')
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
                # '?'
            ]:
                print(ERR_TEXT_1.format(row[0], '\'Собственник\'', ''))
                return False
            if row[8] == '1' and (row[5] == '' or row[7] == ''):
                print(ERR_TEXT_2.format(row[0], '\'5\', \'7\', \'8\''))
                return False
            if row[15] not in ['', 'СИ', 'инд', 'Х.З.']:
                print(ERR_TEXT_1.format(row[0], '\'СИ/инд/Х.З.\'', ''))
                return False
            if row[18] not in [
                '',
                'используется',
                'демонтировано',
                'хран-ещё будет пока неизвестно где',
                'хран-ещё будет известно где',
                'хран-передача',
                'хран-на спис',
                'фиктивная строка',
                '?'
            ]:
                print(ERR_TEXT_1.format(row[0], '\'статус ТС\'', ''))
                return False
            if row[20] not in ['', '0', '1', '2', '3']:
                print(ERR_TEXT_1.format(
                    row[0], '\'0\', \'1\', \'2\', \'3\'', ''))
                return False
            if row[21] not in ['', '0', '1']:
                print(ERR_TEXT_1.format(row[0], '\'0\', \'1\'', ''))
                return False
            if not (row[22] in ['', '?'] or re.fullmatch(r'^\d{4}$', row[22])):
                print(ERR_TEXT_1.format(row[0], 'год выпуска', ''))
                return False
            if not (row[23] in ['', '?'] or re.fullmatch(r'^\d{4}$', row[23])):
                print(ERR_TEXT_1.format(row[0], 'год ввода', ''))
                return False
            if not (row[24] in ['', '?'] or re.fullmatch(r'^\d{4}$', row[24])):
                print(ERR_TEXT_1.format(row[0], 'год срока службы', ''))
                return False
            if (not ((
                row[11] == 'основная' and
                row[8] in ['2', '3', '4'] and
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
            if row[8] == '1' and not (row[5] != '' and row[7] in [
                '', 'АПП', 'ВПП', 'ЖДПП', 'МПП', 'ППП', 'РПП',
                'СПП', 'ММПО', 'ОЭЗ', 'ЗТК'
            ]):
                print(ERR_TEXT_2.format(row[0], '\'8\', \'7\' и \'5\''))
                return False
            if row[8] == '2' and not (row[3] != '' and row[5] == ''
                                      and row[6] == '' and row[7] == ''):
                print(ERR_TEXT_2.format(row[0], '\'8\', \'3\' и \'5-7\''))
                return False
            if row[8] == '3' and not (row[2] != '' and row[3] == '' and
                                      row[5] == '' and row[6] == '' and
                                      row[7] == ''):
                print(ERR_TEXT_2.format(row[0], '\'8\', \'2-3\' и \'5-7\''))
                return False
            if row[8] == '4' and not (row[1] != '' and row[2] == '' and
                                      row[3] == '' and row[5] == '' and
                                      row[6] == '' and row[7] == ''):
                print(ERR_TEXT_2.format(row[0], '\'8\', \'1-3\' и \'5-7\''))
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
                          'название т.о. [если есть, то в сочетании с '
                          'вышестоящими] неуникально.')
                    return False
                if item[2] != 1:
                    print(f'Строка {item[0][0]}, \'основная\', '
                          'код т.органа неуникален.')
                    return False
            return True

        def loc_uniq_chk(data_in: list[Union[list[str], str]]) -> bool:
            """."""
            names_list = [item[1] for item in data_in]
            counts_names_list = [names_list.count(item) for item in names_list]
            for item in zip(data_in, counts_names_list):
                if item[1] != 1:
                    print(f'Строка {item[0][0]}, \'основная\', '
                          'название локации в сочетании с т.о.'
                          'неуникально')
                    return False
            return True

        def bd_some_flags_update(data_in: Union[
            Rtu,
            CustHouse,
            CustPost
            ]
        ) -> Union[
            Rtu,
            CustHouse,
            CustPost
        ]:
            """Принимает объект таможенного органа.
            Проверяет, входит ли он в перечень тех, которым
            разрешено работать вне территориального
            обхъекта (пункт пропуска, ММПО, СВХ, ЗТК). Обычно это
            т.н. внутренние посты. Если входит, ему изменяется
            флаг, он сохраняется в БД и возвращается."""
            if data_in.code in STANDALONE_CODES:
                data_in.standalone_allowed = True
                data_in.save()
            return data_in

        def get_or_create_rtu(
                data_in: list[Union[list[str], str]]
        ) -> Rtu:
            """Создает или находит объект РТУ и возвращает."""
            curr_rtu_1, _ = Rtu.objects.get_or_create(
                title=data_in[1][0],
                code=data_in[2],
            )
            curr_rtu_1.address = data_in[3]
            curr_rtu_1.save()
            return bd_some_flags_update(curr_rtu_1)

        def get_or_create_ch(
                data_in: list[Union[list[str], str]],
                upper_rtu_1: Rtu
        ) -> CustHouse:
            """Создает или находит объект таможни и возвращает."""
            curr_ch_1, _ = CustHouse.objects.get_or_create(
                title=data_in[1][1],
                code=data_in[2],
                upper_id=upper_rtu_1
            )
            curr_ch_1.address = data_in[3]
            curr_ch_1.save()
            return (bd_some_flags_update(curr_ch_1))

        def get_or_create_cp(
                data_in: list[Union[list[str], str]],
                upper_ch_1: CustHouse,
        ) -> CustPost:
            """Создает или находит объект поста и возвращает."""
            curr_cp_1, _ = CustPost.objects.get_or_create(
                title=data_in[1][2],
                code=data_in[2],
                upper_id=upper_ch_1
            )
            curr_cp_1.address = data_in[3]
            curr_cp_1.save()
            return (bd_some_flags_update(curr_cp_1))

        def get_rtu(
                data_in: list[Union[list[str], str]],
                all_rtus_1: QuerySet,
        ) -> tuple[Rtu, bool]:
            """."""
            if data_in[1][0] != '':
                rtu_1_qs = all_rtus_1.filter(title=data_in[1][0])
            else:
                rtu_1_qs = all_rtus_1.filter(title='ТНП')
            if rtu_1_qs.count() != 1:
                return (None, False)
            return (rtu_1_qs.first(), True)

        def get_ch(
                data_in: list[Union[list[str],
                                    str]],
                all_ch_1: QuerySet,
                upper_rtu_1: Rtu,
        ) -> tuple[CustHouse, bool]:
            """."""
            if data_in[1][1] != '':
                ch_1_qs = all_ch_1.filter(
                    title=data_in[1][1],
                    upper_id=upper_rtu_1
                )
            else:
                ch_1_qs = all_ch_1.filter(title='ТНП')
            if ch_1_qs.count() != 1:
                return (None, False)
            return (ch_1_qs.first(), True)

        def get_cp(
                data_in: list[Union[list[str],
                                    str]],
                all_cp_1: QuerySet,
                upper_ch_1: CustHouse,
        ) -> tuple[CustPost, bool]:
            """."""
            cp_1_qs = all_cp_1.filter(
                title=data_in[1][2],
                upper_id=upper_ch_1
            )
            if cp_1_qs.count() != 1:
                return (None, False)
            return (cp_1_qs.first(), True)

        def get_curr_cust_place(
                item: list[list[str], str],
                all_rtus_1: QuerySet,
                all_ch_1: QuerySet,
                all_cp_1: QuerySet,
        ) -> Union[Rtu, CustHouse, CustPost]:
            """Определение там.органа.
            Принимает строку вида
            ['1', ['Дальневосточное таможенное управление', 'Бурятская таможня', 'Таможенный пост ДАПП Монды'], ...]  # noqa
            Также принимает полные перечни всех РТУ, таможен, постов.
            В виде кверисетов.
            Возвращает объект какого-либо из классов Rtu, CustHouse, CustPost.
            """
            curr_cust_place_1 = None
            if item[1][2] != '':
                curr_level = 3
            elif item[1][1] != '':
                curr_level = 2
            else:
                curr_level = 1
            curr_rtu_1, flag = get_rtu(
                data_in=item,
                all_rtus_1=all_rtus_1)
            if not flag:
                err_report(row=item[0],
                           reason='Ошибка получения текущего РТУ',
                           st_2='РТУ')
                return None
            curr_cust_place_1 = curr_rtu_1
            if curr_level in [2, 3]:
                curr_ch_1, flag = get_ch(
                    data_in=item,
                    all_ch_1=all_ch_1,
                    upper_rtu_1=curr_rtu_1,
                )
                if not flag:
                    err_report(row=item[0],
                               reason='Ошибка получения текущей таможни',
                               st_2='таможни')
                    return None
                if curr_ch_1.title != 'ТНП':
                    curr_cust_place_1 = curr_ch_1
            if curr_level == 3:
                curr_cp_1, flag = get_cp(
                    data_in=item,
                    all_cp_1=all_cp_1,
                    upper_ch_1=curr_ch_1,
                )
                if not flag:
                    err_report(row=item[0],
                               reason='Ошибка получения текущего поста',
                               st_2='поста')
                    return None
                curr_cust_place_1 = curr_cp_1
            return curr_cust_place_1

        def get_curr_pl_1_acc(
                curr_cpl: Union[Rtu, CustHouse, CustPost]) -> CustPlace1Acc:
            """."""
            if isinstance(curr_cpl, Rtu):
                return CustPlace1Acc.objects.get(rtu=curr_cpl)
            if isinstance(curr_cpl, CustHouse):
                return CustPlace1Acc.objects.get(custhouse=curr_cpl)
            if isinstance(curr_cpl, CustPost):
                if curr_cpl.upper_id.title == 'ТНП':
                    return CustPlace1Acc.objects.get(custpost=curr_cpl)
                return CustPlace1Acc.objects.get(custhouse=curr_cpl.upper_id)
            return None

        def get_curr_pl_1_use(
                curr_cpl: Union[Rtu, CustHouse, CustPost]) -> CustPlace1Use:
            """."""
            if isinstance(curr_cpl, Rtu):
                return CustPlace1Use.objects.get(rtu=curr_cpl)
            if isinstance(curr_cpl, CustHouse):
                return CustPlace1Use.objects.get(custhouse=curr_cpl)
            if isinstance(curr_cpl, CustPost):
                return CustPlace1Use.objects.get(custpost=curr_cpl)
            return None

        def get_curr_loc_use(
                curr_site: Union[Ppr, Mmpo, Oez, Ztk]
        ) -> LocationOfUse:
            """."""
            if isinstance(curr_site, Ppr):
                return LocationOfUse.objects.get(ppr=curr_site)
            if isinstance(curr_site, Mmpo):
                return LocationOfUse.objects.get(mmpo=curr_site)
            if isinstance(curr_site, Oez):
                return LocationOfUse.objects.get(oez=curr_site)
            if isinstance(curr_site, Ztk):
                return LocationOfUse.objects.get(ztk=curr_site)
            return None

        def get_or_cr_curr_cp_to_loc(
                curr_pl_1_use: CustPlace1Use,
                curr_cust_place_1: Union[Rtu, CustHouse, CustPost],
                curr_loc_use: LocationOfUse
        ) -> CustPlaceToLocation:
            """."""
            temp_cp_to_loc = CustPlaceToLocation.objects.filter(
                cust_pl1=curr_pl_1_use,
            )
            if not temp_cp_to_loc.exists():
                return CustPlaceToLocation.objects.create(
                    cust_pl1=curr_pl_1_use,
                    loc=curr_loc_use,
                    is_main_for_cust=True
                    )
            else:
                temp2_cp_to_loc = temp_cp_to_loc.filter(loc=curr_loc_use)
                if not temp2_cp_to_loc.exists():
                    return CustPlaceToLocation.objects.create(
                        cust_pl1=curr_pl_1_use,
                        loc=curr_loc_use,
                        is_main_for_cust=False
                    )
                return temp2_cp_to_loc.first()

        def chk_flags(
                item: list[list[str], str],
                curr_cpl: Union[Rtu, CustHouse, CustPost],
                curr_site: Union[Ppr, Mmpo, Oez, Ztk]
        ) -> bool:
            """."""
            if curr_cpl.standalone_allowed is False and curr_site is None:
                err_report(row=item[0],
                           reason='Некорректное сочетание флага '
                           'standalone_allowed и отсутствия субъекта '
                           'эксплуатации (п.п., ММПО, ОЭЗ, ЗТК).')
                return False
            if curr_cpl.ztk_allowed is False and isinstance(curr_site, Ztk):
                err_report(row=item[0],
                           reason='Некорректное сочетание флага '
                           'ztk_allowed и того, что в строке ЗТК.')
                return False
            return True

        def get_or_create_pp(row: list[Union[list[str], str]]):
            """."""
            country = row[2][1] if row[2][1] != '' else None
            pre_type = row[2][2]
            try:
                pptype = PprType.objects.get(title=pre_type)
            except Exception:
                err_report(row=item[0],
                           reason='поиска ТИПА п.п.')
                return None
            return Ppr.objects.get_or_create(
                pptype=pptype,
                title=row[2][0],
                tow_country=country
            )[0]

        def get_or_create_mmpo_oez_ztk(
                model: Union[Mmpo, Oez, Ztk],
                item: list[Union[list[str], str]]
        ):
            """."""
            try:
                return model.objects.get(title=item[2][0])
            except Exception:
                return model.objects.create(title=item[2][0])

        def get_curr_site(
                item: list[Union[list[str], str]],
                all_pprs: QuerySet,
                all_mmpos: QuerySet,
                all_oezs: QuerySet,
                all_ztks: QuerySet
        ) -> Union[Ppr, Mmpo, Ztk, Oez]:
            """Определение текущего п.п, ММПО, ОЭЗ или ЗТК.
            Принимает строку вида
            ['1', ['Дальневосточное таможенное управление', 'Бурятская таможня', 'Таможенный пост ДАПП Монды'], ['Монды', 'МНР', 'АПП']]  # noqa
            И перечни всех п.п., ММПО, ОЭЗ, ЗТК в виде кверисетов.
            Возвращает объект одного из типов:
            Ppr, Mmpo, Ztk или Oez.
            """
            if item[2][2] in ['АПП', 'ВПП', 'ЖДПП',
                              'МПП', 'ППП', 'РПП', 'СПП']:
                pptype = PprType.objects.get(title=item[2][2])
                if item[2][2] in ['АПП', 'ЖДПП', 'ППП', 'РПП', 'СПП']:
                    pprs_qs = all_pprs.filter(
                        pptype=pptype,
                        title=item[2][0],
                        tow_country=item[2][1]
                    )
                else:
                    pprs_qs = all_pprs.filter(
                        pptype=pptype,
                        title=item[2][0]
                    )
                if pprs_qs.count() != 1:
                    err_report(row=item[0],
                               reason='поиска п.п.')
                    return None
                return pprs_qs.first()
            elif item[2][2] == 'ММПО':
                mmpos_qs = all_mmpos.filter(title=item[2][0])
                if mmpos_qs.count() != 1:
                    err_report(row=item[0],
                               reason='поиска ММПО')
                    return None
                return mmpos_qs.first()
            elif item[2][2] == 'ОЭЗ':
                oezs_qs = all_oezs.filter(title=item[2][0])
                if oezs_qs.count() != 1:
                    err_report(row=item[0],
                               reason='поиска ОЭЗ')
                    return None
                return oezs_qs.first()
            elif item[2][2] == 'ЗТК':
                ztks_qs = all_ztks.filter(title=item[2][0])
                if ztks_qs.count() != 1:
                    err_report(row=item[0],
                               reason='поиска ЗТК')
                    return None
                return ztks_qs.first()
            return None

        def get_curr_dev(
                item: list[Union[list[str], str]],
                all_dev_types: QuerySet[DevTypes],
                curr_pl_1_acc: CustPlace1Acc,
                all_sour_types: QuerySet,
                all_status_types: QuerySet
        ) -> Device:
            """."""

            # Определение типа девайса
            if (item[13] != '' and
               item[13] in [
                   '1П1', '1П2', '1П3', '1У', 'ПБ', '2П1', '2П2', '2П3']):
                curr_dev_type_temp = 'Янтарь-' + item[13]
            elif item[13] != '' and item[13] == 'АРМ/ССД':
                curr_dev_type_temp = item[13]
            else:
                curr_dev_type_temp = item[12]
            try:
                curr_dev_type = all_dev_types.get(
                    title=curr_dev_type_temp
                )
            except Exception:
                err_report(row=item[0],
                           reason='поиск типа девайса')
                return None

            # определение серийного номера девайса
            serial_field = 17 if curr_dev_type.title[:2] == 'ВН' else 16
            if (item[serial_field] == '' or
               item[serial_field] == 'б/н' or
               item[serial_field] == 'б.н.'):
                curr_serial = None
            else:
                curr_serial = item[serial_field]
            if ((curr_serial is not None) and
               (curr_dev_type.serial_flag is False)):
                err_report(row=item[0],
                           reason='наличия сер.номера, а его быть не должно')
                return None
            if ((curr_serial is None) and
               (curr_dev_type.serial_flag is True)):
                err_report(row=item[0],
                           reason='отсутствие сер.номера, а он должен быть')
                return None

            # определение собственника девайса
            curr_sour_type_temp = replace_to_clean(source=item[14],
                                                   pattern=PATTERN3)
            try:
                curr_sour_type = all_sour_types.get(
                    title=curr_sour_type_temp
                )
            except Exception:
                err_report(row=item[0],
                           reason='названия собственника нет в БД')
                return None

            # определение статуса тех.средства по использованию
            curr_status_use_temp = replace_to_clean(source=item[18],
                                                    pattern=PATTERN4)

            try:
                curr_status_use = all_status_types.get(
                    title=curr_status_use_temp
                )
            except Exception:
                err_report(row=item[0],
                           reason='статуса по эксплуатации т.с. нет в БД')
                return None

            # curr_subtype = ???
            # if ((curr_subtype is not None) and
            #     (curr_dev_type.sub_types is not None) and
            #         (curr_subtype not in curr_dev_type.sub_types)):
            #     err_report(row=item[0],
            #                reason='невалидный подтип девайса')
            #     return None

            # определение вышестоящего девайса
            if curr_dev_type.upper_dev_flag:
                temp_dev = Device.objects.filter(
                    type__title__regex=r'Янтарь*',
                    cp1_acc=curr_pl_1_acc,
                    serial=item[16]
                )
                if temp_dev.exists():
                    curr_upper_id = temp_dev.first()
                else:
                    curr_upper_id = None
            else:
                curr_upper_id = None

            # определение принадлежности девайса к СИ
            if curr_dev_type.si_flag is False:
                curr_is_si = None
            elif item[15] == '':
                curr_is_si = None
            elif item[15] == 'СИ':
                curr_is_si = True
            elif item[15] == 'инд':
                curr_is_si = False
            else:
                err_report(row=item[0],
                           reason='поиска типа СИ',
                           st_2='литерала, который таков:' + item[15])
                return None

            # определение флага включения ТС в ГК
            curr_serv_flag = item[20]
            if curr_serv_flag not in ['0', '1', '2', '3']:
                err_report(row=item[0],
                           reason='парсинга флага включения в ГК',
                           st_2=curr_serv_flag)
                return None
            serv_types_list = [item.pk for item in ServiceTypes.objects.all().order_by('id')]  # noqa
            curr_serv_type = ServiceTypes.objects.get(pk=serv_types_list[int(curr_serv_flag)])  # noqa

            # загрузка примечаний к девайсу
            note1 = item[9] if item[9] != '' else None
            note2 = item[10] if item[10] != '' else None
            note3 = item[19] if item[19] != '' else None

            # создание девайса
            temp_f = None
            if curr_dev_type.serial_flag is False:
                curr_dev = Device.objects.create(
                    type=curr_dev_type,
                    serial=None,
                    cp1_acc=curr_pl_1_acc,
                    sour_type=curr_sour_type,
                    status_use=curr_status_use,
                    # sub_type=curr_subtype,
                    upper_id=curr_upper_id,
                    service_type=curr_serv_type
                )
            elif curr_dev_type.serial_flag is None and curr_serial is None:
                curr_dev = Device.objects.create(
                    type=curr_dev_type,
                    serial=curr_serial,
                    cp1_acc=curr_pl_1_acc,
                    sour_type=curr_sour_type,
                    status_use=curr_status_use,
                    # sub_type=curr_subtype,
                    upper_id=curr_upper_id,
                    service_type=curr_serv_type
                )
            else:
                curr_dev, temp_f = Device.objects.get_or_create(
                    type=curr_dev_type,
                    serial=curr_serial,
                    cp1_acc=curr_pl_1_acc,
                    sour_type=curr_sour_type,
                    status_use=curr_status_use,
                    # sub_type=curr_subtype,
                    upper_id=curr_upper_id,
                    service_type=curr_serv_type
                )
            curr_dev.note1 = note1
            curr_dev.note2 = note2
            curr_dev.note3 = note3
            curr_dev.is_si = curr_is_si
            # if curr_gk_flag == '0':
            #     curr_dev.gk_flag = 'Ни тех.обслуживания, ни ремонта'
            # elif curr_gk_flag == '1':
            #     curr_dev.gk_flag = 'И тех.обслуживание, и ремонт'
            # elif curr_gk_flag == '2':
            #     curr_dev.gk_flag = 'Только тех.обслуживание'
            # elif curr_gk_flag == '3':
            #     curr_dev.gk_flag = 'Только ремонт'
            curr_dev.save()
            if temp_f is False:
                print(f'Строка {item[0]}, девайс был не создан, а ретривен.')
            return curr_dev

        def get_or_cr_curr_reltodev(
                to_rel: CustPlaceToLocation,
                to_dev: Device
        ) -> RelToDev:
            """."""
            temp_rel_to_dev = RelToDev.objects.filter(to_dev=to_dev)
            if not temp_rel_to_dev.exists():
                return RelToDev.objects.create(
                    to_rel=to_rel,
                    to_dev=to_dev,
                    is_main_for_dev=True
                )
            else:
                temp2_rel_to_dev = temp_rel_to_dev.filter(to_rel=to_rel)
                if not temp2_rel_to_dev.exists():
                    return RelToDev.objects.create(
                        to_rel=to_rel,
                        to_dev=to_dev,
                        is_main_for_dev=False
                    )
                return temp2_rel_to_dev.first()

        def err_report(
                row: str = None,
                reason: str = None,
                st_1: str = None,
                st_2: str = None):
            """."""
            row_lit = f'Строка {row}. ' if row else ''
            reason_lit = f'Ошибка {reason}. ' if reason else ''
            stage_lit_1 = f'При создании перечня {st_1}. ' if st_1 else ''
            stage_lit_2 = f'На этапе запроса {st_2}.' if st_2 else ''
            print(f'{row_lit}{reason_lit}{stage_lit_1}{stage_lit_2}')

        # Main begin
        data = get_frame()
        data_2 = [
            [
                '' if isinstance(j, float) and math.isnan(j) else
                str(j) for j in i
                ]
            for i in data.values]
        data_3 = clean_data_second(data_2)

        del_flag = None
        while not (del_flag == 'y' or del_flag == 'n'):
            del_flag = input('Очищать таблицы в БД (y/n)?')
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
            err_report(reason='уникальности имён либо кодов', st_1='РТУ')
            sys.exit()
        ##########
        for item in rtu_pre_list:
            get_or_create_rtu(item)
        all_rtus_1 = Rtu.objects.all()
        print('Успешное завершение создания/апдейта перечня РТУ.')

        print('Начало создания/апдейта перечня таможен.')
        ch_pre_list = [
            [row[0],
             [row[1], row[2]],
             row[4],
             row[26]]
            for row in data_3 if row[11] == 'основная' and row[8] == '3'
        ]
        if not (co_uniq_chk(ch_pre_list)):
            err_report(reason='уникальности имён либо кодов', st_1='таможен')
            sys.exit()
        ##########
        for item in tqdm(ch_pre_list):
            upp_rtu_1, flag = get_rtu(item, all_rtus_1)
            if not flag:
                err_report(row=item[0], reason=' ', st_1='таможен', st_2='РТУ')
                continue
            get_or_create_ch(item, upp_rtu_1)
        all_ch_1 = CustHouse.objects.all()
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
            err_report(reason='уникальности имён либо кодов', st_1='т.постов')
            sys.exit()
        ##########
        for item in tqdm(cp_pre_list):
            upper_rtu_1, flag = get_rtu(
                data_in=item,
                all_rtus_1=all_rtus_1)
            if not flag:
                err_report(row=item[0], reason=' ', st_1='постов', st_2='РТУ')
                continue
            upper_ch_1, flag = get_ch(
                data_in=item,
                all_ch_1=all_ch_1,
                upper_rtu_1=upper_rtu_1
            )
            if not flag:
                err_report(row=item[0], reason=' ', st_1='постов', st_2='т-н')
                continue
            get_or_create_cp(item, upper_ch_1)
            all_cp_1 = CustPost.objects.all()
        print('Успешное завершение создания/апдейта перечня т.постов.')

        print('Начало создания/апдейта перечня пунктов пропуска, '
              'ММПО, ОЭЗ, ЗТК.')
        sites_pre_list = [
            [row[0],
             [row[1], row[2], row[3]],
             [row[5], row[6], row[7]]]
            for row in data_3 if (
                row[11] == 'основная' and
                row[8] == '1' and
                row[7] in ['АПП', 'ВПП', 'ЖДПП', 'МПП', 'ППП',
                           'РПП', 'СПП', 'ММПО', 'ОЭЗ', 'ЗТК']
                )
        ]
        pp_pre_list = [[
            row[0],
            [row[1][0], row[1][1], row[1][2], row[2][0], row[2][1], row[2][2]]
        ] for row in sites_pre_list if row[2][2] in [
            'АПП', 'ВПП', 'ЖДПП', 'МПП', 'ППП', 'РПП', 'СПП']]
        mmpo_pre_list = [[
            row[0],
            [row[1][0], row[1][1], row[1][2], row[2][0], row[2][1]]
        ] for row in sites_pre_list if row[2][1] == 'ММПО']
        oez_pre_list = [[
            row[0],
            [row[1][0], row[1][1], row[1][2], row[2][0], row[2][1]]
        ] for row in sites_pre_list if row[2][1] == 'ОЭЗ']
        ztk_pre_list = [[
            row[0],
            [row[1][0], row[1][1], row[1][2], row[2][0], row[2][1]]
        ] for row in sites_pre_list if row[2][1] == 'ЗТК']
        if not (loc_uniq_chk(pp_pre_list)):
            err_report(reason='уникальности имён пунктов пропуска в сочетании '
                       'с именами т.органа', st_1='п.пропуска')
            sys.exit()
        if not (loc_uniq_chk(mmpo_pre_list)):
            err_report(reason='уникальности имён ММПО в сочетании '
                       'с именами т.органа', st_1='ММПО')
            sys.exit()
        if not (loc_uniq_chk(oez_pre_list)):
            err_report(reason='уникальности имён ОЭЗ в сочетании '
                       'с именами т.органа', st_1='ОЭЗ')
            sys.exit()
        if not (loc_uniq_chk(ztk_pre_list)):
            err_report(reason='уникальности имён ЗТК в сочетании '
                       'с именами т.органа', st_1='ЗТК')
            sys.exit()
        ##########
        for item in tqdm(sites_pre_list):
            curr_cust_place_1 = get_curr_cust_place(
                item=item,
                all_rtus_1=all_rtus_1,
                all_ch_1=all_ch_1,
                all_cp_1=all_cp_1
            )
            ##########
            if not curr_cust_place_1:
                err_report(row=item[0],
                           reason='определения текущего т.органа',
                           st_1='п.пропуска, ММПО, ОЭЗ, ЗТК')
                continue
            ##########
            curr_pl_1_acc = get_curr_pl_1_acc(curr_cust_place_1)
            if not curr_pl_1_acc:
                err_report(row=item[0], reason='определения '
                           'субъекта собственника текущего т.органа',
                           st_1='п.пропуска, ММПО, ОЭЗ, ЗТК')
                continue
            curr_pl_1_use = get_curr_pl_1_use(curr_cust_place_1)
            if not curr_pl_1_use:
                err_report(row=item[0], reason='Ошибка определения '
                           'субъекта пользователя текущего т.органа',
                           st_1='п.пропуска, ММПО, ОЭЗ, ЗТК')
                continue
            ##########
            if item[2][2] in ['АПП', 'ВПП', 'ЖДПП',
                              'МПП', 'ППП', 'РПП', 'СПП']:
                curr_site = get_or_create_pp(item)
            elif item[2][2] == 'ММПО':
                curr_site = get_or_create_mmpo_oez_ztk(item=item, model=Mmpo)
            elif item[2][2] == 'ОЭЗ':
                curr_site = get_or_create_mmpo_oez_ztk(item=item, model=Oez)
            elif item[2][2] == 'ЗТК':
                curr_site = get_or_create_mmpo_oez_ztk(item=item, model=Ztk)
            else:
                curr_site = None

            curr_loc_use = get_curr_loc_use(curr_site)
            # Внимание!! Проверка только по т.о. первого типа!!
            # Иметь в виду, если будет решено перейти на т.о. второго типа.
            if not chk_flags(item, curr_cust_place_1, curr_site):
                continue
            # Внимание!! Только по т.о. первого типа!!
            # Иметь в виду, если будет решено перейти на т.о. второго типа.
            get_or_cr_curr_cp_to_loc(curr_pl_1_use,
                                     curr_cust_place_1,
                                     curr_loc_use)
        print('Успешное завершение создания/апдейта перечня пунктов '
              'пропуска, ММПО, ОЭЗ, ЗТК.')

        print('Начало создания/апдейта перечня девайсов.')
        devs_pre_list = [row for row in data_3 if row[11] == 'служебная']
        all_dev_types = DevTypes.objects.all()
        all_sour_types = SourceTypes.objects.all()
        all_status_types = StatusTypes.objects.all()
        all_pprs = Ppr.objects.all()
        all_mmpos = Mmpo.objects.all()
        all_oezs = Oez.objects.all()
        all_ztks = Ztk.objects.all()
        ##########
        for item in tqdm(devs_pre_list):
            curr_mini_item = [
                item[0],
                [item[1], item[2], item[3]],
                [item[5], item[6], item[7]]
            ]
            curr_cust_place_1 = get_curr_cust_place(
                item=curr_mini_item,
                all_rtus_1=all_rtus_1,
                all_ch_1=all_ch_1,
                all_cp_1=all_cp_1
            )
            if not curr_cust_place_1:
                err_report(row=item[0],
                           reason='определения текущего т.органа',
                           st_1='девайсов')
                continue
            ##########
            curr_pl_1_acc = get_curr_pl_1_acc(curr_cust_place_1)
            if not curr_pl_1_acc:
                err_report(row=item[0], reason='определения '
                           'субъекта собственника текущего т.органа',
                           st_1='девайсов')
                continue
            curr_pl_1_use = get_curr_pl_1_use(curr_cust_place_1)
            if not curr_pl_1_use:
                err_report(row=item[0], reason='определения '
                           'субъекта пользователя текущего т.органа',
                           st_1='девайсов')
                continue
            ##########
            curr_site = get_curr_site(
                item=curr_mini_item,
                all_pprs=all_pprs,
                all_mmpos=all_mmpos,
                all_oezs=all_oezs,
                all_ztks=all_ztks
            )
            ##########
            curr_loc_use = get_curr_loc_use(curr_site)
            if not chk_flags(item, curr_cust_place_1, curr_site):
                continue
            curr_cpl_to_loc = get_or_cr_curr_cp_to_loc(curr_pl_1_use,
                                                       curr_cust_place_1,
                                                       curr_loc_use)
            if curr_cpl_to_loc is None:
                err_report(row=item[0],
                           reason='curr_cpl_to_loc не распознан '
                           'и девайс пропущен')
                continue
            ##########
            curr_dev = get_curr_dev(item=item,
                                    all_dev_types=all_dev_types,
                                    curr_pl_1_acc=curr_pl_1_acc,
                                    all_sour_types=all_sour_types,
                                    all_status_types=all_status_types
                                    )
            if curr_dev is None:
                err_report(row=item[0],
                           reason='девайс не распознан и пропущен')
                continue
            get_or_cr_curr_reltodev(to_rel=curr_cpl_to_loc,
                                    to_dev=curr_dev)
        print('Успешное завершение создания/апдейта перечня девайсов.')
