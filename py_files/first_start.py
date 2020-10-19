import os
from loguru import logger
from py_files.some_functions import set_logger

PROXY_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'your_files', 'proxies.yml')
LOGIN_PASS_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'your_files', 'login, pass.txt')
INF_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'your_files', 'inf.yml')
YOUR_FILES_FOLDER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'your_files')
SORTED_PRICES_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'your_files', 'sorted_prices.yml')


def check_exist_path(path_file):
    if os.path.exists(path_file):
        return True
    else:
        return False

    # проверяем, существует ли proxies.yml


def check_your_files_folder(path_to_folder):
    if check_exist_path(path_to_folder):
        logger.debug('Папка "your_files" существует')
    else:
        os.mkdir(path_to_folder)
        logger.debug('Создал папку "your_files"')


def check_sorted_prices_file(path_to_sorted_prices_file):
    if check_exist_path(path_to_sorted_prices_file):
        logger.debug('Файл "sorted_prices.yml" существует')
    else:
        open(path_to_sorted_prices_file, 'w')
        logger.debug('Файл "sorted_prices.yml" не существовал, создал новый')


def check_proxies_file(path_to_proxies_file):
    if check_exist_path(path_to_proxies_file):
        logger.debug('Файл "proxies.yml" существует')

    # если не существует, просим пользователя ввести login:pass:ip:port прокси

    else:
        logger.debug('proxies.yml не существовал, создаю файл в папке your_files')
        with open(path_to_proxies_file, 'w') as proxies_file:
            logger.info(
                'Ниже введите прокси в формате login:pass:ip:port. Если не хотите использовать прокси - нажмите Enter')
            proxies_data = input()
            if proxies_data == '':
                pass
            else:
                proxies_file.write(f'proxy: {proxies_data}')


def check_login_pass_file(path_to_login_pass_file):
    # проверяем, существует ли login, pass.txt. Если нет - создаем

    if check_exist_path(path_to_login_pass_file):
        logger.debug('Файл "login, pass.txt" существует')
    else:
        open(path_to_login_pass_file, 'w')
        logger.debug('Файл "login, pass.txt" не существовал, создал новый')


def check_inf_file(path_to_inf_file):
    if check_exist_path(path_to_inf_file):
        logger.debug('Файл "inf.yml" существует')

    # если не существует, просим пользователя ввести токен и номер страны

    else:
        logger.debug('inf.yml не существует, создаю файл в папке your_files')
        with open(path_to_inf_file, 'w', encoding='utf-8-sig') as inf_file:
            logger.info('Ниже введите токен вашего аккаунта на sms-activate')
            token = input()
            logger.info(
                'Ниже введите название страны, номер телефона которой хотите арендовать. '
                'С большой буквы на русском языке:')
            country_name = input()
            logger.info('Ниже введите пол будущего аккаунта (MALE, FEMALE)')
            sex = input()
            inf_file.write(f'token: {token}\n'
                           f'country_name: {country_name}\n'
                           f'sex: {sex}\n'
                           '#Подсказка:если хотите пользоваться автоподбором страны с самой дешевой ценой номера, '
                           'задайте country_name значение False')


set_logger()
check_your_files_folder(YOUR_FILES_FOLDER_PATH)
check_sorted_prices_file(SORTED_PRICES_FILE_PATH)
check_proxies_file(PROXY_FILE_PATH)
check_login_pass_file(LOGIN_PASS_FILE_PATH)
check_inf_file(INF_FILE_PATH)
