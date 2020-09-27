import os
import re
import sys
import time
import json
import requests
import random as r

from loguru import logger
from selenium import webdriver
from collections import OrderedDict
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def main_func():
    logger.remove()
    # настраиваем логгирование

    def debug_only(record):
        return record["level"].name == "DEBUG"

    def critical_only(record):
        return record["level"].name == "CRITICAL"

    def info_only(record):
        return record["level"].name == "INFO"

    logger_format_debug = "<green>{time:DD-MM-YY HH:mm:ss}</> | <bold><blue>{level}</></> | <cyan>{file}:{function}:{line}</> | <blue>{message}</> | <blue>🛠</>"
    logger_format_info = "<green>{time:DD-MM-YY HH:mm:ss}</> | <bold><fg 255,255,255>{level}</></> | <cyan>{file}:{function}:{line}</> | <fg 255,255,255>{message}</> | <fg 255,255,255>✔</>"
    logger_format_critical = "<green>{time:DD-MM-YY HH:mm:ss}</> | <RED><fg 255,255,255>{level}</></> | <cyan>{file}:{function}:{line}</> | <fg 255,255,255><RED>{message}</></> | <RED><fg 255,255,255>❌</></>"

    logger.add(sys.stderr, format=logger_format_debug, level='DEBUG', filter=debug_only)
    logger.add(sys.stderr, format=logger_format_info, level='INFO', filter=info_only)
    logger.add(sys.stderr, format=logger_format_critical, level='CRITICAL', filter=critical_only)
    # logger.add('myfile.log', format=logger_format_debug, level='DEBUG', filter=debug_only)

    # Присваиваем значение переменных

    countries_codes_dict, dict, proxies_dict, numbers_of_countries_list = {}, {}, {}, []
    ID, phone_numbers, sms_code = None, None, None

    # Проверяем, пустой ли файл. Если да - пропускаем установку прокси, если нет - подключаемся к ней

    def type_proxy():
        with open('.' + os.path.join(os.sep, 'yourfiles', 'proxies.txt'), 'r', encoding='utf-8-sig',
                  errors='ignore') as proxies_file:
            for line in proxies_file:
                proxies_list = line.strip('\n').split(':')
                if len(proxies_list) == 2:
                    return 'simple proxy'
                elif len(proxies_list) == 4:
                    return 'private proxy'
                else:
                    logger.critical('Тип прокси не определен')

    def proxy_get():
        if os.path.getsize('.' + os.path.join(os.sep, 'yourfiles', 'proxies.txt')) > 0:
            if type_proxy() == 'private proxy':
                logger.debug('Тип вашего прокси - приватный')
                with open('.' + os.path.join(os.sep, 'yourfiles', 'proxies.txt'), 'r', encoding='utf-8-sig',
                          errors='ignore') as proxies_file:
                    line = proxies_file.readline()
                    proxies_list = line.strip('\n').split(':')
                    login_proxy = proxies_list[0]
                    password_proxy = proxies_list[1]
                    ip_proxy = proxies_list[2]
                    port_proxy = proxies_list[3]

                    options = webdriver.ChromeOptions()
                    PROXY = ip_proxy + ':' + port_proxy
                    options.add_extension("Proxy_Auto_Auth.crx")
                    options.add_argument("--proxy-server=http://{}".format(PROXY))

                    driver = webdriver.Chrome(options=options)

                    driver.get("chrome-extension://ggmdpepbjljkkkdaklfihhngmmgmpggp/options.html")

                    driver.find_element_by_id("login").send_keys(login_proxy)
                    driver.find_element_by_id("password").send_keys(password_proxy)
                    driver.find_element_by_id("retry").clear()
                    driver.find_element_by_id("retry").send_keys("2")
                    driver.find_element_by_id("save").click()
                    logger.debug('Прокси успешно подключен')

                    return driver

            else:
                logger.debug('Тип вашего прокси - открытый')
                with open('.' + os.path.join(os.sep, 'yourfiles', 'proxies.txt'), 'r', encoding='utf-8',
                          errors='ignore') as proxies_file:
                    line = proxies_file.readline()
                    chrome_options = webdriver.ChromeOptions()
                    chrome_options.add_argument('--proxy-server=%s' % line)
                    driver = webdriver.Chrome(options=chrome_options)
                    return driver

        else:
            logger.debug('Вы не задали никакого прокси')
            return webdriver.Chrome

    # проверяем, существует ли proxies.txt

    exist_proxies_file_check = os.path.exists('.' + os.path.join(os.sep, 'yourfiles', 'proxies.txt'))

    # если существует, берем инфу

    def proxy_main():

        if exist_proxies_file_check == True:
            logger.debug('Файл "proxies.txt" существует')

        # если не существует, просим пользователя ввести login:pass:ip:port прокси

        else:
            logger.info('proxies.txt не существует, создаю файл в папке txtfiles')
            with open('.' + os.path.join(os.sep, 'yourfiles', 'proxies.txt'), 'w') as proxies_file:
                logger.info(
                    'Ниже введите прокси в формате login:pass:ip:port. Если не хотите использовать прокси - нажмите Enter')
                proxies_str = input()
                proxies_file.write(proxies_str)
                proxies_file.close()
        return proxy_get()

    # Назначаем финальное значение драйвера

    driver = proxy_main()

    def send_keys(xpath, keys):
        driver.find_element_by_xpath(xpath).send_keys(keys)

    def clear(xpath):
        return driver.find_element_by_xpath(xpath).clear()

    def click(xpath):
        return driver.find_element_by_xpath(xpath).click()

    # запрос статуса номера

    def get_status():
        payload_get_code = {'api_key': f'{token}', 'action': 'getStatus', 'id': f'{ID}'}
        response = requests.get('https://sms-activate.ru/stubs/handler_api.php',
                                params=payload_get_code)
        return response

    # анализ пришедшего ответа

    def response_analise(response):
        if 'STATUS_OK' in response.text:
            logger.debug(f'Смс пришло. Код: {response.text}')
            return response.text
        elif response.text == 'STATUS_WAIT_CODE':
            logger.debug('Ожидаем смс')
            return False
        elif response.text == 'NO_BALANCE':
            logger.critical('Денег нет')
            return False
        elif response.text == 'NO_NUMBERS':
            logger.debug('Нет номеров')
            return 'NO_NUMBERS'
        elif response.text == 'BAD_KEY':
            logger.critical('Токен из файла inf.txt не работает')
            return False
        elif 'ACCESS_NUMBER' in response.text:
            return 'ACCESS_NUMBER'
        elif 'BAD_STATUS' in response.text:
            logger.critical('Что-то не так с ID операции')
            return False
        else:
            logger.critical(f'Что-то пошло не так. Ответ sms-activate: {response.text}')
            return False

    # прием и распаковка кода смс

    def response_next(self):
        sms_code = response_analise(get_status())
        if sms_code == False:
            return False
        else:
            sms_code = sms_code.split(':')[1]
            return sms_code

    def country_get():

        # проверяем, есть ли в файлике заданная страна
        # если пользователь воспользовался подбором дешевой страны:
        if country_name_from_inf == 'False':
            country_code_final = number_of_the_cheapest_country
        # если пользователь не воспользовался подбором дешевой страны:
        else:
            country_code_final = country_code_from_user

        # запрос в сервис для получения номера

        logger.debug(f'Берем страну: {country_name_from_inf} с номером: {country_code_final}')
        payload = {'api_key': f'{token}', 'action': 'getNumber', 'service': 'vk', 'operator': 'any',
                   'country': f'{country_code_final}'}
        g = requests.get('https://sms-activate.ru/stubs/handler_api.php', params=payload)

        if response_analise(g) == 'ACCESS_NUMBER':
            pass

        # если номеров нет

        elif response_analise(g) == 'NO_NUMBERS':
            payload_number_is_ready_request = {'api_key': f'{token}', 'action': 'setStatus', 'status': '8',
                                               'id': f'{ID}'}
            number_is_ready_request = requests.post('https://sms-activate.ru/stubs/handler_api.php',
                                                    params=payload_number_is_ready_request)
            logger.info(f'Отправили запрос на отмену активации: {number_is_ready_request.text}')
            logger.debug('Берем другую страну')

                country_get()  # функция, которая другую страну берет

        else:
            sys.exit()  # заканчиваем работу скрипта

        result = re.split(r':', g.text)

        # разбив полученной инфы на ID и номер

        ID = result[1]
        phone_numbers = re.findall(r'\d{10}$', result[2])[0]
        logger.debug(f'Получили номер: {phone_numbers} и ID операции: {ID}')

        # Находим и вводим страну

        clear('//input[@class="selector_input selected"]')
        send_keys('//input[@class="selector_input selected"]', country_name_from_inf)
        send_keys('//td[@class="selector"]/input[@type="text"]', u'\ue007')

        # находим и вводим телефон в поле ввода, вырезаем и вставляем

        clear('//div[@class="prefix_input_field"]/input[@id="join_phone"]')
        send_keys('//div[@class="prefix_input_field"]/input[@id="join_phone"]', phone_numbers)

        # Ctrl+A, Ctrl+X, Ctrl+V телефонного номера:

        # ActionChains(driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        # ActionChains(driver).key_down(Keys.CONTROL).send_keys('x').key_up(Keys.CONTROL).perform()
        # ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

        # находим и кликаем по кнопке "Получить код"

        click('//button[@id="join_send_phone"]')

        # надо сделать проверку наличия окна "я не робот": //div[@class="popup_box_container"]

        # проверяем наличия div "Номер заблокирован"
        time.sleep(1)

        try:
            driver.find_element_by_xpath("//div[@class='msg_text']")
            logger.info('Вк заблокировал номер')
            payload_number_is_ready_request = {'api_key': f'{token}', 'action': 'setStatus', 'status': '8',
                                               'id': f'{ID}'}
            number_is_ready_request = requests.post('https://sms-activate.ru/stubs/handler_api.php',
                                                    params=payload_number_is_ready_request)
            logger.debug(f'отправили запрос на отмену активации: {number_is_ready_request.text}')
            logger.debug('Берем другую страну')

            ID, phone_numbers = country_get()  # функция, которая другую страну берет

        except NoSuchElementException:
            logger.debug('Вк не заблокировал номер')
            pass

        # проверяем наличия div "Неверный номер телефона. Введите в международном формате"

        try:
            driver.find_element_by_xpath("//div[@class='msg error']")
            logger.info('Неверный номер телефона. Введите в международном формате')

            payload_number_is_ready_request = {'api_key': f'{token}', 'action': 'setStatus', 'status': '8',
                                               'id': f'{ID}'}
            number_is_ready_request = requests.post('https://sms-activate.ru/stubs/handler_api.php',
                                                    params=payload_number_is_ready_request)
            logger.debug('отправили запрос на отмену активации: ', number_is_ready_request.text)

            ID, phone_numbers = country_get()  # функция, которая другую страну берет

        except NoSuchElementException:
            logger.debug('Международный формат - ок')
            pass

        # проверка наличия блока "Мы только что повторно выслали вам смс с кодом", надписи "Введите код" или кнопки "Я не получил код"

        send_code_button = driver.find_element_by_xpath("//div[@id='join_code_row']")

        if send_code_button.is_displayed() == True:
            logger.debug('Div, содержащий "Введите код" доступен')
        else:
            # проверка готовности кнопки "Отправить код с помощью смс"
            logger.debug('Ожидаю появления кнопки для отправки кода с помощью смс')
            WebDriverWait(driver, 140).until(EC.presence_of_element_located((By.XPATH, "//a[@id='join_resend_lnk']")))

            # клик по "Отправить код с помощью смс"

            click('//a[@id="join_resend_lnk"]')
            logger.debug('Нажал "Отправить код с помощью смс"')

        # отправляем запрос: номер готов к получению смс

        payload_number_is_ready_request = {'api_key': f'{token}', 'action': 'setStatus', 'status': '1', 'id': f'{ID}'}
        number_is_ready_request = requests.post('https://sms-activate.ru/stubs/handler_api.php',
                                                params=payload_number_is_ready_request)
        logger.debug(f'отправили запрос на изменения статуса: {number_is_ready_request.text}')

        return ID, phone_numbers

    # удаляем куки и переходим на страницу

    driver.delete_all_cookies()
    driver.get('https://vk.com/')

    # проверяем, существует ли login, pass.txt

    exist_loginpass_file_check = os.path.exists('.' + os.path.join(os.sep, 'yourfiles', 'login, pass.txt'))

    if exist_loginpass_file_check == True:
        logger.debug('Файл "login, pass.txt" существует')
        pass
    else:
        open('.' + os.path.join(os.sep, 'yourfiles', 'login, pass.txt'), 'w', encoding='utf-8')
        logger.info('Файл "login, pass.txt" не существует, создал новый')

    # проверяем, существует ли inf.txt

    exist_inf_file_check = os.path.exists('.' + os.path.join(os.sep, 'yourfiles', 'inf.txt'))

    # если существует, берем инфу

    if exist_inf_file_check == True:
        logger.debug('Файл "inf.txt" существует')
        with open('.' + os.path.join(os.sep, 'yourfiles', 'inf.txt'), 'r', encoding='utf-8-sig',
                  errors='ignore') as url_inf:
            for line in url_inf:
                list_inf = line.strip('\n').split(':')
                dict[list_inf[0]] = list_inf[1]

    # если не существует, просим пользователя ввести токен и номер страны

    else:
        logger.info('inf.txt не существует, создаю файл в папке txtfiles')
        with open('.' + os.path.join(os.sep, 'yourfiles', 'inf.txt'), 'w', encoding='utf-8-sig') as url_inf:
            logger.info('Ниже введите токен вашего аккаунта на sms-activate')
            token = input()
            logger.info(
                'Ниже введите название страны, номер телефона которой хотите арендовать. С большой буквы на русском языке:')
            country_name = input()
            url_inf.write(f'token:{token}\n'
                          f'country_name:{country_name}\n'
                          'Подсказка:если хотите пользоваться автоподбором страны с самой дешевой ценой номера, задайте country_name значение False')
            url_inf.close()

            with open('.' + os.path.join(os.sep, 'yourfiles', 'inf.txt'), 'r', encoding='utf-8-sig') as url_inf:
                for line in url_inf:
                    list_inf = line.strip().split(':')
                    dict[list_inf[0]] = list_inf[1]
    token = dict['token']
    logger.debug(f'Распаковали inf.txt, взяли из него токен: {token}')
    country_name_from_inf = dict.get('country_name')

    # распаковываем коды стран

    with open('.' + os.path.join(os.sep, 'txtfiles', 'countries_code.txt'), 'r', encoding='utf-8-sig',
              errors='ignore') as countries_codes_file:
        for line in countries_codes_file:
            list_inf = line.strip().split(':')
            countries_codes_dict[list_inf[1]] = list_inf[0]
    logger.debug('Распаковали коды стран')
    country_code_from_user = countries_codes_dict[country_name_from_inf]

    # создаем списки имен и фамилий

    name_list = []
    surname_list = []

    # импортируем имена и фамилии их txt-списков python списки и делаем их с большой буквы
    with open('.' + os.path.join(os.sep, 'txtfiles', 'name_rus.txt'), 'r', encoding='utf-8-sig',
              errors='ignore') as inf:
        for eachLine in inf:
            a = eachLine.capitalize().strip().split("\n")
            name_list.append(a)

    with open('.' + os.path.join(os.sep, 'txtfiles', 'surname.txt'), 'r', encoding='utf-8-sig', errors='ignore') as inf:
        for eachLine in inf:
            a = eachLine.capitalize().strip().split("\n")
            surname_list.append(a)

    logger.debug('Распаковали имена и фамилии')

    # рандомно выбираем имя и фамилию и вставляем в инпуты

    name = r.choice(name_list)
    name = name[0]
    surname = r.choice(surname_list)
    surname = surname[0]
    send_keys('//input[@id="ij_first_name"]', name)
    send_keys('//input[@id="ij_last_name"]', surname)

    # находим и кликаем по полю "день", из выпадающего списка рандомно выбираем день от 1 до 28. Кликаем

    click("//div[@id='container1']")
    day_random_count = r.randint(1, 28)
    day_count = driver.find_element_by_xpath(
        "//ul[@id='list_options_container_1']/li[text() = '%s']" % day_random_count)
    day_count.click()

    # находим и кликаем по полю "месяц", из выпадающего списка рандомно выбираем месяц. Кликаем

    click("//div[@id='container2']")
    months_list = ['Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня', 'Июля', 'Августа', 'Сентября', 'Октября',
                   'Ноября', 'Декабря']
    month = r.choice(months_list)
    month_li = driver.find_element_by_xpath("//ul[@id='list_options_container_2']/li[text() = '%s']" % month)
    month_li.click()

    # находим и кликаем по полю "год", из выпадающего списка рандомно выбираем год от 1980 до 2001. Кликаем

    click("//div[@id='container3']")
    year_random_count = r.randint(1980, 2001)
    year_li = driver.find_element_by_xpath("//ul[@id='list_options_container_3']/li[text() = '%s']" % year_random_count)
    year_li.click()

    logger.debug('Заполнили поля имени, фамилии, дня, месяца, года')

    # клик на кнопку "зарегистрироваться"

    click("//button[@id='ij_submit']")
    time.sleep(1)
    logger.debug('Нажали "зарегистрироваться"')

    # проверка, открылась ли следующая страница

    reg_url = driver.current_url
    if reg_url == "https://vk.com/":
        tab_index = r.randint(-1, 0)
        sex_div = driver.find_element_by_xpath("//div[@id='ij_sex_row']/div[@tabindex='%s']" % tab_index)
        sex_div.click()
        click("//button[@id='ij_submit']")

    # проверяем, хочет ли человек автоподбор самой дешевой страны

    if country_name_from_inf != 'False':  # проверяем, есть ли в файлике inf.txt заданная страна
        logger.debug('Автоподбор страны с самым дешевым номером отключен')
        pass

    else:

        # находим самый дешевый номер
        # отправляем запрос на получение инфы о номерах

        payload = {'api_key': f'{token}', 'action': 'getPrices', 'service': 'vk', 'operator': 'any'}
        g = requests.get('https://sms-activate.ru/stubs/handler_api.php', params=payload)
        response_dic = json.loads(g.text.replace("'", '"'))  # переводим строку в json, чтоб сделать словарем

        # создаем и заполняем словарик: {номер страны: цена телефона этой страны}

        number_cost_dic = {}
        for elem in response_dic:
            if response_dic[elem] == {}:  # проверка, не пустая ли эта часть словаря
                continue
            else:
                if response_dic[elem]['vk']['count'] < 10:  # проверка, есть ли инфа и 10 доступных номеров
                    continue
                else:
                    number_cost_dic[elem] = response_dic[elem]['vk'][
                        'cost']  # добавляем в словарь значения

        # сортируем словарик по возрастанию цены стран

        ordered_number_cost_dic = OrderedDict(
            sorted(number_cost_dic.items(), key=lambda t: t[1]))

        # создаем список с номерами стран в порядке возрастания цены

        for number_of_country in ordered_number_cost_dic:
            numbers_of_countries_list.append(number_of_country)

        logger.debug(f'создали список стран в порядке возрастания цены: {numbers_of_countries_list}')

        number_of_the_cheapest_country = numbers_of_countries_list[0]  # берем первую страну из словарика
        numbers_of_countries_list.remove(number_of_the_cheapest_country)  # удаляем первую страну из словарика
        logger.debug(number_of_the_cheapest_country)

    # вызываем функцию, которая определяет страну

    ID, phone_numbers = country_get()

    # ждем, пока не придет код

    try:
        WebDriverWait(driver, 300, 30).until(response_next, "смска пришла???")
    except TimeoutException:
        click('//a[@id="join_other_phone"]')
        logger.info('Нажал на "Изменить номер"')

        payload_number_is_ready_request = {'api_key': f'{token}', 'action': 'setStatus', 'status': '8', 'id': f'{ID}'}
        number_is_ready_request = requests.post('https://sms-activate.ru/stubs/handler_api.php',
                                                params=payload_number_is_ready_request)
        logger.debug(f'отправили запрос на отмену активации: {number_is_ready_request.text}')

        logger.debug('Беру другую страну, ибо время вышло')
        ID, phone_numbers = country_get()

    # присваиваем sms_code значение пришедшего кода

    sms_code = response_next(driver)

    # вводим код в input "Введите код"

    send_keys('//input[@id="join_code"]', sms_code)

    time.sleep(1)

    # клик по кнопке "Отправить код"

    click('//button[@id="join_send_code"]')

    time.sleep(1)

    phone_numbers_str = str(phone_numbers)

    # вводим пароль

    password = ''.join(
        [r.choice(list('123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM')) for x in range(12)])
    send_keys('//input[@id="join_pass"]', password)

    # клик "Войти на сайт"

    click("//button[@id='join_send_pass']")

    # записываем в файлик логин и пароль

    login_pass = name + '&' + surname + '#' + phone_numbers_str + ':' + password
    with open('.' + os.path.join(os.sep, 'yourfiles', 'login, pass.txt'), 'a') as passLoginFile:
        passLoginFile.writelines('\n' + login_pass)
    logger.debug(f'Информация о созданном аккаунте находится в директории autoreg/txtfiles/login, pass.txt')
    logger.debug(f'Аккаунт: {login_pass}')

    # Нажимаем "Пропустить"

    time.sleep(2)
    click('//a[@class="join_skip_link"]')


main_func()
