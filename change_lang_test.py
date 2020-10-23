import time
from webbrowser import Chrome

import pytest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

# XPATHS
change_lang_xpath = "//*[@id='__next']//div[@class='xwtbyq-0 iGclcX cmc-header-desktop']/div[1]//button/span[2]"
a_lang_xpath = "//p[contains(text(),'All languages')]/../div/a"




def test_languages():
    # driver init
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    driver = webdriver.Chrome(chrome_options=options)

    print("Current session is {}".format(driver.session_id))
    driver.set_window_size(width=1920, height=1080)
    wait = WebDriverWait(driver, 30)
    driver.get("https://coinmarketcap.com/")

    lang_menu = wait.until(ec.visibility_of_element_located((By.XPATH, change_lang_xpath)))
    lang_menu.click()
    wait.until(ec.visibility_of_element_located((By.XPATH, a_lang_xpath)))
    langs_elements = driver.find_elements_by_xpath(a_lang_xpath)
    langs_arr = []
    for lang in langs_elements:
        langs_arr.append(lang.text.split(" ")[0]) # get all languages
    lang_menu.click() #close popup
    for lang in langs_arr:
        lang_menu = wait.until(ec.visibility_of_element_located((By.XPATH, change_lang_xpath)))
        lang_menu.click() # open lang menu
        lang_element = wait.until(ec.visibility_of_element_located((By.XPATH, a_lang_xpath+"[contains(text(),'"+lang+"')]")))
        lang_element.click() # choose languages
        current_lang = wait.until(ec.visibility_of_element_located((By.XPATH, change_lang_xpath)))
        current_lang_name = current_lang.text
        assert lang in current_lang_name
    driver.close()
