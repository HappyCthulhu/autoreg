import os
import yaml
from loguru import logger
from selenium import webdriver
from py_files.some_functions import set_logger

set_logger()


def define_proxy_type(proxy_file_path):
    with open(proxy_file_path, 'r',
              encoding='utf-8-sig', errors='ignore') as proxies_file:
        proxy_data_list = yaml.load(proxies_file, Loader=yaml.FullLoader)['proxy'].split(':')
        if len(proxy_data_list) == 2:
            return 'simple proxy', proxy_data_list
        elif len(proxy_data_list) == 4:
            return 'private proxy', proxy_data_list
        else:
            logger.critical('Тип прокси не определен')


def connect_to_privat_proxy(proxy_data_list):
    login_proxy = proxy_data_list[0]
    password_proxy = proxy_data_list[1]
    ip_proxy = proxy_data_list[2]
    port_proxy = proxy_data_list[3]

    options = webdriver.ChromeOptions()
    proxy = ip_proxy + ':' + port_proxy
    options.add_extension(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Proxy_Auto_Auth.crx'))
    options.add_argument("--proxy-server=http://{}".format(proxy))

    driver = webdriver.Chrome(options=options)

    driver.get("chrome-extension://ggmdpepbjljkkkdaklfihhngmmgmpggp/options.html")

    driver.find_element_by_id("login").send_keys(login_proxy)
    driver.find_element_by_id("password").send_keys(password_proxy)
    driver.find_element_by_id("retry").clear()
    driver.find_element_by_id("retry").send_keys("2")
    driver.find_element_by_id("save").click()
    logger.debug('Прокси успешно подключен')

    return driver


def connect_to_public_proxy(proxy_data_list):
    proxy_ip_port = ':'.join(proxy_data_list)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server=%s' % proxy_ip_port)
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def connect_to_proxy(proxy_file_path):
    # Проверяем, пустой ли файл. Если да - пропускаем установку прокси, если нет - подключаемся к ней

    if os.path.getsize(proxy_file_path) > 0:
        type_proxy, proxy_data_list = define_proxy_type(proxy_file_path)
        if type_proxy == 'private proxy':
            logger.debug('Тип вашего прокси - приватный')
            return connect_to_privat_proxy(proxy_data_list)

        else:
            logger.debug('Тип вашего прокси - открытый')
            return connect_to_public_proxy(proxy_data_list)
    else:
        logger.debug('Вы не задали никакого прокси')
        return webdriver.Chrome()


def driver_settings(proxy_file_path):
    return connect_to_proxy(proxy_file_path)
