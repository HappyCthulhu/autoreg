from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import random as r
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
import time, requests, re, os, json, random, sys
from random import seed
from selenium.webdriver.common.action_chains import ActionChains
from collections import OrderedDict
import os.path
from loguru import logger
import stun
from requests.auth import HTTPProxyAuth

with codecs.open('.' + os.path.join(os.sep, 'txtfiles', 'inf.txt'), 'w', encodi) as url_inf:
    logger.info('Под этой надписью введите токен вашего аккаунта на sms-activate')
    token = input()
    logger.info(
        'Под этой надписью введите название страны, номер телефона которой хотите арендовать. С большой буквы на русском языке:')
    country_name = input()
    url_inf.write(f'token:{token}\n'
                  f'country_name:{country_name}\n'
                  'Подсказка:если хотите пользоваться автоподбором страны с самой дешевой ценой номера, задайте country_name значение False')
    url_inf.close()

    with open('.' + os.path.join(os.sep, 'txtfiles', 'inf.txt'), 'r') as url_inf:
        for line in url_inf:
            list_inf = line.strip().split(':')
            dict[list_inf[0]] = list_inf[1]
