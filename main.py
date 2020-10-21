from datetime import datetime
import os
import sys
import time
import json

import phonenumbers
import requests
import random as r
import yaml

from pathlib import Path
from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from mimesis import Person
from mimesis.enums import Gender

from py_files.add_proxy import driver_settings
from py_files.some_functions import set_logger

# Присваиваем значение переменных
enumerate_list_of_countries_numbers_prices = []
INF_FILE_PATH = Path('your_files', 'inf.yml')
COUNTRY_CODES_FILE_PATH = Path('text_files', 'countries_codes.yml')


def exit_code(status='Останавливаю работу скрипта'):
    logger.critical(f'Причина: {status}')
    driver.quit()
    sys.exit()


def send_keys(xpath, keys):
    driver.find_element_by_xpath(xpath).send_keys(keys)


def clear(xpath):
    return driver.find_element_by_xpath(xpath).clear()


def click(xpath):
    return driver.find_element_by_xpath(xpath).click()


def inf_file_unpack(path_to_file):
    with open(path_to_file, 'r', encoding='UTF-8') as inf_file:
        inf_file_dic = yaml.load(inf_file, Loader=yaml.FullLoader)
        logger.debug(f'Распаковали inf.txt')
        token = inf_file_dic['token']
        logger.debug(f'Ваш токен: {token}')
        country_name = inf_file_dic['country_name']
        country_auto_select = inf_file_dic['country_auto_select']
        logger.debug(f'Выбранная страна: {country_name}')
        sex = inf_file_dic['sex']
        logger.debug(f'Выбранный пол: {sex}')
        person = Person('ru')
        if sex == 'FEMALE':
            name = person.name(gender=Gender.FEMALE)
            surname = person.surname(gender=Gender.FEMALE)
        else:
            name = person.name(gender=Gender.MALE)
            surname = person.surname(gender=Gender.MALE)

        return token, country_name, name, surname, country_auto_select


def auto_selection_country():
    # находим самый дешевый номер
    # отправляем запрос на получение инфы о номерах
    payload = {'api_key': f'{token}', 'action': 'getPrices', 'service': 'vk', 'operator': 'any'}
    response_get_prices_json = requests.get('https://sms-activate.ru/stubs/handler_api.php', params=payload)
    response_dic = json.loads(
        response_get_prices_json.text.replace("'", '"'))  # переводим строку в json, чтоб сделать словарем

    # распаковываем файлик, чтоб считывать из него название стран
    with open(Path('text_files', 'countries_codes_reverse.yml'), 'r', encoding='UTF-8') as countries_codes_file:
        countries_codes_reverse_dict = yaml.load(countries_codes_file, Loader=yaml.FullLoader)
        logger.debug(f'Распаковали "countries_codes_reverse.yml"')

    # создаем и заполняем вложенный список: [['страна', [номер страны, цена телефона этой страны]]]
    for country_number in response_dic:
        if response_dic[country_number] == {}:  # проверка, не пустая ли эта часть словаря
            continue
        else:
            if response_dic[country_number]['vk']['count'] < 50:  # проверка, есть ли инфа и 10 доступных номеров
                continue
            else:
                try:
                    country_name = countries_codes_reverse_dict[int(country_number)]
                    cost = response_dic[country_number]['vk']['cost']
                    count_of_numbers = response_dic[country_number]['vk']['count']
                    enumerate_list_of_countries_numbers_prices.append(
                        [{'country name': country_name},
                         {'country number': int(country_number), 'cost': cost, 'count of numbers': count_of_numbers}])
                except KeyError:
                    pass

    # создаем список с номерами стран в порядке возрастания цены
    def sort_list(i):
        return i[1]['cost']

    enumerate_list_of_countries_numbers_prices.sort(key=sort_list)

    # записываем список цен в файл
    with open(Path('your_files', 'sorted_prices.yml'), 'w', encoding='utf-8') as sorted_prices_file:
        sorted_prices_file.write('#' + str(datetime.today()) + '\n' + '\n')
        yaml.dump(enumerate_list_of_countries_numbers_prices, sorted_prices_file, allow_unicode=True)
    logger.debug(
        'Создали список стран по порядку увеличения цены аренды номера. Результаты в your_files/sorted_prices.yml')

    return enumerate_list_of_countries_numbers_prices


# удаляем из списка первую страну и кладем ее номер в переменную
def cheapest_country_select(enumerate_countries_list):
    cheapest_country_list = enumerate_countries_list[0]
    number_of_the_cheapest_country = cheapest_country_list[1]['country number']  # берем первую страну из списка
    country_name = cheapest_country_list[0]['country name']  # берем первую страну из списка
    cost = cheapest_country_list[1]['cost']
    enumerate_countries_list.remove(
        enumerate_countries_list[0])  # удаляем первую страну из списка
    logger.debug(
        f'Взяли страну: "{country_name}", с номером: {number_of_the_cheapest_country}, по цене: {cost}₽')
    return enumerate_countries_list, number_of_the_cheapest_country, country_name


# распаковываем коды стран
def countries_codes_file_unpack(path_to_file, country_name):
    with open(path_to_file, 'r', encoding='UTF-8') as countries_codes_file:
        countries_codes_dict = yaml.load(countries_codes_file, Loader=yaml.FullLoader)
        # проверяем, хочет ли человек автоподбор самой дешевой страны
        country_number = countries_codes_dict[country_name]
        logger.debug(f'Распаковали "countries_codes.inf"')
        logger.debug(f'Номер страны "{country_name}": {country_number}')
        return country_number


# проверяем IP, с которого подключаемся
def print_ip():
    try:
        driver.get('https://2ip.ru/')
        ip = driver.find_element_by_xpath('//div[@class="ip"]/span').text
        logger.debug(f'Ваш прокси: {ip}')
    except NoSuchElementException:
        logger.critical('2ip не прогрузился')
        return '2ip не прогрузился'


def get_number_request(country_code, privat_key):
    payload = {'api_key': f'{privat_key}', 'action': 'getNumber', 'service': 'vk', 'operator': 'any',
               'country': f'{country_code}'}
    response_get_number = requests.get('https://sms-activate.ru/stubs/handler_api.php', params=payload)
    return response_get_number


# анализ пришедшего ответа
def get_number_response_analyze(response_get_number):
    if 'ACCESS_NUMBER' in response_get_number.text:
        logger.debug('Запрос прошел. Все ок')
        return True
    elif response_get_number.text == 'NO_BALANCE':
        logger.critical('Денег нет')
        exit_code()
    elif response_get_number.text == 'NO_NUMBERS':
        logger.debug('Нет номеров')
    elif response_get_number.text == 'BAD_KEY':
        logger.critical('Токен из файла inf.yml не работает')
        exit_code()
    elif 'BAD_STATUS' in response_get_number.text:
        logger.critical('Что-то не так с ID операции')
        exit_code()
    else:
        logger.critical(f'Что-то пошло не так. Ответ sms-activate: {response_get_number.text}')
        exit_code()
    return False


# вытаскиваем id и номер телефона из запроса
def get_id_and_phone_number(response_get_number):
    split_response = response_get_number.text.split(':')
    id, phone_numbers_with_country_code = split_response[1], split_response[2]
    phone_numbers_parse = phonenumbers.parse('+{}'.format(phone_numbers_with_country_code))
    phone_numbers = phone_numbers_parse.national_number
    logger.debug(f'Получили номер: {phone_numbers} и ID операции: {id}')
    return id, phone_numbers


def send_request_set_status_canceling_activation(token, id):
    payload_number_is_cancel_request = {'api_key': f'{token}', 'action': 'setStatus', 'status': '8', 'id': f'{id}'}
    number_is_cancel_response = requests.post('https://sms-activate.ru/stubs/handler_api.php',
                                              params=payload_number_is_cancel_request)
    logger.debug(f'отправили запрос на отмену активации: {number_is_cancel_response.text}')
    return number_is_cancel_response


# меняем статус номера (номер готов к принятию смс)
def send_set_status_ready_request(id, token):
    payload_number_is_ready_request = {'api_key': f'{token}', 'action': 'setStatus', 'status': '1', 'id': f'{id}'}
    requests.post('https://sms-activate.ru/stubs/handler_api.php',
                  params=payload_number_is_ready_request)


# узнаем статус номера
def send_get_status_request(token, id):
    payload_get_code = {'api_key': f'{token}', 'action': 'getStatus', 'id': f'{id}'}
    response_get_status = requests.get('https://sms-activate.ru/stubs/handler_api.php',
                                       params=payload_get_code)
    return response_get_status


# узнаем, пришла ли смс
def get_status_response_analysis(response_get_status):
    if 'STATUS_OK' in response_get_status.text:
        logger.debug(f'Смс пришло')
        return True
    elif response_get_number.text == 'STATUS_WAIT_CODE':
        logger.debug('Ожидаем смс')
        return False


# узнаем статус и анализируем ответ
def send_get_status_request_and_analyze_response(self):
    response_get_status = send_get_status_request(token, id)
    return get_status_response_analysis(response_get_status)


# вытаскиваем из ответа смс-код
def get_sms_code_analysis(id, token):
    response_get_status = send_get_status_request(token, id)
    sms_code = response_get_status.text.split(':')[1]
    return sms_code


# проверка, заблокировал ли вк номер или сказал, что формат номера неверный
def is_number_blocked_or_wrong_format():
    try:
        time.sleep(1)
        driver.find_element_by_xpath("//div[@class='msg_text']")
        return False
    except NoSuchElementException:
        logger.debug('Вк не заблокировал номер')
        pass

    # проверяем наличия div "Неверный номер телефона. Введите в международном формате"

    try:
        time.sleep(1)
        driver.find_element_by_xpath("//div[@class='msg error']")
        return False
    except NoSuchElementException:
        logger.debug('Международный формат - ок')
        pass
    return True


# берем другой номер
def take_another_number(country_number, token):
    attempt_count = 0
    while attempt_count < 10:
        attempt_count += 1
        response_get_number = get_number_request(country_number, token)
        if not get_number_response_analyze(response_get_number):
            take_another_country(enumerate_list_of_countries_numbers_prices)
            driver.quit()
            exit_code()

        id, phone_numbers = get_id_and_phone_number(response_get_number)
        clear('//div[@class="prefix_input_field"]/input[@id="join_phone"]')
        clear('//div[@class="prefix_input_field"]/input[@id="join_phone"]')
        send_keys('//div[@class="prefix_input_field"]/input[@id="join_phone"]', phone_numbers)
        click('//button[@id="join_send_phone"]')
        if is_number_blocked_or_wrong_format():
            return id
        send_request_set_status_canceling_activation(token, id)
    return False


# берем другую страну. Эта часть кода находится в разработке))))
def take_another_country(enumerate_list_of_countries_numbers_prices):
    enumerate_list_of_countries_numbers_prices, country_number, country_name = cheapest_country_select(
        enumerate_list_of_countries_numbers_prices)
    # countries_not_allowed = ['Камбоджа', 'США', 'Индонезия', 'Сьерра-Леоне', 'Англия', 'Венесуэла']
    # for i in countries_not_allowed:
    #     while i == country_name:
    #         enumerate_list_of_countries_numbers_prices, country_number, country_name = cheapest_country_select(
    #             enumerate_list_of_countries_numbers_prices)

    clear('//input[@class="selector_input selected"]')
    send_keys('//input[@class="selector_input selected"]', country_name)
    send_keys('//td[@class="selector"]/input[@type="text"]', u'\ue007')
    take_another_number(country_number, token)
    return enumerate_list_of_countries_numbers_prices, country_number, country_name


set_logger()

token, country_name, name, surname, country_auto_select = inf_file_unpack(INF_FILE_PATH)
country_number = countries_codes_file_unpack(COUNTRY_CODES_FILE_PATH, country_name)
if country_auto_select:
    logger.debug('Включен автоподбор страны с самым дешевым номером')
    enumerate_list_of_countries_numbers_prices, country_number, country_name = cheapest_country_select(
        auto_selection_country())

# Назначаем драйвер
driver = driver_settings(Path('your_files', 'proxies.yml'))

# удаляем куки и переходим на страницу
driver.delete_all_cookies()
print_ip()
driver.get('https://vk.com/')

# вставляем имя и фамилию
WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//input[@id="ij_first_name"]')))
send_keys('//input[@id="ij_first_name"]', name)
send_keys('//input[@id="ij_last_name"]', surname)

# находим и кликаем по полю "день", из выпадающего списка рандомно выбираем день от 1 до 28. Кликаем
click("//div[@id='container1']")
driver.find_element_by_xpath(
    f"//ul[@id='list_options_container_1']/li[text() = {r.randint(1, 28)}]").click()

# находим и кликаем по полю "месяц", из выпадающего списка рандомно выбираем месяц. Кликаем
click("//div[@id='container2']")
driver.find_element_by_css_selector(f"#list_options_container_2 :nth-child({r.randint(2, 13)})").click()

# находим и кликаем по полю "год", из выпадающего списка рандомно выбираем год от 1980 до 2001. Кликаем
click("//div[@id='container3']")
driver.find_element_by_xpath(f"//ul[@id='list_options_container_3']/li[text() = {r.randint(1980, 2001)}]").click()
logger.debug('Заполнили поля имени, фамилии, дня, месяца, года')

# клик на кнопку "зарегистрироваться"
click("//button[@id='ij_submit']")
logger.debug('Нажали "зарегистрироваться"')

# проверка, открылась ли следующая страница. Если появилось поле ввода пола - заполняем
try:
    WebDriverWait(driver, 2).until(
        EC.element_to_be_clickable((By.XPATH, f"//div[@id='ij_sex_row']/div[@tabindex='{r.randint(-1, 0)}']")))
    logger.debug('Вылезло поле определения пола')
    driver.find_element_by_xpath(f"//div[@id='ij_sex_row']/div[@tabindex='{r.randint(-1, 0)}']").click()
    click("//button[@id='ij_submit']")
except BaseException:
    logger.debug('Поле определения пола скрыто')

# отправляем запрос на получение номера телефона
response_get_number = get_number_request(country_number, token)
if not get_number_response_analyze(response_get_number):
    exit_code('Что-то с запросом на выдачу номера')

# выдергиваем id и номер телефона из ответа
id, phone_numbers = get_id_and_phone_number(response_get_number)
response_get_status = send_get_status_request(token, id)

WebDriverWait(driver, 5).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, '.selector_input')))

# Находим и вводим страну
clear('//input[@class="selector_input selected"]')
send_keys('//input[@class="selector_input selected"]', country_name)
send_keys('//td[@class="selector"]/input[@type="text"]', u'\ue007')

# Находим и вводим телефон в input
clear('//div[@class="prefix_input_field"]/input[@id="join_phone"]')
send_keys('//div[@class="prefix_input_field"]/input[@id="join_phone"]', phone_numbers)

# кликаем по кнопке "Получить код"
click('//button[@id="join_send_phone"]')
time.sleep(1)

# проверка, пропускает ли вк номер
if not is_number_blocked_or_wrong_format():
    id = take_another_number(country_number, token)
    while id is False:
        enumerate_list_of_countries_numbers_prices, country_number, country_name = take_another_country(
            enumerate_list_of_countries_numbers_prices)
# проверка готовности кнопки "Отправить код с помощью смс"
send_code_button = driver.find_element_by_xpath("//div[@id='join_code_row']")
if send_code_button.is_displayed():
    logger.debug('Div, содержащий "Введите код" доступен')
else:
    # ожидание готовности кнопки "Отправить код с помощью смс"
    logger.debug('Ожидаю появления кнопки для отправки кода с помощью смс. Время ожидения - 2 минуты')
    WebDriverWait(driver, 140).until(EC.presence_of_element_located((By.XPATH, "//a[@id='join_resend_lnk']")))

    # клик по "Отправить код с помощью смс"
    click('//a[@id="join_resend_lnk"]')
    logger.debug('Нажал "Отправить код с помощью смс"')
    send_set_status_ready_request(id, token)
    logger.debug('Изменил статус активации на "ready"')
try:
    logger.debug('Ожидаю смс-кода')
    WebDriverWait(driver, 300, 5).until(send_get_status_request_and_analyze_response, "Смска не пришла")
except TimeoutException:

    send_request_set_status_canceling_activation(token, id)
    id = take_another_number(country_number, token)
    if not id:
        enumerate_list_of_countries_numbers_prices, country_number, country_name = take_another_country(
            enumerate_list_of_countries_numbers_prices)

sms_code = get_sms_code_analysis(id, token)

# вводим код в input "Введите код"
send_keys('//input[@id="join_code"]', sms_code)

time.sleep(1)

# клик по кнопке "Отправить код"
click('//button[@id="join_send_code"]')
phone_numbers_str = str(phone_numbers)

# вводим пароль
password = Person('en').password(length=12)
send_keys('//input[@id="join_pass"]', password)

# клик "Войти на сайт"
try:
    WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#join_send_pass')))
except BaseException:
    logger.info('Кнопки "Войти на сайт не дождались"')
click("//button[@id='join_send_pass']")

# записываем в файлик логин и пароль
login_pass = name + '&' + surname + '#' + phone_numbers_str + ':' + password
with open(Path('your_files', 'login, pass.txt'), 'a', encoding='UTF-8') as passLoginFile:
    passLoginFile.write(login_pass + '\n')
logger.debug(f'Аккаунт: {login_pass}')
logger.debug(f'Информация о созданном аккаунте находится в директории autoreg/your_files/login, pass.txt')
time.sleep(2)

# Нажимаем "Пропустить"
click('//a[@class="join_skip_link"]')

time.sleep(20)
driver.quit()
