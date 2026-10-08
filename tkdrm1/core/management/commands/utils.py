"""."""
import datetime
import math
import os
import pandas
from django.db.models import QuerySet
from typing import Union

from users.models import (TKDRMUser,
                          Departments)
from core.models import (DTCPotential,
                         Device,
                         DTCReal,
                         RelContrDoing,
                         Contracts,
                         Doings,
                         SourceTypes,
                         ServiceTypes,
                         RelToDev,
                         DevTypes,
                         StatusTypes,
                         DevCatsL2,
                         DevCatsL1)
from custplaces.models import (CustHouse,
                               CustPost,
                               LocationOfUse,
                               Ppr,
                               PprType,
                               Mmpo,
                               Oez,
                               Ztk,
                               Svh,
                               Rtu,
                               CustPlace1Acc,
                               CustPlace1Use,
                               CustPlaceToLocation)
from core.constants import (
    PATTERN1,
    PATTERN2,
    # PATTERN3,
    # PATTERN4,
    # STANDALONE_CODES,
    SOURCE_TITLES,
    SERVICE_TITLES,
    STATUS_TITLES,
    DOING1,
    DOING2,
    DOING3,
    DOING4,
    CONTRACT1,
    CONTRACT2,
    CONTRACT3,
    CONTRACT4,
    CONTRACT5
)

def err_report(
    row: str = None,
    reason: str = None,
    st_1: str = None,
    st_2: str = None,
    elsewhere: str = None
):
    """."""
    row_lit = f'Строка {row}. ' if row else ''
    reason_lit = f'Ошибка {reason}. ' if reason else ''
    stage_lit_1 = f'При создании перечня {st_1}. ' if st_1 else ''
    stage_lit_2 = f'На этапе запроса {st_2}. ' if st_2 else ''
    elst_lit = f'Иная ошибка: {elsewhere}.'
    print(f'{row_lit}{reason_lit}{stage_lit_1}{stage_lit_2}{elst_lit}')

def get_frame(
        file,
        skip,
        sheet
) -> pandas.DataFrame:
    """."""
    if not os.path.exists(file):
        err_report(
            elsewhere=f'В текущем каталоге не найден файл {file}, аварийно завершено'
        )
        return
    print(f'В текущем каталоге найден файл {file}.')
    try:
        data = pandas.read_excel(file,
                                 skiprows=skip,
                                 header=None,
                                 sheet_name=sheet,
                                 )
    except Exception:
        err_report(elsewhere='Ошибка формата файла, аварийно завершено')
        return
    return data

def replace_to_clean(source: str, pattern: dict):
    """."""
    if source in pattern.keys():
        to_out = pattern.get(source)
    else:
        to_out = source
    return to_out

def clean_data_first(data_in):
    """."""
    data_out = []
    for i in data_in.values:
        data_out_temp = []
        for j in i:
            if isinstance(j, int):
                data_out_temp.append(str(j))
            elif isinstance(j, float) and math.isnan(j):
                data_out_temp.append('')
            elif isinstance(j, float):
                data_out_temp.append(str(int(j)))
            elif isinstance(j, str):
                data_out_temp.append(str(j))
            else:
                data_out_temp.append('')
        data_out.append(data_out_temp)
    return data_out

def clean_data_second(data_in: list[list[str]], num_im: int):
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
            elif num_im ==3 and (i in [4, 20, 21, 22, 23, 24]):
                temp_row.append(
                    row[i].split('.')[0]
                )
            elif num_im == 4 and (i in[0, 25]):
                temp_row.append(
                    row[i].split('.')[0]
                )
            elif num_im == 3 and i == 7:
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
        # core app
        RelToDev.objects.all().delete()
        # connection.cursor().execute('ALTER SEQUENCE reltodev_id_seq RESTART WITH 1')  # noqa
        DTCReal.objects.all().delete()
        DTCPotential.objects.all().delete()
        Device.objects.all().delete()
        RelContrDoing.objects.all().delete()
        Contracts.objects.all().delete()
        Doings.objects.all().delete()
        DevTypes.objects.all().delete()
        DevCatsL2.objects.all().delete()
        DevCatsL1.objects.all().delete()
        ServiceTypes.objects.all().delete()
        StatusTypes.objects.all().delete()
        SourceTypes.objects.all().delete()
        # users app
        TKDRMUser.objects.all().delete()
        Departments.objects.all().delete()
        # custplace app
        CustPlaceToLocation.objects.all().delete()
        LocationOfUse.objects.all().delete()
        CustPlace1Use.objects.all().delete()
        CustPlace1Acc.objects.all().delete()
        Svh.objects.all().delete()
        Ztk.objects.all().delete()
        Oez.objects.all().delete()
        Mmpo.objects.all().delete()
        Ppr.objects.all().delete()
        PprType.objects.all().delete()
        CustPost.objects.all().delete()
        CustHouse.objects.all().delete()
        Rtu.objects.all().delete()

        # create initial
        # custplace app
        tnp_obj_1 = Rtu.objects.create(title='ТНП', code=None)
        CustHouse.objects.create(title='ТНП', code=None, upper_id=tnp_obj_1)  # noqa
        ppr_types_titles = ['АПП', 'ВПП', 'ЖДПП', 'МПП', 'ППП', 'РПП', 'СПП']  # noqa
        ppr_types_objs = [PprType(title=item) for item in ppr_types_titles]
        PprType.objects.bulk_create(objs=ppr_types_objs)
        oez_titles = [
            'АО \n«ВИнКо\n»',
            'Липецк',
            'Нойдорф',
            'ОАО \n"ОЭЗ ТВТ-Дубна\n"',
            'ПОЭЗ Ульяновск',
            'Томск'
        ]
        for item in oez_titles:
            Oez.objects.create(title=item)     
        # users app
        Departments.objects.create(title='ОТКДРМ')
        # core app
        source_objs = [SourceTypes(title=i) for i in SOURCE_TITLES]
        SourceTypes.objects.bulk_create(objs=source_objs)
        status_objs = [StatusTypes(title=i) for i in STATUS_TITLES]
        StatusTypes.objects.bulk_create(objs=status_objs)
        service_objs = [ServiceTypes(title=i) for i in SERVICE_TITLES]
        ServiceTypes.objects.bulk_create(objs=service_objs)
        DevCatsL1.objects.create(title='Стационарные')
        DevCatsL1.objects.create(title='Переносные')
        dev_cats_l2_titles = [
            ['СТСО', DevCatsL1.objects.get(title='Стационарные')],
            ['ИИИ к СТСО', DevCatsL1.objects.get(title='Переносные')],
            ['МТСО', DevCatsL1.objects.get(title='Переносные')],
            ['ВН', DevCatsL1.objects.get(title='Стационарные')],
            ['Телеком', DevCatsL1.objects.get(title='Стационарные')],
            ['Дозиметры', DevCatsL1.objects.get(title='Переносные')],
            ['Поисковые', DevCatsL1.objects.get(title='Переносные')],
            ['Поисковые двухканальные', DevCatsL1.objects.get(title='Переносные')],
            ['Радиометры-спектрометры', DevCatsL1.objects.get(
                title='Переносные')],
            ['Спектрометры', DevCatsL1.objects.get(title='Переносные')],
            ['СИЗ', DevCatsL1.objects.get(title='Переносные')],
            ['Прочее', DevCatsL1.objects.get(title='Переносные')],
        ]
        dev_cats_l2_objs = [
            DevCatsL2(title=item[0],
                      cat_l1=item[1]) for item in dev_cats_l2_titles]
        DevCatsL2.objects.bulk_create(objs=dev_cats_l2_objs)
        dev_types_titles = [
            ['FH40G-L10', DevCatsL2.objects.get(title='Дозиметры'), 24,
             True, False, True, None],
            ['AT1121', DevCatsL2.objects.get(title='Дозиметры'), 24,
             True, False, True, None],
            ['AT1123', DevCatsL2.objects.get(title='Дозиметры'), 24,
             True, False, True, None],
            ['Гамма-1С/NB1-02', DevCatsL2.objects.get(title='Спектрометры'), 24,
             True, False, True, None],
            ['ДБГ', DevCatsL2.objects.get(title='Дозиметры'), 24,
             True, False, True, None],
            ['Калифорний-252', DevCatsL2.objects.get(title='ИИИ к СТСО'), 24,
             None, False, None, None],
            ['Кюрий-244', DevCatsL2.objects.get(title='ИИИ к СТСО'), 24,
             None, False, None, None],
            ['МКС-А02', DevCatsL2.objects.get(title='Радиометры-спектрометры'), 24,
             True, False, True, None],
            ['МКС-А03-1', DevCatsL2.objects.get(title='Радиометры-спектрометры'), 24,
             True, False, True, None],
            ['МКС-А03-1Н', DevCatsL2.objects.get(title='Радиометры-спектрометры'), 24,
             True, False, True, None],
            ['ММОМ', DevCatsL2.objects.get(title='Прочее'), 24,
             None, False, False, None],
            ['РМ1203М', DevCatsL2.objects.get(title='Дозиметры'), 24,
             True, False, True, None],
            ['РМ1401', DevCatsL2.objects.get(title='Поисковые'), 24,
             True, False, True, None],
            ['РМ1401К', DevCatsL2.objects.get(title='Радиометры-спектрометры'), 24,
             True, False, True, None],
            ['РМ1401К-01', DevCatsL2.objects.get(title='Поисковые двухканальные'), 24,
             True, False, True, None],
            ['РМ1401М', DevCatsL2.objects.get(title='Поисковые'), 24,
             True, False, True, None],
            ['РМ1610', DevCatsL2.objects.get(title='Дозиметры'), 24,
             True, False, True, None],
            ['РМ1621', DevCatsL2.objects.get(title='Дозиметры'), 24,
             True, False, True, None],
            ['РСУ-01', DevCatsL2.objects.get(title='Радиометры-спектрометры'), 24,
             True, False, True, None],
            ['СИЗ', DevCatsL2.objects.get(title='СИЗ'), 24,
             False, False, False, None],
            ['СКС-50М', DevCatsL2.objects.get(title='Спектрометры'), 24,
             True, False, True, None],
            ['ТППРК', DevCatsL2.objects.get(title='МТСО'), 24,
             None, False, False, None],
            ['Цезий-137', DevCatsL2.objects.get(title='ИИИ к СТСО'), 24,
             None, False, None, None],
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
             None, None, False, None],
            ['Янтарь-1А', DevCatsL2.objects.get(title='СТСО'), 12,
             True, False, True, None],
            ['Янтарь-2А', DevCatsL2.objects.get(title='СТСО'), 12,
             True, False, True, None],
            ['ВН-А', DevCatsL2.objects.get(title='ВН'), 2,
             None, None, False, None],
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
             None, None, False, None],
            ['ВН-ПБ', DevCatsL2.objects.get(title='ВН'), 2,
             None, None, False, None],
            ['Янтарь-1Ж', DevCatsL2.objects.get(title='СТСО'), 12,
             True, False, True, None],
            ['Янтарь-1Ж2', DevCatsL2.objects.get(title='СТСО'), 12,
             True, False, True, None],
            ['Янтарь-2Ж', DevCatsL2.objects.get(title='СТСО'), 12,
             True, False, True, None],
            ['Янтарь-2Ж2', DevCatsL2.objects.get(title='СТСО'), 12,
             True, False, True, None],
            ['Янтарь-МА', DevCatsL2.objects.get(title='МТСО'), 24,
             True, False, True, None],
            ['ВН-Ж', DevCatsL2.objects.get(title='ВН'), 2,
             None, None, False, None],
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
        # Создание всех контрактов
        # 2012
        # по м-продлению ср.службы
        c_2012_m12 = Contracts.objects.create(
            title=CONTRACT1,
            number=118,
            date_of=datetime.date(year=2012, month=6, day=29),
            date_start=datetime.date(year=2012, month=6, day=29),
            date_end=datetime.date(year=2013, month=6, day=30)
        )
        # 2013
        # по м-продлению ср.службы
        c_2013_m12 = Contracts.objects.create(
            title=CONTRACT1,
            number=1,
            date_of=datetime.date(year=2013, month=7, day=1),
            date_start=datetime.date(year=2013, month=7, day=2),
            date_end=datetime.date(year=2014, month=6, day=30)
        )
        # по одновременно т.о. и ремонту
        c_2013_tr = Contracts.objects.create(
            title=CONTRACT5,
            number=65,
            date_of=datetime.date(year=2013, month=4, day=2),
            date_start=datetime.date(year=2013, month=4, day=2),
            date_end=datetime.date(year=2014, month=10, day=27)
        )
        # 2014
        # по м-продлению ср.службы
        c_2014_m12 = Contracts.objects.create(
            title=CONTRACT1,
            number=120,
            date_of=datetime.date(year=2014, month=10, day=28),
            date_start=datetime.date(year=2014, month=10, day=29),
            date_end=datetime.date(year=2015, month=6, day=30)
        )
        # по одновременно т.о. и ремонту
        c_2014_tr = Contracts.objects.create(
            title=CONTRACT5,
            number=119,
            date_of=datetime.date(year=2014, month=10, day=28),
            date_start=datetime.date(year=2014, month=10, day=29),
            date_end=datetime.date(year=2016, month=9, day=4)
        )
        # 2015
        # по м-продлению ср.службы
        c_2015_m12 = Contracts.objects.create(
            title=CONTRACT1,
            number=136,
            date_of=datetime.date(year=2015, month=10, day=20),
            date_start=datetime.date(year=2015, month=10, day=21),
            date_end=datetime.date(year=2015, month=12, day=10)
        )
        # 2016
        # по м-продлению ср.службы
        c_2016_m12 = Contracts.objects.create(
            title=CONTRACT1,
            number=142,
            date_of=datetime.date(year=2016, month=10, day=3),
            date_start=datetime.date(year=2016, month=10, day=4),
            date_end=datetime.date(year=2016, month=12, day=1)
        )
        # по одновременно т.о. и ремонту
        c_2016_tr = Contracts.objects.create(
            title=CONTRACT5,
            number=124,
            date_of=datetime.date(year=2016, month=9, day=5),
            date_start=datetime.date(year=2016, month=9, day=6),
            date_end=datetime.date(year=2016, month=12, day=1)
        )
        # 2017
        # по одновременно т.о. и ремонту
        c_2017_tr = Contracts.objects.create(
            title=CONTRACT5,
            number=150,
            date_of=datetime.date(year=2017, month=9, day=25),
            date_start=datetime.date(year=2017, month=9, day=26),
            date_end=datetime.date(year=2017, month=11, day=30)
        )
        # 2018
        # по одновременно т.о. и ремонту
        c_2018_tr = Contracts.objects.create(
            title=CONTRACT5,
            number=74,
            date_of=datetime.date(year=2018, month=5, day=28),
            date_start=datetime.date(year=2018, month=5, day=29),
            date_end=datetime.date(year=2018, month=11, day=20)
        )
        # 2019
        # по т.о.
        c_2019_t = Contracts.objects.create(
            title=CONTRACT4,
            number=104,
            date_of=datetime.date(year=2019, month=7, day=3),
            date_start=datetime.date(year=2019, month=7, day=15),
            date_end=datetime.date(year=2019, month=11, day=20)
        )
        # по ремонту
        c_2019_r = Contracts.objects.create(
            title=CONTRACT3,
            number=108,
            date_of=datetime.date(year=2019, month=7, day=3),
            date_start=datetime.date(year=2019, month=7, day=15),
            date_end=datetime.date(year=2019, month=11, day=20)
        )
        # по м-светофор
        c_2019_ms = Contracts.objects.create(
            title=CONTRACT2,
            number=134,
            date_of=datetime.date(year=2019, month=8, day=27),
            date_start=datetime.date(year=2019, month=9, day=11),
            date_end=datetime.date(year=2019, month=11, day=20)
        )
        # 2020
        # по т.о.
        c_2020_t = Contracts.objects.create(
            title=CONTRACT4,
            number=50271,
            date_of=datetime.date(year=2020, month=5, day=8),
            date_start=datetime.date(year=2020, month=6, day=5),
            date_end=datetime.date(year=2020, month=11, day=20)
        )
        # по ремонту1
        c_2020_r1 = Contracts.objects.create(
            title=CONTRACT3,
            number=282,
            date_of=datetime.date(year=2020, month=5, day=13),
            date_start=datetime.date(year=2020, month=6, day=5),
            date_end=datetime.date(year=2020, month=11, day=20)
        )
        # по ремонту2
        c_2020_r2 = Contracts.objects.create(
            title=CONTRACT3,
            number=379,
            date_of=datetime.date(year=2020, month=11, day=2),
            date_start=datetime.date(year=2020, month=11, day=11),
            date_end=datetime.date(year=2021, month=11, day=19)
        )
        # 2021
        # по т.о.
        c_2021_t = Contracts.objects.create(
            title=CONTRACT4,
            number=114,
            date_of=datetime.date(year=2021, month=8, day=18),
            date_start=datetime.date(year=2021, month=8, day=30),
            date_end=datetime.date(year=2021, month=11, day=29)
        )
        # по ремонту
        c_2021_r = Contracts.objects.create(
            title=CONTRACT3,
            number=115,
            date_of=datetime.date(year=2021, month=8, day=23),
            date_start=datetime.date(year=2021, month=8, day=30),
            date_end=datetime.date(year=2022, month=11, day=21)
        )
        # 2022
        # по т.о.
        c_2022_t = Contracts.objects.create(
            title=CONTRACT4,
            number=424,
            date_of=datetime.date(year=2022, month=10, day=3),
            date_start=datetime.date(year=2022, month=10, day=7),
            date_end=datetime.date(year=2022, month=11, day=29)
        )
        # по ремонту
        c_2022_r = Contracts.objects.create(
            title=CONTRACT3,
            number=393,
            date_of=datetime.date(year=2022, month=8, day=15),
            date_start=datetime.date(year=2022, month=8, day=31),
            date_end=datetime.date(year=2023, month=11, day=21)
        )
        # 2023
        # по т.о.1
        c_2023_t1 = Contracts.objects.create(
            title=CONTRACT4,
            number=85,
            date_of=datetime.date(year=2023, month=6, day=26),
            date_start=datetime.date(year=2023, month=7, day=14),
            date_end=datetime.date(year=2023, month=11, day=21)
        )
        # по т.о.2
        c_2023_t2 = Contracts.objects.create(
            title=CONTRACT4,
            number=82,
            date_of=datetime.date(year=2023, month=6, day=21),
            date_start=datetime.date(year=2023, month=7, day=5),
            date_end=datetime.date(year=2023, month=11, day=21)
        )
        # по ремонту
        c_2023_r = Contracts.objects.create(
            title=CONTRACT3,
            number=72,
            date_of=datetime.date(year=2023, month=5, day=29),
            date_start=datetime.date(year=2023, month=6, day=16),
            date_end=datetime.date(year=2024, month=11, day=21)
        )
        # 2024
        # по т.о.
        c_2024_t = Contracts.objects.create(
            title=CONTRACT4,
            number=184,
            date_of=datetime.date(year=2024, month=3, day=26),
            date_start=datetime.date(year=2024, month=4, day=23),
            date_end=datetime.date(year=2024, month=11, day=21)
        )
        # по ремонту
        c_2024_r = Contracts.objects.create(
            title=CONTRACT3,
            number=183,
            date_of=datetime.date(year=2024, month=3, day=27),
            date_start=datetime.date(year=2024, month=4, day=23),
            date_end=datetime.date(year=2025, month=11, day=21)
        )
        # 2025
        # по т.о.
        c_2025_t = Contracts.objects.create(
            title=CONTRACT4,
            number=47,
            date_of=datetime.date(year=2025, month=4, day=22),
            date_start=datetime.date(year=2025, month=4, day=30),
            date_end=datetime.date(year=2025, month=11, day=21)
        )
        # по ремонту
        c_2025_r = Contracts.objects.create(
            title=CONTRACT3,
            number=68,
            date_of=datetime.date(year=2025, month=6, day=23),
            date_start=datetime.date(year=2025, month=7, day=10),
            date_end=datetime.date(year=2026, month=7, day=1)
        )
        # 2026
        # по т.о.
        c_2026_t = Contracts.objects.create(
            title=CONTRACT4,
            number=32,
            date_of=datetime.date(year=2026, month=5, day=6),
            date_start=datetime.date(year=2026, month=7, day=3),
            date_end=datetime.date(year=2026, month=11, day=23)
        )

        # Создание всех отношений между контрактами и действиями по ним
        # 2012
        # по м-продлению ср.службы
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING1)[0],
            to_contract=c_2012_m12,
            min_count=1,
            max_count=1
        )
        # 2013
        # по м-продлению ср.службы
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING1)[0],
            to_contract=c_2013_m12,
            min_count=1,
            max_count=1
        )
        # по одновременно т.о. и ремонту
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING4)[0],
            to_contract=c_2013_tr,
            min_count=1,
            max_count=1
        )
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING3)[0],
            to_contract=c_2013_tr,
            min_count=0,
            max_count=500
        )
        # 2014
        # по м-продлению ср.службы
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING1)[0],
            to_contract=c_2014_m12,
            min_count=1,
            max_count=1
        )
        # по одновременно т.о. и ремонту
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING4)[0],
            to_contract=c_2014_tr,
            min_count=1,
            max_count=1
        )
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING3)[0],
            to_contract=c_2014_tr,
            min_count=0,
            max_count=500
        )
        # 2015
        # по м-продлению ср.службы
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING1)[0],
            to_contract=c_2015_m12,
            min_count=1,
            max_count=1
        )
        # 2016
        # по м-продлению ср.службы
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING1)[0],
            to_contract=c_2016_m12,
            min_count=1,
            max_count=1
        )
        # по одновременно т.о. и ремонту
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING4)[0],
            to_contract=c_2016_tr,
            min_count=1,
            max_count=1
        )
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING3)[0],
            to_contract=c_2016_tr,
            min_count=0,
            max_count=500
        )
        # 2017
        # по одновременно т.о. и ремонту
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING4)[0],
            to_contract=c_2017_tr,
            min_count=1,
            max_count=1
        )
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING3)[0],
            to_contract=c_2017_tr,
            min_count=0,
            max_count=500
        )
        # 2018
        # по одновременно т.о. и ремонту
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING4)[0],
            to_contract=c_2018_tr,
            min_count=1,
            max_count=1
        )
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING3)[0],
            to_contract=c_2018_tr,
            min_count=0,
            max_count=500
        )
        # 2019
        # по т.о.
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING4)[0],
            to_contract=c_2019_t,
            min_count=1,
            max_count=1
        )
        # по ремонту
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING3)[0],
            to_contract=c_2019_r,
            min_count=0,
            max_count=500
        )
        # по м-светофор
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING2)[0],
            to_contract=c_2019_ms,
            min_count=1,
            max_count=1
        )
        # 2020
        # по т.о.
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING4)[0],
            to_contract=c_2020_t,
            min_count=1,
            max_count=1
        )
        # по ремонту1
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING3)[0],
            to_contract=c_2020_r1,
            min_count=0,
            max_count=500
        )
        # по ремонту2
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING3)[0],
            to_contract=c_2020_r2,
            min_count=0,
            max_count=500
        )
        # 2021
        # по т.о.
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING4)[0],
            to_contract=c_2021_t,
            min_count=1,
            max_count=1
        )
        # по ремонту
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING3)[0],
            to_contract=c_2021_r,
            min_count=0,
            max_count=500
        )
        # 2022
        # по т.о.
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING4)[0],
            to_contract=c_2022_t,
            min_count=1,
            max_count=1
        )
        # по ремонту
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING3)[0],
            to_contract=c_2022_r,
            min_count=0,
            max_count=500
        )
        # 2023
        # по т.о.1
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING4)[0],
            to_contract=c_2023_t1,
            min_count=1,
            max_count=1
        )
        # по т.о.2
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING4)[0],
            to_contract=c_2023_t2,
            min_count=1,
            max_count=1
        )
        # по ремонту
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING3)[0],
            to_contract=c_2023_r,
            min_count=0,
            max_count=500
        )
        # 2024
        # по т.о.
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING4)[0],
            to_contract=c_2024_t,
            min_count=1,
            max_count=1
        )
        # по ремонту
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING3)[0],
            to_contract=c_2024_r,
            min_count=0,
            max_count=500
        )
        # 2025
        # по т.о.
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING4)[0],
            to_contract=c_2025_t,
            min_count=1,
            max_count=1
        )
        # по ремонту
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING3)[0],
            to_contract=c_2025_r,
            min_count=0,
            max_count=500
        )
        # 2026
        # по т.о.
        RelContrDoing.objects.create(
            to_doing=Doings.objects.get_or_create(title=DOING4)[0],
            to_contract=c_2026_t,
            min_count=1,
            max_count=1
        )

def get_rtu(
          data_in: list[Union[list[str], str]],
          all_rtus_1: QuerySet
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
        data_in: list[Union[list[str], str]],
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
        data_in: list[Union[list[str], str]],
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
        all_cp_1: QuerySet
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

def get_curr_site(
        item: list[Union[list[str], str]],
        all_pprs: QuerySet,
        all_mmpos: QuerySet,
        all_oezs: QuerySet,
        all_ztks: QuerySet,
        all_svhs: QuerySet
        ) -> list[Union[Ppr, Mmpo, Ztk, Oez, Svh]]:
    """Определение текущего п.п, ММПО, ОЭЗ, ЗТК или СВХ.
    Принимает строку вида
    ['1', ['Дальневосточное таможенное управление', 'Бурятская таможня', 'Таможенный пост ДАПП Монды'], ['Монды', 'МНР', 'АПП']]  # noqa
    И перечни всех п.п., ММПО, ОЭЗ, ЗТК, СВХ в виде кверисетов.
    Возвращает список объектов, в идеале из единственного члена,
    одного из типов:
    Ppr, Mmpo, Ztk, Oez или Svh.
    """
    if item[2][2] in ['АПП', 'ВПП', 'ЖДПП',
                      'МПП', 'ППП', 'РПП', 'СПП']:
        pptype = PprType.objects.get(title=item[2][2])
        if item[2][2] in ['АПП', 'ЖДПП', 'ППП', 'РПП', 'СПП'] and item[2][1]:
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
        return list(pprs_qs)
    elif item[2][2] == 'ММПО':
        mmpos_qs = all_mmpos.filter(title=item[2][0])
        return list(mmpos_qs)
    elif item[2][2] == 'ОЭЗ':
        oezs_qs = all_oezs.filter(title=item[2][0])
        return list(oezs_qs)
    elif item[2][2] == 'ЗТК':
        ztks_qs = all_ztks.filter(title=item[2][0])
        return list(ztks_qs)
    elif item[2][2] == 'СВХ' or item[2][2] == 'СВХ-ЮЛ':
        svhs_qs = all_svhs.filter(title=item[2][0])
        return list(svhs_qs)
    return []

def get_curr_loc_use(
        curr_site: Union[Ppr, Mmpo, Oez, Ztk, Svh]
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
    if isinstance(curr_site, Svh):
        return LocationOfUse.objects.get(svh=curr_site)
    return None
