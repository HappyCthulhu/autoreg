from selenium import webdriver
from selenium.webdriver.common import keys
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.wait import WebDriverWait
import random as r
from selenium.common.exceptions import TimeoutException
import time
import requests
import re
import json

dict = {}
with open('C:\Python\Selenium\\autoreg\\inf.txt', 'r') as UrInf:
    for line in UrInf:
        listInf = line.strip().split(':')
        dict[listInf[0]] = listInf[1]
token = dict.get('token')

payload = {'api_key': f'{token}', 'action': 'getPrices', 'service': 'vk', 'operator': 'any'}
g = requests.get('https://sms-activate.ru/stubs/handler_api.php', params=payload)
responseDic = json.loads(g.text.replace("'", '"'))  # переводим в строку json, чтоб сделать словарем
print(responseDic)
keys = list(responseDic.keys())  # получаем список с номерами стран
lowestPriceList = [keys[0], responseDic[keys[0]]['vk']['cost']]  # создаем список, в котором будет номер страны с самой дешевой ценой аренды и добавляем первую страну

for elem in responseDic:
    if responseDic[elem] == {} or responseDic[elem]['vk']['count'] < 10:  # проверка, есть ли инфа и 10 доступных номеров
        continue
    else:
        if responseDic[elem]['vk']['cost'] >= lowestPriceList[1]: # если полученная цена больше цены из списка, берем другой номер
            continue
        else:  # если цена меньше
            lowestPriceList.clear() # очищаем список
            lowestPriceList += [elem, responseDic[elem]['vk']['cost'], responseDic[elem]['vk']['count']] # добавляем номер страны, цену и кол-во номеров
print('самая меньшая цена:', lowestPriceList)


countryName = dict.get(lowestPriceList[0])
countryNumber = dict.get(lowestPriceList[1])
lowestPriceList(countryName, countryName)
