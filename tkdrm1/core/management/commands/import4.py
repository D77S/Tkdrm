"""."""
import random
import string
import sys
from datetime import datetime
from tqdm import tqdm
from typing import Union
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.core.management.base import BaseCommand

from core.models import (
    Device,
    SourceTypes,
    ServiceTypes,
    # RelToDev,
    DevTypes,
    StatusTypes,
    # DevCatsL2,
    # DevCatsL1
)

from custplaces.models import (
    Rtu,
    CustHouse,
    CustPost,
    # LocationOfUse,
    Ppr,
    # PprType,
    Mmpo,
    Oez,
    Ztk,
    Svh,
    CustPlace1Acc,
    # CustPlace1Use,
    CustPlaceToLocation
)

from users.models import (TKDRMUser,
                          Departments)

from .utils import (
    err_report,
    get_frame,
    clean_data_first,
    clean_data_second,
    get_curr_cust_place,
    get_curr_pl_1_acc,
    get_curr_pl_1_use,
    get_curr_site,
    get_curr_loc_use,
    get_or_cr_curr_reltodev
)

class Command(BaseCommand):
    """."""

    def handle(self, *args, **options):
        """."""

        def get_curr_dev4(
                item: list[Union[list[str], str]],
                all_dev_types: QuerySet[DevTypes],
                curr_pl_1_acc: CustPlace1Acc,
                curr_holder: TKDRMUser,
                all_sour_types: QuerySet,
                all_status_types: QuerySet
        ) -> Device:
            """."""

            # Определение типа девайса и срока гарантии
            curr_dev_type_temp = item[9]
            curr_dev_warr = int(float(item[15].replace(',', '.')) * 12)
            try:
                curr_dev_type = all_dev_types.get(
                    title=curr_dev_type_temp
                )
            except Exception:
                err_report(row=item[0],
                           reason='поиск типа девайса')
                return None

            # определение серийного номера девайса
            if (item[11] == '' or
               item[11] == 'б/н' or
               item[11] == 'б.н.'):
                curr_serial = None
            else:
                curr_serial = item[11]
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
            if item[17] == 'да':
                curr_sour_type = all_sour_types.get(
                    title='РФ в лице там.органа'
                )
            elif item[17] == 'нет':
                curr_sour_type = all_sour_types.get(
                    title='Иной владелец (по факту, без документа-основания)'
                )
            else:
                err_report(row=item[0],
                           reason='названия собственника нет в БД')
                return None
            # Предупреждение
            if item[5] == 'СВХ-ЮЛ' and curr_sour_type.title == 'РФ в лице там.органа':
                err_report(row=item[0],
                           reason='На коммерческом складе СВХ используется государственный прибор')

            # определение статуса тех.средства по использованию
            curr_status_use = all_status_types.get(
                    title='Используется'
                )

            # curr_subtype = ???

            # определение вышестоящего девайса
            curr_upper_id = None

            # определение принадлежности девайса к СИ
            if curr_dev_type.si_flag is False:
                curr_is_si = None
            elif item[22] == 'Да':
                curr_is_si = True
            elif item[22] == 'Нет':
                curr_is_si = False
            else:
                err_report(row=item[0],
                           reason='определения СИ/инд из-за ',
                           st_2='литерала, который таков:' + item[22])
                return None

            # определение флага включения ТС в ГК
            if item[17] == 'да':
                curr_serv_type = ServiceTypes.objects.get(
                    title='Г.бюджет, децентр.'
                )
            elif item[17] == 'нет':
                curr_serv_type = ServiceTypes.objects.get(
                    title='Вне гос.бюждета'
                )
            else:
                err_report(row=item[0],
                           reason='определения, за чей счет тех.поддержка, из-за ',
                           st_2='литерала, который таков:' + item[17])
                return None

            # загрузка второстепенных атрибутов прибора
            try:
                date_prod = datetime.strptime(item[13], '%d.%m.%Y')
            except Exception:
                err_report(row=item[0], reason=f'даты изготовления')
                return None

            try:
                date_expl = datetime.strptime(item[14], '%d.%m.%Y')
            except Exception:
                err_report(row=item[0], reason=f'даты ввода')
                return None

            curr_invent = item[12] if item[12] != '' else None

            try:
                curr_date_verif = datetime.strptime(item[23], '%d.%m.%Y')
            except Exception:
                curr_date_verif = None

            cat_number_f = int(item[24])

            if item[18] == '' or item[18] == 'Нет данных':
                curr_cost = None
            else:
                curr_cost = float(item[18])

            if item[20] == 'Исправно':
                curr_cond = True
            elif item[20] == 'Неисправно':
                curr_cond = False
            else:
                curr_cond = None

            note1 = None
            note2 = item[38] if item[38] != '' else None
            note3 = None

            # создание девайса
            try:
                curr_dev = Device.objects.create(
                    type=curr_dev_type,
                    # sub_type=curr_subtype,
                    sub_type=None,
                    serial=curr_serial,
                    inventary=curr_invent,
                    holder=curr_holder,
                    date_prod=date_prod,
                    date_expl=date_expl,
                    warr_period=curr_dev_warr,
                    date_verif=curr_date_verif,
                    cat_number_f = cat_number_f,
                    cp1_acc=curr_pl_1_acc,
                    sour_type=curr_sour_type,
                    cost=curr_cost,
                    condition=curr_cond,
                    upper_id=curr_upper_id,
                    is_si=curr_is_si,
                    is_stud=False,
                    status_use=curr_status_use,
                    service_type=curr_serv_type,
                    note1=note1,
                    note2=note2,
                    note3=note3
                )
            except Exception:
                err_report(row=item[0], reason='создания девайса')
                return None

            return curr_dev

        User = get_user_model()

        # Main begin
        print('import4.py начал работу.')
        data = get_frame(
            file='_свод_инфобаза.xlsx',
            skip=3,
            sheet='Лист1'
        )
        print('Данные из Excel загружены.')
        data_2 = clean_data_first(data)
        print('Первая очистка данных прошла.')
        # for item in data_2:
        #     print(f'Первая строка: {item}')
        #     break
        data_3 = clean_data_second(data_2, 4)
        print('Вторая очистка данных прошла.')
        # for item in data_3:
        #     print(f'Первая строка: {item}')
        #     break

        print('Начало создания перечня девайсов.')
        all_dev_types = DevTypes.objects.all()
        all_sour_types = SourceTypes.objects.all()
        all_status_types = StatusTypes.objects.all()
        all_pprs = Ppr.objects.all()
        all_mmpos = Mmpo.objects.all()
        all_oezs = Oez.objects.all()
        all_ztks = Ztk.objects.all()
        all_svhs = Svh.objects.all()
        all_rtus_1 = Rtu.objects.all()
        all_ch_1 = CustHouse.objects.all()
        all_cp_1 = CustPost.objects.all()

        print('Начало создания перечня всех, кроме Янтарь не на СВХ')
        for item in tqdm(data_3):
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # if int(item[0]) >= 2:
            #     sys.exit()
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if item[7] == 'СТСО' and  not (item[5] == 'СВХ' or item[5] == 'СВХ-ЮЛ'):
                continue
            curr_mini_item = [
                item[0],
                [item[1], item[2], item[3]],
                [item[6], None, item[5]]
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
            curr_pl_1_acc = get_curr_pl_1_acc(curr_cust_place_1)
            if not curr_pl_1_acc:
                err_report(row=item[0], reason='определения '
                           'субъекта собственника текущего т.органа',
                           st_1='п.пропуска, ММПО, ОЭЗ, ЗТК')
                continue
            curr_pl_1_use = get_curr_pl_1_use(curr_cust_place_1)

            if not curr_pl_1_use:
                err_report(row=item[0], reason='определения '
                           'субъекта пользователя текущего т.органа',
                           st_1='девайсов')
                continue
            curr_site_list: list = get_curr_site(
                item=curr_mini_item,
                all_pprs=all_pprs,
                all_mmpos=all_mmpos,
                all_oezs=all_oezs,
                all_ztks=all_ztks,
                all_svhs=all_svhs
            )
            if curr_site_list == [] and not all(x == '' or x is None for x in curr_mini_item[2]):
                print(f'{curr_mini_item=}')
                err_report(
                    row=item[0],
                    reason='не распознан сайт (ПП, ММПО, ...), критично!'
                )
                continue

            curr_loc_use_list = []
            for item2 in curr_site_list:
                curr_loc_use_list.append(get_curr_loc_use(item2))

            curr_cpl_to_loc_list = []

            if curr_loc_use_list == []:
                temp1 = CustPlaceToLocation.objects.filter(
                    cust_pl1=curr_pl_1_use,
                    loc__isnull=True
                ).first()
                if temp1:
                    curr_cpl_to_loc = temp1
                else:
                    try:
                        curr_cpl_to_loc = CustPlaceToLocation.objects.create(
                            cust_pl1=curr_pl_1_use,
                            loc=None,
                            is_main_for_cust=True
                        )
                    except Exception:
                        curr_cpl_to_loc = CustPlaceToLocation.objects.create(
                            cust_pl1=curr_pl_1_use,
                            loc=None,
                            is_main_for_cust=False
                        )
            else:
                for item2 in curr_loc_use_list:
                    try:
                        if item2 is not None:
                            temp1 = CustPlaceToLocation.objects.get(
                                cust_pl1=curr_pl_1_use,
                                loc=item2
                            )
                        else:
                            temp1 = CustPlaceToLocation.objects.get(
                                cust_pl1=curr_pl_1_use,
                                loc__isnull=False
                            )
                    except Exception:
                        temp1 = None
                    if temp1:
                        curr_cpl_to_loc_list.append(temp1)

                if len(curr_cpl_to_loc_list) == 1:
                    curr_cpl_to_loc = curr_cpl_to_loc_list[0]
                elif len(curr_cpl_to_loc_list) > 1:
                    print('Внимание, обнаружено неединственное сочетание т.о. и сайта. Берем первый.')
                    curr_cpl_to_loc = curr_cpl_to_loc_list[0]
                else:
                    err_report(
                        row=item[0],
                        reason='Непустой, но неизвестный сайт. Правьте на этапе import3.'
                    )
                    continue
            # Попытка поиска в БД первого попавшегося юзера
            # с текущим т.органом и отделом.
            # Если нет ни одного - создается.
            try:
                curr_user_dept = Departments.objects.get(
                    title=item[4])
            except Exception:
                err_report(
                    row=item[0],
                    reason='Неизвестный отдел в столбце 4'
                )
                continue
            if not User.objects.filter(
                empl=curr_pl_1_use,
                dept=curr_user_dept
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
                    dept=curr_user_dept
                )
            else:
                user = User.objects.filter(
                    empl=curr_pl_1_use,
                    dept=curr_user_dept
                ).first()
            # Создание девайса
            curr_dev = get_curr_dev4(item=item,
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
            # Создание связей по эксплуатации прибора
            get_or_cr_curr_reltodev(to_rel=curr_cpl_to_loc,
                                    to_dev=curr_dev)
