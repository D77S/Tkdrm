"""."""
import datetime
import random
import re
import string
import sys
from tqdm import tqdm
from typing import Union
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
# from django.db import connection
from django.db.models import QuerySet
from django.utils import timezone

from core.constants import (
    # PATTERN1,
    # PATTERN2,
    PATTERN3,
    PATTERN4,
    STANDALONE_CODES,
    # SOURCE_TITLES,
    # SERVICE_TITLES,
    # STATUS_TITLES,
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
from .utils import (
    err_report,
    get_frame,
    replace_to_clean,
    clean_data_first,
    clean_data_second,
    clear_n_init,
    get_rtu,
    get_ch,
    # get_cp,
    get_curr_cust_place,
    get_curr_pl_1_acc,
    get_curr_pl_1_use,
    get_curr_site,
    get_curr_loc_use
)
from users.models import (TKDRMUser,
                          Departments)
from core.models import (
    DTCPotential,
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
    # DevCatsL2,
    # DevCatsL1
)
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


class Command(BaseCommand):
    """."""

    def handle(self, *args, **options):
        """."""

        User = get_user_model()

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
            curr_ch_1.standalone_allowed = True
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

        def get_or_cr_curr_cp_to_loc(
                curr_pl_1_use: CustPlace1Use,
                curr_loc_use: LocationOfUse,
                curr_cust_place_1: Union[Rtu, CustHouse, CustPost],
        ) -> CustPlaceToLocation:
            """."""
            temp_cp_to_loc_list = CustPlaceToLocation.objects.filter(
                cust_pl1=curr_pl_1_use,
                loc=curr_loc_use
            )
            # В БД обнаружено единственное сочетание т.о. и его сайта
            if len(temp_cp_to_loc_list) == 1:
                return temp_cp_to_loc_list[0]
            # В БД обнаружено неединственное сочетание т.о. и его сайта
            if len(temp_cp_to_loc_list) > 1:
                print('Внимание, обнаружена неуникальность сочетания т.органа и его сайта экплуатации. Работаем с первым из них.')
                return temp_cp_to_loc_list[0]
            # В БД не обнаружено таких сочетаний т.о. и его сайта
            # Создаем его
            try:
                to_out =  CustPlaceToLocation.objects.create(
                    cust_pl1=curr_pl_1_use,
                    loc=curr_loc_use,
                    is_main_for_cust=True
                )
            except Exception:
                to_out =  CustPlaceToLocation.objects.create(
                    cust_pl1=curr_pl_1_use,
                    loc=curr_loc_use,
                    is_main_for_cust=False
                )
            return to_out

        def chk_flags(
                item: list[list[str], str],
                curr_cpl: Union[Rtu, CustHouse, CustPost],
                curr_site: Union[Ppr, Mmpo, Oez, Ztk, Svh]
        ) -> bool:
            """Проверка верности сочетания флагов и наличия/отсутствия
            субъекта эксплуатации прибора."""
            if curr_cpl.standalone_allowed is False and curr_site is None:
                err_report(row=item[0],
                           reason='Некорректное сочетание флага '
                           'standalone_allowed и отсутствия субъекта '
                           'эксплуатации (п.п., ММПО, ОЭЗ, ЗТК, СВХ).')
                return False
            if curr_cpl.ztk_allowed is False and isinstance(curr_site, Ztk):
                err_report(row=item[0],
                           reason='Некорректное сочетание флага '
                           'ztk_allowed и того, что в строке ЗТК.')
                return False
            return True

        def chk_valid_year(item: str) -> bool:
            """."""
            try:
                int(item)
            except Exception:
                return False
            if not (1990 < int(item) < 2100):
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

        def get_or_create_mmpo_oez_ztk_svh(
                model: Union[Mmpo, Oez, Ztk, Svh],
                item: list[Union[list[str], str]]
        ):
            """."""
            try:
                return model.objects.get(title=item[2][0])
            except Exception:
                return model.objects.create(title=item[2][0])

        def get_curr_dev(
                item: list[Union[list[str], str]],
                all_dev_types: QuerySet[DevTypes],
                curr_pl_1_acc: CustPlace1Acc,
                curr_holder: TKDRMUser,
                all_sour_types: QuerySet,
                all_status_types: QuerySet
        ) -> Device:
            """."""

            # Определение типа девайса и срока гарантии
            if (item[13] != '' and
               item[13] in [
                   '1П1', '1П2', '1П3', '1У', 'ПБ', '2П1', '2П2', '2П3']):
                curr_dev_type_temp = 'Янтарь-' + item[13]
            elif item[13] != '' and item[13] == 'АРМ/ССД':
                curr_dev_type_temp = item[13]
            else:
                curr_dev_type_temp = item[12]
            if re.match('Янтарь', curr_dev_type_temp):
                curr_dev_warr = 24
            else:
                curr_dev_warr = 18
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

            # загрузка второстепенных атрибутов прибора
            year_prod = item[22] if item[22] != '' else None
            year_expl = item[23] if item[23] != '' else None
            note1 = item[9] if item[9] != '' else None
            note2 = item[10] if item[10] != '' else None
            note3 = item[19] if item[19] != '' else None

            # создание девайса
            curr_dev = Device.objects.create(
                type=curr_dev_type,
                serial=curr_serial,
                is_si=curr_is_si,
                cp1_acc=curr_pl_1_acc,
                sour_type=curr_sour_type,
                status_use=curr_status_use,
                # sub_type=curr_subtype,
                upper_id=curr_upper_id,
                service_type=curr_serv_type
            )

            # Дозаполнение некоторых полей созданного девайса, затем сохранение
            curr_dev.note1 = note1
            curr_dev.note2 = note2
            curr_dev.note3 = note3
            curr_dev.warr_period = curr_dev_warr
            curr_dev.holder = curr_holder
            curr_dev.cat_number_f = curr_dev.cat_number_c

            if chk_valid_year(year_prod):
                curr_dev.date_prod = datetime.date(
                    day=1,
                    month=1,
                    year=int(year_prod)
                )
            elif curr_dev.upper_id:
                curr_dev.date_prod = curr_dev.upper_id.date_prod

            if chk_valid_year(year_expl):
                curr_dev.date_expl = datetime.date(
                    day=1,
                    month=1,
                    year=int(year_expl)
                )
            elif curr_dev.upper_id:
                curr_dev.date_expl = curr_dev.upper_id.date_expl

            # Сохранение
            curr_dev.save()

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

        def cr_rel_to_contrs(
                curr_dev,
                item0,
                item_pos,
                pos,
                contr_num,
                date_of,
                title_of,
                doing,
        ):
            """Создание (если возможно) связей приборов и контрактов."""
            if item_pos == '':
                return
            try:
                temp_data = datetime.datetime.strptime(item_pos, '%d.%m.%Y')  # noqa
                data_flag = True
            except Exception:
                data_flag = False
            if not (data_flag or item_pos == '00.00.0000'):  # noqa
                err_report(row=item0, reason=f'столбец {pos}, ошибка даты')
                return

            temp_contract = Contracts.objects.get(
                title=title_of,
                number=contr_num,
                date_of=date_of
            )
            temp_relcd = RelContrDoing.objects.get(
                to_contract=temp_contract,
                to_doing=doing
            )
            temp_dtcp = DTCPotential.objects.create(dev=curr_dev, reltocd=temp_relcd)  # noqa

            if data_flag:
                temp_data = temp_data.replace(hour=0, minute=0, second=0)
                temp_data = timezone.make_aware(temp_data)
                DTCReal.objects.create(basis=temp_dtcp, exact_moment=temp_data)
            return

        # Main begin
        print('import3.py начал работу.')
        data = get_frame(
            file='__база СТСО.xlsm',
            skip=6,
            sheet='Новая база2'
        )
        print('Данные из Excel загружены.')
        if data.empty:
            sys.exit()
        data_2 = clean_data_first(data)
        print('Первая очистка данных прошла.')
        data_3 = clean_data_second(data_2, 3)
        print('Вторая очистка данных прошла.')

        print('Очистка таблиц в БД.')

        clear_n_init()

        print('Pre-valid тесты начаты.')
        for item in data_3:
            if not pre_valid_tests(item):
                print(f'Не прошла валидация строки {item[0]}!')
                sys.exit()
        print('Pre-valid тесты успешно завершены.')

        print('Начало создания перечня РТУ.')
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
        print('Успешное завершение создания перечня РТУ.')

        print('Начало создания перечня таможен.')
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
        print('Успешное завершение создания перечня таможен.')

        print('Начало создания перечня т.постов.')
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
        print('Успешное завершение создания перечня т.постов.')

        print('Начало создания перечня пунктов пропуска, '
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

            # Определяется текущий по строке объект
            # одной из моделей: Rtu, CustHouse, CustPost
            curr_cust_place_1 = get_curr_cust_place(
                item=item,
                all_rtus_1=all_rtus_1,
                all_ch_1=all_ch_1,
                all_cp_1=all_cp_1
            )
            if not curr_cust_place_1:
                err_report(row=item[0],
                           reason='определения текущего т.органа',
                           st_1='п.пропуска, ММПО, ОЭЗ, ЗТК')
                continue

            # Определяется текущий по строке объект модели
            # CustPlace1Acc
            curr_pl_1_acc = get_curr_pl_1_acc(curr_cust_place_1)
            if not curr_pl_1_acc:
                err_report(row=item[0], reason='определения '
                           'субъекта собственника текущего т.органа',
                           st_1='п.пропуска, ММПО, ОЭЗ, ЗТК')
                continue

            # Определяется текущий по строке объект модели
            # CustPlace1Use
            curr_pl_1_use = get_curr_pl_1_use(curr_cust_place_1)
            if not curr_pl_1_use:
                err_report(row=item[0], reason='Ошибка определения '
                           'субъекта пользователя текущего т.органа',
                           st_1='п.пропуска, ММПО, ОЭЗ, ЗТК')
                continue

            # Определяется или создается текущий по строке
            # объект одной из моделей: Ppr, Mmpo, Oez, Ztk, Svh
            if item[2][2] in ['АПП', 'ВПП', 'ЖДПП',
                              'МПП', 'ППП', 'РПП', 'СПП']:
                curr_site = get_or_create_pp(item)
            elif item[2][2] == 'ММПО':
                curr_site = get_or_create_mmpo_oez_ztk_svh(item=item, model=Mmpo)
            elif item[2][2] == 'ОЭЗ':
                curr_site = get_or_create_mmpo_oez_ztk_svh(item=item, model=Oez)
            elif item[2][2] == 'ЗТК':
                curr_site = get_or_create_mmpo_oez_ztk_svh(item=item, model=Ztk)
            elif item[2][2] == 'СВХ' or item[2][2] == 'СВХ-ЮЛ':
                curr_site = get_or_create_mmpo_oez_ztk_svh(item=item, model=Svh)
            else:
                curr_site = None

            # Определяется текущий по строке объект модели LocationOfUse
            curr_loc_use = get_curr_loc_use(curr_site)
            if not chk_flags(item, curr_cust_place_1, curr_site):
                continue

            # Определяется или создается текущий по строке объект
            # модели CustPlaceToLocation
            get_or_cr_curr_cp_to_loc(
                curr_pl_1_use=curr_pl_1_use,
                curr_loc_use=curr_loc_use,
                curr_cust_place_1=curr_cust_place_1
            )
        print('Успешное завершение создания перечня пунктов '
              'пропуска, ММПО, ОЭЗ, ЗТК, СВХ.')

        print('Начало создания перечня девайсов.')
        devs_pre_list = [row for row in data_3 if row[11] == 'служебная']
        all_dev_types = DevTypes.objects.all()
        all_sour_types = SourceTypes.objects.all()
        all_status_types = StatusTypes.objects.all()
        all_pprs = Ppr.objects.all()
        all_mmpos = Mmpo.objects.all()
        all_oezs = Oez.objects.all()
        all_ztks = Ztk.objects.all()
        all_svhs = Svh.objects.all()
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
            curr_site_list: list = get_curr_site(
                item=curr_mini_item,
                all_pprs=all_pprs,
                all_mmpos=all_mmpos,
                all_oezs=all_oezs,
                all_ztks=all_ztks,
                all_svhs=all_svhs
            )
            if curr_site_list == [] and not all(x == '' for x in curr_mini_item[2]):
                print(f'{curr_mini_item=}')
                err_report(
                    row=item[0],
                    reason='не распознан сайт (ПП, ММПО, ...), критично!'
                )
                continue
            if len(curr_site_list) > 1:
                err_report(
                    row=item[0],
                    reason='распознано более одного сайта (ПП, ММПО, ...), берем первый'
                )
            try:
                curr_site=curr_site_list[0]
            except Exception:
                curr_site=None
            ##########
            curr_loc_use = get_curr_loc_use(curr_site)
            if not chk_flags(item, curr_cust_place_1, curr_site):
                continue
            curr_cpl_to_loc = get_or_cr_curr_cp_to_loc(
                curr_pl_1_use=curr_pl_1_use,
                curr_loc_use=curr_loc_use,
                curr_cust_place_1=curr_cust_place_1
            )
            if curr_cpl_to_loc is None:
                err_report(row=item[0],
                           reason='curr_cpl_to_loc не распознан '
                           'и девайс пропущен')
                continue
            #########
            # Попытка поиска в БД первого попавшегося юзера
            # с текущим т.органом.
            # Если нет ни одного - создается.
            if not User.objects.filter(
                empl=curr_pl_1_use
            ).first():
                username = ''.join(random.choices(string.ascii_lowercase, k=5))
                user = User.objects.create_user(
                    username=username,
                    first_name='Иван',
                    pater_name='Иванович',
                    last_name='Иванов',
                    email='a@a.com',
                    password='123',
                    empl=curr_pl_1_use,
                    dept=Departments.objects.first()
                )
            else:
                user = User.objects.filter(empl=curr_pl_1_use).first()
            ##########
            # Создание связей по эксплуатации прибора
            curr_dev = get_curr_dev(item=item,
                                    all_dev_types=all_dev_types,
                                    curr_pl_1_acc=curr_pl_1_acc,
                                    curr_holder=user,
                                    all_sour_types=all_sour_types,
                                    all_status_types=all_status_types
                                    )
            if curr_dev is None:
                err_report(row=item[0],
                           reason='девайс не распознан и пропущен')
                continue
            get_or_cr_curr_reltodev(to_rel=curr_cpl_to_loc,
                                    to_dev=curr_dev)
            ##########
            # Создание связей по вхождению прибора в контракты
            # 2012
            # по м-продлению ср.службы
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                pos=27,
                item_pos=item[27],
                contr_num=118,
                date_of=datetime.date(year=2012, month=6, day=29),
                title_of=CONTRACT1,
                doing=Doings.objects.get(title=DOING1)
            )
            # 2013
            # по м-продлению ср.службы
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[28],
                pos=28,
                contr_num=118,
                date_of=datetime.date(year=2012, month=6, day=29),
                title_of=CONTRACT1,
                doing=Doings.objects.get(title=DOING1)
            )
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[31],
                pos=31,
                contr_num=1,
                date_of=datetime.date(year=2013, month=7, day=1),
                title_of=CONTRACT1,
                doing=Doings.objects.get(title=DOING1)
            )
            # # по одновременно т.о. и ремонту
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[29],
                pos=29,
                contr_num=65,
                date_of=datetime.date(year=2013, month=4, day=2),
                title_of=CONTRACT5,
                doing=Doings.objects.get(title=DOING4)
            )
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[30],
                pos=30,
                contr_num=65,
                date_of=datetime.date(year=2013, month=4, day=2),
                title_of=CONTRACT5,
                doing=Doings.objects.get(title=DOING3)
            )
            # 2014
            # по м-продлению ср.службы
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[32],
                pos=32,
                contr_num=1,
                date_of=datetime.date(year=2013, month=7, day=1),
                title_of=CONTRACT1,
                doing=Doings.objects.get(title=DOING1)
            )
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[33],
                pos=33,
                contr_num=120,
                date_of=datetime.date(year=2014, month=10, day=28),
                title_of=CONTRACT1,
                doing=Doings.objects.get(title=DOING1)
            )
            # по одновременно т.о. и ремонту
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[34],
                pos=34,
                contr_num=119,
                date_of=datetime.date(year=2014, month=10, day=28),
                title_of=CONTRACT5,
                doing=Doings.objects.get(title=DOING4)
            )
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[35],
                pos=35,
                contr_num=119,
                date_of=datetime.date(year=2014, month=10, day=28),
                title_of=CONTRACT5,
                doing=Doings.objects.get(title=DOING3)
            )
            # 2015
            # по м-продлению ср.службы
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[36],
                pos=36,
                contr_num=120,
                date_of=datetime.date(year=2014, month=10, day=28),
                title_of=CONTRACT1,
                doing=Doings.objects.get(title=DOING1)
            )
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[38],
                pos=38,
                contr_num=136,
                date_of=datetime.date(year=2015, month=10, day=20),
                title_of=CONTRACT1,
                doing=Doings.objects.get(title=DOING1)
            )
            # по одновременно т.о. и ремонту
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[37],
                pos=37,
                contr_num=119,
                date_of=datetime.date(year=2014, month=10, day=28),
                title_of=CONTRACT5,
                doing=Doings.objects.get(title=DOING4)
            )
            # 2016
            # по м-продлению ср.службы
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[39],
                pos=39,
                contr_num=142,
                date_of=datetime.date(year=2016, month=10, day=3),
                title_of=CONTRACT1,
                doing=Doings.objects.get(title=DOING1)
            )
            # по одновременно т.о. и ремонту
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[40],
                pos=40,
                contr_num=124,
                date_of=datetime.date(year=2016, month=9, day=5),
                title_of=CONTRACT5,
                doing=Doings.objects.get(title=DOING4)
            )
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[41],
                pos=41,
                contr_num=124,
                date_of=datetime.date(year=2016, month=9, day=5),
                title_of=CONTRACT5,
                doing=Doings.objects.get(title=DOING3)
            )
            # 2017
            # по одновременно т.о. и ремонту
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[42],
                pos=42,
                contr_num=150,
                date_of=datetime.date(year=2017, month=9, day=25),
                title_of=CONTRACT5,
                doing=Doings.objects.get(title=DOING4)
            )
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[43],
                pos=43,
                contr_num=150,
                date_of=datetime.date(year=2017, month=9, day=25),
                title_of=CONTRACT5,
                doing=Doings.objects.get(title=DOING3)
            )
            # 2018
            # по одновременно т.о. и ремонту
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[44],
                pos=44,
                contr_num=74,
                date_of=datetime.date(year=2018, month=5, day=28),
                title_of=CONTRACT5,
                doing=Doings.objects.get(title=DOING4)
            )
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[45],
                pos=45,
                contr_num=74,
                date_of=datetime.date(year=2018, month=5, day=28),
                title_of=CONTRACT5,
                doing=Doings.objects.get(title=DOING3)
            )
            # 2019
            # по т.о.
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[46],
                pos=46,
                contr_num=104,
                date_of=datetime.date(year=2019, month=7, day=3),
                title_of=CONTRACT4,
                doing=Doings.objects.get(title=DOING4)
            )
            # по ремонту
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[47],
                pos=47,
                contr_num=108,
                date_of=datetime.date(year=2019, month=7, day=3),
                title_of=CONTRACT3,
                doing=Doings.objects.get(title=DOING3)
            )
            # по м-светофор
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[48],
                pos=48,
                contr_num=134,
                date_of=datetime.date(year=2019, month=8, day=27),
                title_of=CONTRACT2,
                doing=Doings.objects.get(title=DOING2)
            )
            # 2020
            # по т.о.
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[51],
                pos=51,
                contr_num=50271,
                date_of=datetime.date(year=2020, month=5, day=8),
                title_of=CONTRACT4,
                doing=Doings.objects.get(title=DOING4)
            )
            # по ремонту1
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[49],
                pos=49,
                contr_num=282,
                date_of=datetime.date(year=2020, month=5, day=13),
                title_of=CONTRACT3,
                doing=Doings.objects.get(title=DOING3)
            )
            # по ремонту2
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[50],
                pos=50,
                contr_num=379,
                date_of=datetime.date(year=2020, month=11, day=2),
                title_of=CONTRACT3,
                doing=Doings.objects.get(title=DOING3)
            )
            # 2021
            # по т.о.
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[53],
                pos=53,
                contr_num=114,
                date_of=datetime.date(year=2021, month=8, day=18),
                title_of=CONTRACT4,
                doing=Doings.objects.get(title=DOING4)
            )
            # по ремонту
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[52],
                pos=52,
                contr_num=115,
                date_of=datetime.date(year=2021, month=8, day=23),
                title_of=CONTRACT3,
                doing=Doings.objects.get(title=DOING3)
            )
            # 2022
            # по т.о.
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[55],
                pos=55,
                contr_num=424,
                date_of=datetime.date(year=2022, month=10, day=3),
                title_of=CONTRACT4,
                doing=Doings.objects.get(title=DOING4)
            )
            # по ремонту
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[54],
                pos=54,
                contr_num=393,
                date_of=datetime.date(year=2022, month=8, day=15),
                title_of=CONTRACT3,
                doing=Doings.objects.get(title=DOING3)
            )
            # 2023
            # по т.о.1
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[57],
                pos=57,
                contr_num=85,
                date_of=datetime.date(year=2023, month=6, day=26),
                title_of=CONTRACT4,
                doing=Doings.objects.get(title=DOING4)
            )
            # по т.о.2
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[58],
                pos=58,
                contr_num=82,
                date_of=datetime.date(year=2023, month=6, day=21),
                title_of=CONTRACT4,
                doing=Doings.objects.get(title=DOING4)
            )
            # по ремонту
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[56],
                pos=56,
                contr_num=72,
                date_of=datetime.date(year=2023, month=5, day=29),
                title_of=CONTRACT3,
                doing=Doings.objects.get(title=DOING3)
            )
            # 2024
            # по т.о.
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[60],
                pos=60,
                contr_num=184,
                date_of=datetime.date(year=2024, month=3, day=26),
                title_of=CONTRACT4,
                doing=Doings.objects.get(title=DOING4)
            )
            # по ремонту
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[59],
                pos=59,
                contr_num=183,
                date_of=datetime.date(year=2024, month=3, day=27),
                title_of=CONTRACT3,
                doing=Doings.objects.get(title=DOING3)
            )
            # 2025
            # по т.о.
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[67],
                pos=67,
                contr_num=47,
                date_of=datetime.date(year=2025, month=4, day=22),
                title_of=CONTRACT4,
                doing=Doings.objects.get(title=DOING4)
            )
            # по ремонту
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[71],
                pos=71,
                contr_num=68,
                date_of=datetime.date(year=2025, month=6, day=23),
                title_of=CONTRACT3,
                doing=Doings.objects.get(title=DOING3)
            )
            # 2026
            # по т.о.
            cr_rel_to_contrs(
                curr_dev=curr_dev,
                item0=item[0],
                item_pos=item[75],
                pos=75,
                contr_num=32,
                date_of=datetime.date(year=2026, month=5, day=6),
                title_of=CONTRACT4,
                doing=Doings.objects.get(title=DOING4)
            )
            # Попытка апдейта фактической категории девайса
            curr_dev.cat_number_f = curr_dev.cat_number_c
            curr_dev.save()

        print('Успешное завершение создания перечня девайсов.')
