from datetime import datetime
import os
import re
import sys
import time
import json
import requests
import random as r
import yaml

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
ENUMERATE_LIST_OF_COUNTRIES_NUMBERS_PRICES = []
countries_codes_dict, dict, proxies_dict = {}, {}, {}
INF_FILE_PATH = os.path.join('your_files', 'inf.yml')
COUNTRY_CODES_FILE_PATH = os.path.join('text_files', 'countries_codes.yml')


def exit_code(status):
    logger.debug('Останавливаю работу скрипта')
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

        return token, country_name, name, surname


def auto_selection_country():
    # находим самый дешевый номер
    # отправляем запрос на получение инфы о номерах
    payload = {'api_key': f'{token}', 'action': 'getPrices', 'service': 'vk', 'operator': 'any'}
    response_get_prices_json = requests.get('https://sms-activate.ru/stubs/handler_api.php', params=payload)
    response_dic = json.loads(
        response_get_prices_json.text.replace("'", '"'))  # переводим строку в json, чтоб сделать словарем

    # распаковываем файлик, чтоб считывать из него название стран
    with open(os.path.join('text_files', 'countries_codes_reverse.yml'), 'r', encoding='UTF-8') as countries_codes_file:
        countries_codes_reverse_dict = yaml.load(countries_codes_file, Loader=yaml.FullLoader)
        logger.debug(f'Распаковали "countries_codes_reverse.yml"')

    # создаем и заполняем вложенный список: [['страна', [номер страны, цена телефона этой страны]]]
    for country_number in response_dic:
        if response_dic[country_number] == {}:  # проверка, не пустая ли эта часть словаря
            continue
        else:
            if response_dic[country_number]['vk']['count'] < 10:  # проверка, есть ли инфа и 10 доступных номеров
                continue
            else:
                country_name = countries_codes_reverse_dict[int(country_number)]
                ENUMERATE_LIST_OF_COUNTRIES_NUMBERS_PRICES.append(
                    [country_name, [int(country_number), response_dic[country_number]['vk']['cost']]])

    # создаем список с номерами стран в порядке возрастания цены
    def sort_list(i):
        return i[1][1]

    ENUMERATE_LIST_OF_COUNTRIES_NUMBERS_PRICES.sort(key=sort_list)

    # записываем список цен в файл
    with open(os.path.join('your_files', 'sorted_prices.yml'), 'w', encoding='utf-8') as sorted_prices_file:
        sorted_prices_file.write('#' + str(datetime.today()) + '\n' + '\n')
        yaml.dump(ENUMERATE_LIST_OF_COUNTRIES_NUMBERS_PRICES, sorted_prices_file, allow_unicode=True)
    logger.debug(
        'Создали список стран по порядку увеличения цены аренды номера. Результаты в your_files/sorted_prices.yml')

    return ENUMERATE_LIST_OF_COUNTRIES_NUMBERS_PRICES


# удаляем из списка первую страну и кладем ее номер в переменную
def cheapest_country_select(enumerate_countries_list):
    cheapest_country_list = enumerate_countries_list[0]
    number_of_the_cheapest_country = cheapest_country_list[1][0]  # берем первую страну из списка
    enumerate_countries_list.remove(
        enumerate_countries_list[0])  # удаляем первую страну из списка
    logger.debug(
        f'Взяли страну: "{cheapest_country_list[0]}", с номером: {number_of_the_cheapest_country}, по цене: {cheapest_country_list[1][1]}₽')
    return enumerate_countries_list, number_of_the_cheapest_country


# распаковываем коды стран
def countries_codes_file_unpack(path_to_file, country_name):
    with open(path_to_file, 'r', encoding='UTF-8') as countries_codes_file:
        countries_codes_dict = yaml.load(countries_codes_file, Loader=yaml.FullLoader)
        # проверяем, хочет ли человек автоподбор самой дешевой страны
        if country_name != False:
            country_number = countries_codes_dict[country_name]
            logger.debug(f'Распаковали "countries_codes.txt"')
            logger.debug(f'Номер страны "{country_name}": {country_number}')
            return country_number
        else:
            return None


# проверяем IP, с которого подключаемся
def ip_check():
    try:
        driver.get('https://2ip.ru/')
        ip = driver.find_element_by_xpath('//div[@class="ip"]/span').text
        logger.debug(f'Ваш прокси: {ip}')
        return ip
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
    elif response_get_number.text == 'NO_NUMBERS':
        logger.debug('Нет номеров')
    elif response_get_number.text == 'BAD_KEY':
        logger.critical('Токен из файла inf.txt не работает')
    elif 'BAD_STATUS' in response_get_number.text:
        logger.critical('Что-то не так с ID операции')
    else:
        logger.critical(f'Что-то пошло не так. Ответ sms-activate: {response_get_number.text}')
    return False


# вытаскиваем id и номер телефона из запроса
def get_id_and_phone_number(response_get_number):
    split_response = re.split(r':', response_get_number.text)
    id = split_response[1]
    phone_numbers = re.findall(r'\d{10}$', split_response[2])[0]
    logger.debug(f'Получили номер: {phone_numbers} и ID операции: {id}')
    return id, phone_numbers


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
        driver.find_element_by_xpath("//div[@class='msg_text']")
        exit_code('Вк заблокировал номер')
        return False
    except NoSuchElementException:
        logger.debug('Вк не заблокировал номер')
        pass

    # проверяем наличия div "Неверный номер телефона. Введите в международном формате"

    try:
        driver.find_element_by_xpath("//div[@class='msg error']")
        exit_code('Неверный номер телефона. Введите в международном формате')
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
        if get_number_response_analyze(response_get_number) == False:
            driver.quit()
            exit_code('')

        id, phone_numbers = get_id_and_phone_number(response_get_number)
        clear('//div[@class="prefix_input_field"]/input[@id="join_phone"]')
        send_keys('//div[@class="prefix_input_field"]/input[@id="join_phone"]', phone_numbers)
        if is_number_blocked_or_wrong_format:
            return id
    exit_code('Было сделано 10 неудачных попыток получения номера')


# берем другую страну. Эта часть кода находится в разработке))))
# def take_another_country():
#     ENUMERATE_LIST_OF_COUNTRIES_NUMBERS_PRICES, country_number = cheapest_country_select(
#         ENUMERATE_LIST_OF_COUNTRIES_NUMBERS_PRICES)
#     return country_number


set_logger()

token, country_name, name, surname = inf_file_unpack(INF_FILE_PATH)
country_number = countries_codes_file_unpack(COUNTRY_CODES_FILE_PATH, country_name)
if country_number == None:
    logger.debug('Включен автоподбор страны с самым дешевым номером')
    ENUMERATE_LIST_OF_COUNTRIES_NUMBERS_PRICES, country_number = cheapest_country_select(auto_selection_country())

# Назначаем драйвер
driver = driver_settings(os.path.join('your_files', 'proxies.yml'))

# удаляем куки и переходим на страницу
driver.delete_all_cookies()
ip_check()
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
months_list = ['Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня', 'Июля', 'Августа', 'Сентября', 'Октября',
               'Ноября', 'Декабря']
driver.find_element_by_xpath(f"//ul[@id='list_options_container_2']/li[text() = '{r.choice(months_list)}']").click()

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
        EC.presence_of_element_located((By.XPATH, "//div[@id='ij_sex_row']/div[@tabindex='{r.randint(-1, 0)}']")))
    logger.debug('Вылезло поле определения пола')
    driver.find_element_by_xpath(f"//div[@id='ij_sex_row']/div[@tabindex='{r.randint(-1, 0)}']").click()
    click("//button[@id='ij_submit']")
except:
    logger.debug('Поле определения пола скрыто')

# отправляем запрос на получение номера телефона
response_get_number = get_number_request(country_number, token)
if get_number_response_analyze(response_get_number) == False:
    exit_code('Что-то с запросом на выдачу номера')

# выдергиваем id и номер телефона из ответа
id, phone_numbers = get_id_and_phone_number(response_get_number)
response_get_status = send_get_status_request(token, id)

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
if is_number_blocked_or_wrong_format() == False:
    id = take_another_number(country_number, token)

# проверка готовности кнопки "Отправить код с помощью смс"
send_code_button = driver.find_element_by_xpath("//div[@id='join_code_row']")
if send_code_button.is_displayed() == True:
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

    payload_number_is_ready_request = {'api_key': f'{token}', 'action': 'setStatus', 'status': '8', 'id': f'{id}'}
    number_is_ready_request = requests.post('https://sms-activate.ru/stubs/handler_api.php',
                                            params=payload_number_is_ready_request)
    logger.debug(f'отправили запрос на отмену активации: {number_is_ready_request.text}')
    id = take_another_number(country_number, token)

sms_code = get_sms_code_analysis(id, token)

# вводим код в input "Введите код"
send_keys('//input[@id="join_code"]', sms_code)

time.sleep(1)

# клик по кнопке "Отправить код"
click('//button[@id="join_send_code"]')
time.sleep(1)
phone_numbers_str = str(phone_numbers)

# вводим пароль
password = Person('en').password(length=12)
send_keys('//input[@id="join_pass"]', password)

# клик "Войти на сайт"
click("//button[@id='join_send_pass']")

# записываем в файлик логин и пароль
login_pass = name + '&' + surname + '#' + phone_numbers_str + ':' + password
with open('.' + os.path.join(os.sep, 'your_files', 'login, pass.txt'), 'a', encoding='UTF-8') as passLoginFile:
    passLoginFile.write(login_pass + '\n')
logger.debug(f'Аккаунт: {login_pass}')
logger.debug(f'Информация о созданном аккаунте находится в директории autoreg/your_files/login, pass.txt')
time.sleep(2)

# Нажимаем "Пропустить"
click('//a[@class="join_skip_link"]')

time.sleep(20)
driver.quit()
