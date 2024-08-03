import bs4
import requests

from bs4 import BeautifulSoup
from collections import defaultdict

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import streamlit as st

@st.cache_resource
def get_driver():
    return webdriver.Chrome(
        service=Service(
            ChromeDriverManager(driver_version="127.0.6533.88").install()
        ),
        options=options,
    )

options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--headless")

# chromedriver_autoinstaller.install()
def times_scrape(symbol):
    # symbol = symbol.replace('.NS','')
    # options = webdriver.ChromeOptions()
    # options.add_argument('--ignore-certificate-errors')
    # options.add_argument("--headless")
    # options.add_experimental_option('detach', True)
    # options.add_argument("--log-level=1")
    # options.add_argument('--incognito')
    # service = Service(executable_path=r"C:\Users\HP\OneDrive\Desktop\fin_dash\chromedriver-win64\chromedriver.exe")

    driver = get_driver()
    driver.get('https://economictimes.indiatimes.com')
    WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'inputBox'))
        )
    search_box = driver.find_element(By.CLASS_NAME, 'inputBox')
    search_box.send_keys('NMDC')
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)
    # news_class = driver.find_element(By.CLASS_NAME,'news_sec')
    page_source = driver.page_source
    soup = BeautifulSoup(page_source,'lxml')
    # WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.CLASS_NAME, 'news_sec'))
    #     )

    news_class = soup.find_all('div',class_ = 'news_sec')
    print(news_class)
    driver.get(news_class[0].find('div',class_ = 'more_section').find('a',class_ = 'full_btn').get('href'))
    news_stock = defaultdict(list)
    time.sleep(10)
    page_source2 = driver.page_source
    soup = BeautifulSoup(page_source2,'lxml')
    eachStory = soup.find_all('div',class_ = 'eachStory')
    news_n = []
    n_article = min(5,len(eachStory))
    for i in range(n_article):
        news_link = eachStory[i].find('a').get('href')
        news_n.append('https://economictimes.indiatimes.com'+news_link)
    print(news_n)
    return news_n
# sign_in = driver.find_element(By.CLASS_NAME,'signInLink')
# sign_in.click()
# time.sleep(4)
# sign_in_with_google = driver.find_element(By.ID,'emailAndMobile')
# sign_in_with_google.send_keys('sahil.chhabra.met21@itbhu.ac.in')
# button = driver.find_element(By.ID,'signInButton')
# button.click()
# time.sleep(4)
# password = driver.find_element(By.ID,'current-password')
# password.send_keys('Sahil@8733')
# pswd_button = driver.find_element(By.ID,'otpPwdSignInBtn')
# pswd_button.click()

def google_scrape(symbol):
    symbol = symbol.replace('.NS','')
    # options = webdriver.ChromeOptions
    # options = webdriver.ChromeOptions()
    # options.add_argument('--ignore-certificate-errors')
    # options.add_argument("--headless")
    # options.add_experimental_option('detach', True)
    # options.add_argument("--log-level=1")
    # options.add_argument('--incognito')
    # service = Service(executable_path=r"C:\Users\HP\OneDrive\Desktop\fin_dash\chromedriver-win64\chromedriver.exe")

    driver = get_driver()
    driver.get('https://www.google.com/')
    # searchBox = driver.find_element(By.CLASS_NAME,'gLFyf')
    # searchBox.send_keys(f'{symbol} latest news')
    # searchBox.send_keys(Keys.RETURN)
    # time.sleep(3)
    searchBox = driver.find_element(By.CLASS_NAME,'gLFyf')
    searchBox.send_keys('Power grid latest news')
    searchBox.send_keys(Keys.RETURN)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source,'lxml')
    top_stories = soup.find_all('a',class_ = 'WlydOe')
    print(top_stories)
    news_articles = defaultdict(list)
    for i in range(len(top_stories)):
        news = top_stories[i].text
        link = top_stories[i].get('href')
        news_articles[i].append(news)
        news_articles[i].append(link)
    return news_articles