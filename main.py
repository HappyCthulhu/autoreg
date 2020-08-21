from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import random as r
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
import time, requests, re, os, json
from selenium.webdriver.common.action_chains import ActionChains
from collections import OrderedDict

# def login():
#     driver = webdriver.Chrome('C:\Python\Selenium\chromedriver.exe')
#     driver.get('https://vk.com/')
#     phoneOrEmail_input = driver.find_element_by_xpath('//input[@id="index_email"]')
#     password_input = driver.find_element_by_xpath('//input[@id="index_pass"]')
#
#     phoneOrEmail_input.send_keys('+77079668226')
#     password_input.send_keys('huy7891')
#
#     login_button = driver.find_element_by_xpath('//button[@class="index_login_button flat_button button_big_text"]')
#     login_button.click()

# назначаем переменную для вебдрайвера
driver = webdriver.Chrome('.' + os.path.join(os.sep, 'chromedriver'))
driver.delete_all_cookies()
driver.get('https://vk.com/')
ID = 0
codeList = []


def sendKeys(xPath, keys):
    driver.find_element_by_xpath(xPath).send_keys(keys)


def clear(xPath):
    return driver.find_element_by_xpath(xPath).clear()


def click(xPath):
    return driver.find_element_by_xpath(xPath).click()


def checkNumbers(request):
    if request.text == 'NO_NUMBERS':
        print('нет номеров')
    else:
        print('Доступные номера есть')
        return True

    # отправляем запрос: получить смс-код


def reg():

    # распаковываем txt-файл inf в словарь

    dict = {}
    with open('.' + os.path.join(os.sep, 'names', 'inf.txt'), 'r') as UrInf:
        for line in UrInf:
            listInf = line.strip().split(':')
            dict[listInf[0]] = listInf[1]

    token = dict.get('token')
    print('распаковали txt-файл, взяли из него токен: ', token)

    # распаковываем коды стран

    countriesCodesDic = {}
    with open('.' + os.path.join(os.sep, 'names', 'countries_code.txt'), 'r', encoding='utf-8',
              errors='ignore') as countriesCodesFile:
        for line in countriesCodesFile:
            listInf = line.strip().split(':')
            countriesCodesDic[listInf[0]] = listInf[1]
    print('распаковали коды стран')

    # проверка статуса


    def getStatus(self):
        payloadGetCode = {'api_key': f'{token}', 'action': 'getStatus', 'id': f'{ID}'}
        getCodeRequest = requests.post('https://sms-activate.ru/stubs/handler_api.php',
                                      params=payloadGetCode)
        codeList.append(re.split(r':', getCodeRequest.text))
        print('getCodeRequest.text:', getCodeRequest.text)
        if getCodeRequest == 'STATUS_OK':
            print('статус ок')
            return True
        else:
            print('статус не ок')
            return False

    # создаем списки имен и фамилий

    name_list = []
    surname_list = []

    # импортируем имена и фамилии их txt-списков python списки и делаем их с большой буквы
    with open('.' + os.path.join(os.sep, 'names', 'name_rus.txt'), 'r', encoding='utf-8', errors='ignore') as inf:
        for eachLine in inf:
            a = eachLine.capitalize().strip().split("\n")
            name_list.append(a)

    with open('.' + os.path.join(os.sep, 'names', 'surname.txt'), 'r', encoding='utf-8', errors='ignore') as inf:
        for eachLine in inf:
            a = eachLine.capitalize().strip().split("\n")
            surname_list.append(a)

    print('Распаковали имена и фамилии')

    # рандомно выбираем имя и фамилию и вставляем в инпуты

    sendKeys('//input[@id="ij_first_name"]', r.choice(name_list))
    sendKeys('//input[@id="ij_last_name"]', r.choice(surname_list))

    # находим и кликаем по полю "день", из выпадающего списка рандомно выбираем день от 1 до 28. Кликаем

    click("//div[@id='container1']")
    dayRandomCount = r.randint(1, 28)
    dayCount = driver.find_element_by_xpath("//ul[@id='list_options_container_1']/li[text() = '%s']" % dayRandomCount)
    dayCount.click()

    # находим и кликаем по полю "месяц", из выпадающего списка рандомно выбираем месяц. Кликаем

    click("//div[@id='container2']")
    monthsList = ['Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня', 'Июля', 'Августа', 'Сентября', 'Октября',
                  'Ноября', 'Декабря']
    month = r.choice(monthsList)
    monthLi = driver.find_element_by_xpath("//ul[@id='list_options_container_2']/li[text() = '%s']" % month)
    monthLi.click()

    # находим и кликаем по полю "год", из выпадающего списка рандомно выбираем год от 1980 до 2001. Кликаем

    click("//div[@id='container3']")
    yearRandomCount = r.randint(1980, 2001)
    yearLi = driver.find_element_by_xpath("//ul[@id='list_options_container_3']/li[text() = '%s']" % yearRandomCount)
    yearLi.click()

    print('Заполнили поля имени, фамилии, дня, месяца, года')

    # клик на кнопку "зарегистрироваться"

    click("//button[@id='ij_submit']")
    time.sleep(1)
    print('Нажали "зарегистрироваться"')

    # проверка, открылась ли следующая страница

    regUrl = driver.current_url
    if regUrl == "https://vk.com/":
        tabIndex = r.randint(-1, 0)
        sexDiv = driver.find_element_by_xpath("//div[@id='ij_sex_row']/div[@tabindex='%s']" % tabIndex)
        sexDiv.click()
        click("//button[@id='ij_submit']")

    # находим самый дешевый номер
    # отправляем запрос на получение инфы о номерах

    payload = {'api_key': f'{token}', 'action': 'getPrices', 'service': 'vk', 'operator': 'any'}
    g = requests.get('https://sms-activate.ru/stubs/handler_api.php', params=payload)
    responseDic = json.loads(g.text.replace("'", '"'))  # переводим в строку json, чтоб сделать словарем

    # создаем и заполняем словарик: {номер страны: цена телефона этой страны}

    numberCostDic = {}
    for elem in responseDic:
        if responseDic[elem] == {}: # проверка, не пустая ли эта часть словаря
            continue
        else:
            if responseDic[elem]['vk']['count'] < 10:  # проверка, есть ли инфа и 10 доступных номеров
                continue
            else:
                numberCostDic[elem] = responseDic[elem]['vk'][
                    'cost']  # добавляем в словарь значения

    # сортируем словарик по возрастанию цены стран

    orderedNumberCostDic = OrderedDict(
                sorted(numberCostDic.items(), key=lambda t: t[1]))

    # создаем список с номерами стран в порядке возрастания цены

    numbersOfCountriesList = []
    for numberOfCountry in orderedNumberCostDic:
        numbersOfCountriesList.append(numberOfCountry)

    print('создали список стран в порядке возрастания цены: ', numbersOfCountriesList)

    def countryGet():
        firstNumberOfCountriesList = numbersOfCountriesList[0]  # берем первую страну из словарика
        numbersOfCountriesList.remove(firstNumberOfCountriesList)  # удаляем первую страну из словарика

        # запрос в сервис для получения номера

        countryName = countriesCodesDic.get(firstNumberOfCountriesList)
        print('Берем страну:', countryName, ' с номером: ', firstNumberOfCountriesList)
        payload = {'api_key': f'{token}', 'action': 'getNumber', 'service': 'vk', 'operator': 'any',
                   'country': f'{firstNumberOfCountriesList}'}
        g = requests.get('https://sms-activate.ru/stubs/handler_api.php', params=payload)

        # проверка, точно ли есть номера

        checkNumbers(g)

        # проверка токена

        if g.text == "BAD_KEY":
            print('Токен из файла inf.txt не работает')
            exit(0)
        else:
            print('С токеном все окей')
        result = re.split(r':', g.text)


        # разбив полученной инфы на ID и номер

        ID = result[1]
        phoneNumbers = result[2]
        print('Получили номер: ', phoneNumbers, ' и ID операции: ', ID)

        # Находим и вводим страну

        clear('//input[@class="selector_input selected"]')
        sendKeys('//input[@class="selector_input selected"]', countryName)
        sendKeys('//td[@class="selector"]/input[@type="text"]', u'\ue007')

        # находим и вводим телефон в поле ввода, вырезаем и вставляем

        sendKeys('//div[@class="prefix_input_field"]/input[@id="join_phone"]', phoneNumbers)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('x').key_up(Keys.CONTROL).perform()
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

        # находим и кликаем по кнопке "Получить код"

        click('//button[@id="join_send_phone"]')

        # надо сделать проверку наличия окна "я не робот": //div[@class="popup_box_container"]

        # проверяем наличия div "Номер заблокирован"

        try:
            driver.find_element_by_xpath("//div[@class='msg_text']")
            print('Вк заблокировал номер')
            click('//a[@id="join_other_phone"]')
            countryGet()  # функция, которая другую страну берет
        except NoSuchElementException:
            print('Вк не заблокировал номер')
            pass

        # проверяем наличия div "Неверный номер телефона. Введите в международном формате"

        try:
            driver.find_element_by_xpath("//div[@class='msg error']")
            print('Неверный номер телефона. Введите в международном формате')
            click('//a[@id="join_other_phone"]')
            countryGet()  # функция, которая другую страну берет
        except NoSuchElementException:
            print('Международный формат - ок')
            pass

        # проверка готовности кнопки "Отправить код с помощью смс"

        print('Ожидаю появления кнопки для отправки кода с помощью смс')
        WebDriverWait(driver, 140).until(EC.presence_of_element_located((By.XPATH, "//a[@id='join_resend_lnk']")))

        # клик по "Отправить код с помощью смс"

        click('//a[@id="join_resend_lnk"]')
        print('нажал "отправить код с помощью смс"')

        # отправляем запрос: номер готов к получению смс

        payloadNumberReadyRequest = {'api_key': f'{token}', 'action': 'setStatus', 'status': '1', 'id': f'{ID}'}
        numberIsReadyRequest = requests.post('https://sms-activate.ru/stubs/handler_api.php',
                                            params=payloadNumberReadyRequest)
        print('отправили запрос на изменения статуса: ', numberIsReadyRequest.text)

    # вызываем функцию, которая определяет страну

    countryGet()

    # ждем, пока не придет код

    try:
        WebDriverWait(driver, 300, 30).until(getStatus, "смска пришла???")

        if getStatus() == False:
            click('//a[@id="join_other_phone"]')
            print('Беру другую страну')
            countryGet()

        print('смска пришла: ', codeList[1])
    except TimeoutException:
        click('//a[@id="join_other_phone"]')
        print('Беру другую страну')
        countryGet()


    # вводим код в input "Введите код"

    sendKeys('//input[@id="join_code"]', codeList[1])

    # клик по кнопке "Отправить код"

    click('//button[@id="join_send_code"]')

    # time.sleep(3)

    # вводим пароль
    WebDriverWait(driver, 5, 0.5).until()

    sendKeys("//input[@id='join_pass']", r.getrandbits(50))
    sendKeys(u'\ue007')
    # click("//button[@id='join_send_pass']'")


reg()
