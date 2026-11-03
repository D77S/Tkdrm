import os
import sys
import shutil


def remove_and_print(abs_path):
    if os.path.isdir(abs_path):
        shutil.rmtree(abs_path)
    elif os.path.isfile(abs_path):
        os.remove(abs_path)
    else:
        raise ValueError("Неизвестный тип пути: {}".format(abs_path))
    print(abs_path)


def go(current_dir):
    is_clean_exes = "exe" in sys.argv[1:]
    for item in os.listdir(current_dir):
        abs_path = os.path.join(current_dir, item)
        if os.path.isdir(abs_path):
            if item == "__pycache__":
                remove_and_print(abs_path)
            else:
                go(abs_path)
        elif is_clean_exes and item.endswith(".exe"):
            remove_and_print(abs_path)


go(os.getcwd())
