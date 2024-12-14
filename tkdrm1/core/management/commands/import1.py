from django.core.management.base import BaseCommand
import math
import pandas

from core.models import CustPlace, Rtu, CustHouse, CustPost


class Command(BaseCommand):

    def handle(self, *args, **options):

        def rtu_replace(list_in):
            list_out = []
            for i in list_in:
                data_row = []
                for j in i:
                    if j == 'ДВТУ':
                        data_row.append('Дальневосточное таможенное управление')  # noqa
                    elif j == 'ПТУ':
                        data_row.append('Приволжское таможенное управление')
                    elif j == 'СТУ':
                        data_row.append('Сибирское таможенное управление')
                    elif j == 'СЗТУ':
                        data_row.append('Северо-Западное таможенное управление')  # noqa
                    elif j == 'УТУ':
                        data_row.append('Уральское таможенное управление')
                    elif j == 'ЦТУ':
                        data_row.append('Центральное таможенное управление')
                    elif j == 'ЮТУ':
                        data_row.append('Южное таможенное управление')
                    elif j == 'СКТУ':
                        data_row.append('Северо-Кавказское таможенное управление')  # noqa
                    else:
                        data_row.append(j)
                list_out.append(data_row)
            return list_out

        def code_finder(codes: dict[str, str], title: str):
            """."""
            code = codes.get(title, 'Такого кода нет')
            if code == 'Такого кода нет':
                temp_post = title.find('Таможенный пост')
                if temp_post != -1:
                    temp_title_1 = title.replace('Таможенный пост', '')
                    temp_title_1 = temp_title_1.strip()
                    temp_code_2 = codes.get('Таможенный пост ' + temp_title_1, 'Такого кода нет')  # noqa
                    if temp_code_2 != 'Такого кода нет':
                        return temp_code_2
                    temp_code_3 = codes.get(temp_title_1 + ' таможенный пост', 'Такого кода нет')  # noqa
                    if temp_code_3 != 'Такого кода нет':
                        return temp_code_3
                temp_post = title.find('таможенный пост')
                if temp_post != -1:
                    temp_title_1 = title.replace('таможенный пост', '')
                    temp_title_1 = temp_title_1.strip()
                    temp_code_2 = codes.get('Таможенный пост ' + temp_title_1, 'Такого кода нет')  # noqa
                    if temp_code_2 != 'Такого кода нет':
                        return temp_code_2
                    temp_code_3 = codes.get(temp_title_1 + ' таможенный пост', 'Такого кода нет')  # noqa
                    if temp_code_3 != 'Такого кода нет':
                        return temp_code_3
            return code

        data = pandas.read_excel('BD_25-11-2024.xlsx',
                                 # skiprows=0,
                                 # nrows=2,
                                 header=None,
                                 sheet_name='Новая база2',
                                 usecols=range(0, 17),
                                 )

        clean_data = [['' if isinstance(j, float) and math.isnan(j) else str(j) for j in i] for i in data.values if isinstance(i[0], int)]  # noqa
        clean_clean_data = rtu_replace(clean_data)

        codes = pandas.read_excel('BD_25-11-2024.xlsx',
                                  # skiprows=0,
                                  # nrows=2,
                                  header=None,
                                  sheet_name='Коды',
                                  usecols=range(1, 3),
                                  )

        clean_codes = {str(i[0]): str(i[1]) for i in codes.values}

        del_flag = 't'
        while not (del_flag == 'y' or del_flag == 'n'):
            del_flag = input('Удолять в БД проекта таблицы таможенных органов (y/n)?')  # noqa

        if del_flag == 'y':
            CustPlace.objects.all().delete()
            CustPost.objects.all().delete()
            CustHouse.objects.all().delete()
            Rtu.objects.all().delete()

        print(clean_clean_data[0])
        print(clean_clean_data[1])
        print('...')
        print(clean_clean_data[len(clean_clean_data)-2])
        print(clean_clean_data[len(clean_clean_data)-1])

        for i in clean_clean_data:
            row_flags = []
            for j in range(1, 4):
                if i[j] == '':
                    row_flags.append(False)
                else:
                    row_flags.append(True)

            if i[7] not in ['1', '2', '3', '4']:
                print(f'Строка {i[0]}, невалидный столбец 8.')

            if i[7] == '1' and (row_flags == [True, True, True] or row_flags == [True, True, False]):  # noqa
                # валидная строка, пункт пропуска
                # обработка названия РТУ
                if i[1] != 'ТНП':
                    # если это не ТНП, то обработка названия РТУ
                    # code = clean_codes.get(i[1], 'Такого кода нет')
                    code = code_finder(clean_codes, i[1])
                    if code == 'Такого кода нет':
                        # ошибка по коду т.органа, аварийное завершение обработки строки  # noqa
                        print(f'Строка {i[0]}, нет кода т.органа для {i[1]}')
                        continue

                    is_present_1 = Rtu.objects.filter(title=i[1]).exists()
                    is_present_2 = CustPlace.objects.filter(title=i[1]).exists()  # noqa

                    if not is_present_1:
                        # если данного названия т.органа еще нет в БД
                        # штатное создание нового т.органа
                        Rtu.objects.create(
                            title=i[1],
                            code=code,
                            level=1
                        )
                    if not is_present_2:
                        # если данного названия т.органа еще нет в БД
                        # штатное создание нового т.органа
                        CustPlace.objects.create(
                            title=i[1],
                            code=code,
                            level=1,
                            upper_id=None
                        )

                # обработка названия таможни
                code = code_finder(clean_codes, i[2])
                if code == 'Такого кода нет':
                    # ошибка по коду т.органа, аварийное завершение обработки строки  # noqa
                    print(f'Строка {i[0]}, нет кода т.органа для {i[2]}')
                    continue

                is_present_1 = CustHouse.objects.filter(title=i[2]).exists()  # noqa
                is_present_2 = CustPlace.objects.filter(title=i[2]).exists()  # noqa

                if not is_present_1:
                    # если данного названия т.органа еще нет в БД
                    # штатное создание нового т.органа
                    if i[1] == 'ТНП':
                        upper_id = None
                    else:
                        upper_id = Rtu.objects.get(title=i[1])
                    CustHouse.objects.create(
                            title=i[2],
                            code=code,
                            level=2,
                            upper_id=upper_id
                    )
                if not is_present_2:
                    # если данного названия т.органа еще нет в БД
                    # штатное создание нового т.органа
                    if i[1] == 'ТНП':
                        upper_id = None
                    else:
                        upper_id = CustPlace.objects.get(title=i[1])
                    CustPlace.objects.create(
                        title=i[2],
                        code=code,
                        level=2,
                        upper_id=upper_id
                    )

                # обработка названия т.поста (если есть!)
                if i[3] != '':
                    # название поста какое-то есть
                    code = code_finder(clean_codes, i[3])
                    if code == 'Такого кода нет':
                        # ошибка по коду т.органа, аварийное завершение обработки строки  # noqa
                        print(f'Строка {i[0]}, нет кода т.органа для {i[3]}')
                        continue

                    is_present_1 = CustPost.objects.filter(title=i[3]).exists()  # noqa
                    is_present_2 = CustPlace.objects.filter(title=i[3]).exists()  # noqa

                    if not is_present_1:
                        # если данного названия т.органа еще нет в БД
                        # штатное создание нового т.органа
                        if i[2] == '':
                            upper_id = Rtu.objects.get(title=i[1])
                        else:
                            upper_id = CustHouse.objects.get(title=i[2])
                        CustPost.objects.create(
                            title=i[3],
                            code=code,
                            level=3,
                            upper_id=upper_id
                        )
                    if not is_present_2:
                        # если данного названия т.органа еще нет в БД
                        # штатное создание нового т.органа
                        if i[2] == '':
                            upper_id = CustPlace.objects.get(title=i[1])
                        else:
                            upper_id = CustPlace.objects.get(title=i[2])
                        CustPlace.objects.create(
                            title=i[3],
                            code=code,
                            level=3,
                            upper_id=upper_id
                        )

                continue

            if i[7] == '2' and (row_flags == [True, True, True] or row_flags == [True, False, True]):  # noqa
                # валидная строка, пост
                pass
                continue

            if i[7] == '3' and row_flags == [True, True, False]:
                # валидная строка, таможня
                pass
                continue
            if i[7] == '4' and row_flags == [True, False, False]:
                # валидная строка, РТУ
                pass
                continue

            print(f'Строка {i[0]}, невалидное сочетание столбцов 2, 3, 4, 8.')
