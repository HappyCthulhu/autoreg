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



def sendKeys(xPath, keys):
    driver.find_element_by_xpath(xPath).send_keys(keys)


driver = webdriver.Chrome('.' + os.path.join(os.sep, 'chromedriver'))
driver.delete_all_cookies()
driver.get('https://ya.ru/')
sendKeys("//input[@class='input__control input__input mini-suggest__input']", 'Слово для копирования')

element = driver.find_element_by_xpath("//input[@class='input__control input__input mini-suggest__input']")
ActionChains(driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
ActionChains(driver).key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
element.clear()
element.click()
ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()


sendKeys(u'\ue007')