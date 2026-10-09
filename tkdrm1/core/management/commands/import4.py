"""."""
import sys
from tqdm import tqdm
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.models import (
    # DTCPotential,
    # Device,
    # DTCReal,
    # RelContrDoing,
    # Contracts,
    # Doings,
    SourceTypes,
    # ServiceTypes,
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
    # CustPlace1Acc,
    # CustPlace1Use,
    CustPlaceToLocation
)

from .utils import (
    err_report,
    get_frame,
    clean_data_first,
    clean_data_second,
    get_curr_cust_place,
    get_curr_pl_1_acc,
    get_curr_pl_1_use,
    get_curr_site,
    get_curr_loc_use
)

class Command(BaseCommand):
    """."""

    def handle(self, *args, **options):
        """."""

        User = get_user_model()

        # Main begin
        print('import4.py начал работу.')
        data = get_frame(
            file='_свод_инфобаза.xlsx',
            skip=3,
            sheet='Лист1'
        )
        print('Данные из Excel загружены.')
        if data.empty:
            sys.exit()
        data_2 = clean_data_first(data)
        print('Первая очистка данных прошла.')
        data_3 = clean_data_second(data_2, 4)
        print('Вторая очистка данных прошла.')

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

        print('Начало создания перечня всех, кроме Янтарь (с ВН, АРМ, ССД) и кроме СВХ.')
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        x1 = 0
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        for item in tqdm(data_3):
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            x1 += 1 
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if item[7] == 'СТСО' or item[5] == 'СВХ' or item[5] == 'СВХ-ЮЛ':
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
            if len(curr_site_list) > 0:
                for item2 in curr_site_list:
                    curr_loc_use_list.append(get_curr_loc_use(item2))

            curr_cpl_to_loc_list = []
            if len(curr_loc_use_list) > 0:
                for item2 in curr_loc_use_list:
                    try:
                        temp1 = CustPlaceToLocation.objects.get(
                            cust_pl1=curr_pl_1_use,
                            loc=item2
                        )
                    except Exception:
                        temp1 = None
                    if temp1:
                        curr_cpl_to_loc_list.append(temp1)

            if len(curr_cpl_to_loc_list) != 1:
                err_report(
                    row=item[0],
                    reason=' сочетаний т.о. и сайта найдено ноль или больше одного, критично! Пропуск прибора'
                )
                continue
            curr_cpl_to_loc = curr_cpl_to_loc_list[0]

            ##########
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if x1 >= 200:
                sys.exit()
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # print(f'{item[0]=}')
            # print(f'{curr_mini_item=}')
            # print(f'{curr_cust_place_1=}')
            # print(f'{curr_site=}')
