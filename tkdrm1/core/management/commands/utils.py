"""."""
import math
import os
import pandas


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
