"""."""
import os
import pandas

def get_frame(
        file,
        skip,
        sheet
) -> pandas.DataFrame:
    """."""
    if not os.path.exists(file):
        print(f'В текущем каталоге не найден файл {file}, аварийно завершено.')
        return
    print(f'В текущем каталоге найден файл {file}.')
    try:
        data = pandas.read_excel(file,
                                 skiprows=skip,
                                 header=None,
                                 sheet_name=sheet,
                                 )
    except Exception:
        print('Ошибка формата файла, аварийно завершено.')
        return
    return data
