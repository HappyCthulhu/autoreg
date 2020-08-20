from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.wait import WebDriverWait
import random as r
from selenium.common.exceptions import TimeoutException
import time
import requests
import re
import os
from selenium.common.exceptions import NoSuchElementException
import json
from selenium.webdriver.common.action_chains import ActionChains
from collections import OrderedDict

# d = {'name': {'7': '4'}, 'age': {'8': '3'}, 'address': {'9': '2'}}
# new_d = OrderedDict(sorted(d.items(), key=lambda t: t[1]))
# print(new_d)

dict = {}
with open('.' + os.path.join(os.sep, 'names', 'inf.txt'), 'r') as UrInf:
    for line in UrInf:
        listInf = line.strip().split(':')
        dict[listInf[0]] = listInf[1]

token = dict.get('token')


def checkNumbers(request):
    if request.text == 'NO_NUMBERS':
        print('нет номеров')
    else:
        return True


# назначаем переменную для вебдрайвера
driver = webdriver.Chrome('.' + os.path.join(os.sep, 'chromedriver'))
driver.delete_all_cookies()
driver.get('https://vk.com/')

codeList = []

payload = {'api_key': f'{token}', 'action': 'getPrices', 'service': 'vk', 'operator': 'any'}
g = requests.get('https://sms-activate.ru/stubs/handler_api.php', params=payload)
responseDic = json.loads(g.text.replace("'", '"'))  # переводим в строку json, чтоб сделать словарем
keys = list(responseDic.keys())  # получаем список с номерами стран
lowestPriceList = [keys[0], responseDic[keys[0]]['vk'][
    'cost']]  # создаем список, в котором будет номер страны с самой дешевой ценой аренды и добавляем первую страну
numberCostDic = {}
for elem in responseDic:
    if responseDic[elem] == {} or responseDic[elem]['vk'][
        'count'] < 10:  # проверка, есть ли инфа и 10 доступных номеров
        continue
    else:
        # print(g.text)
        # print(elem)
        # print(responseDic[elem])
        # print(responseDic[elem]['vk']['cost'])
        numberCostDic[elem] = responseDic[elem]['vk']['cost']
        # print(numberCostDic)
        if responseDic[elem]['vk']['cost'] >= lowestPriceList[
            1]:  # если полученная цена больше цены из списка, берем другой номер
            continue
        else:  # если цена меньше
            lowestPriceList.clear()  # очищаем список
            lowestPriceList += [elem, responseDic[elem]['vk']['cost'],
                                responseDic[elem]['vk']['count']]  # добавляем номер страны, цену и кол-во номеров
        new_d = OrderedDict(sorted(numberCostDic.items(), key=lambda t: t[1]))

print('самая меньшая цена:', lowestPriceList, 'а вот словарик: ', numberCostDic, 'сортированный словарик: ', new_d)
    for key in new_d:
    print('key: ', key)
    print('new_d[key]', new_d[key])

numbersOfCountriesList = []
for key in new_d:
    numbersOfCountriesList.append(key)
print(numbersOfCountriesList)
print(numbersOfCountriesList[0])
numberOfCountry = numbersOfCountriesList[0]
numbersOfCountriesList.remove(numberOfCountry)

# print(numbersOfCountriesList[0])
#
# print('словарь до метода pop: ', new_d)
# x = 0
# numberOfCountry = list(new_d.keys())[list(new_d.values()).index(numbersOfCountriesList[0])]
# # numberOfCountry = new_d.pop(numbersOfCountriesList[0])
# print('словарь после метода pop: ', new_d)
# print('Номер страны с самым дешевым телефоном: ', numberOfCountry)

# прошлый вариант:
payload = {'api_key': f'{token}', 'action': 'getPrices', 'service': 'vk', 'operator': 'any'}
g = requests.get('https://sms-activate.ru/stubs/handler_api.php', params=payload)
responseDic = json.loads(g.text.replace("'", '"'))  # переводим в строку json, чтоб сделать словарем
keys = list(responseDic.keys())  # получаем список с номерами стран
lowestPriceList = [keys[0], responseDic[keys[0]]['vk'][
    'cost']]  # создаем список, в котором будет номер страны с самой дешевой ценой аренды и добавляем первую страну

for elem in responseDic:
    if responseDic[elem] == {} or responseDic[elem]['vk'][
        'count'] < 10:  # проверка, есть ли инфа и 10 доступных номеров
        continue
    else:
        if responseDic[elem]['vk']['cost'] >= lowestPriceList[
            1]:  # если полученная цена больше цены из списка, берем другой номер
            continue
        else:  # если цена меньше
            lowestPriceList.clear()  # очищаем список
            lowestPriceList += [elem, responseDic[elem]['vk']['cost'],
                                responseDic[elem]['vk']['count']]  # добавляем номер страны, цену и кол-во номеров
print('самая меньшая цена:', lowestPriceList)
