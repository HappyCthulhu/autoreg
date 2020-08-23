from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import random as r
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
import time, requests, re, os, json, random
from random import seed
from selenium.webdriver.common.action_chains import ActionChains
from collections import OrderedDict
import sys
name = 'Валерий'
surname = 'Валерий'
phoneNumbers = 79992069657
password = ''.join(
    [r.choice(list('123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM')) for x in range(12)])

phoneNumbersStr = str(phoneNumbers)

# записываем в файлик логин и пароль
loginPass = name + '&' + surname + '#' + phoneNumbersStr + ':' + password
print(loginPass)

name = ['Валерий']
print(type(name))
name = name[0]
print(type(name))
