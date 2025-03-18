'''
Author: Amit Chakraborty
Project: Alphapointe Job Scraper
Profile URL: https://github.com/amitchakraborty123
E-mail: mr.amitc55@gmail.com
'''

import time
import datetime
import pandas as pd
from bs4 import BeautifulSoup
import warnings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os

warnings.filterwarnings("ignore")

x = datetime.datetime.now()
n = x.strftime("__%b_%d_%Y")


def driver_conn():
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")      # Make the browser Headless. if you don't want to see the display on chrome just uncomment this
    chrome_options.add_argument("--log-level=3")    # Removes error/warning/info messages displayed on the console
    chrome_options.add_argument("--disable-infobars")  # Disable infobars ""Chrome is being controlled by automated test software"  Although is isn't supported by Chrome anymore
    chrome_options.add_argument("start-maximized")     # Make chrome window full screen
    chrome_options.add_argument('--disable-gpu')       # Disable gmaximizepu (not load pictures fully)
    # chrome_options.add_argument("--incognito")       # If you want to run browser as incognito mode then uncomment it
    chrome_options.add_argument("--disable-notifications")  # Disable notifications
    chrome_options.add_argument("--disable-extensions")     # Will disable developer mode extensions
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")    # retrieve_block
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])    # retrieve_block
    chrome_options.add_experimental_option('useAutomationExtension', False)    # retrieve_block
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36')    # retrieve_block
    chrome_options.add_argument('--accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9')    # retrieve_block
    chrome_options.add_argument('--accept-encoding=gzip, deflate, br')    # retrieve_block
    chrome_options.add_argument('--accept-language=en-US,en;q=0.9')    # retrieve_block

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)  # you don't have to download chromedriver it will be downloaded by itself and will be saved in cache
    return driver


def get_data():
    print('========================= Data Scraping =========================')
    all_links = []
    driver = driver_conn()
    driver.get('http://alphapointe.hrmdirect.com/employment/job-openings.php?search=true&')
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    soup = BeautifulSoup(driver.page_source, 'lxml')
    tds = soup.find('table', {'class': 'reqResultTable'}).find_all('tr', {'class': 'ReqRowClick'})
    for td in tds:
        a = 'http://alphapointe.hrmdirect.com/employment/' + td.find('a')['href']
        # print(a)
        all_links.append(a)
    # print(len(all_links))
    pp = 0
    for link in all_links:
        pp += 1
        print('Link: ' + str(pp) + ' Out of ' + str(len(all_links)))
        driver.get(link)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        title = ''
        department = ''
        location = ''
        job_desc = ''
        job_responsibilities = ''
        min_req = ''
        Work_hours = ''

        try:
            title = soup.find('div', {'class': 'reqResult'}).find('h2').text
        except:
            pass
        try:
            temps = soup.find('div', {'class': 'reqResult'}).find('table', {'class': 'viewFields'}).find_all('tr')
            for temp in temps:
                if 'Department:' in temp.text:
                    department = temp.text.replace('Department:', '').replace('\n', '')
                if 'Location:' in temp.text:
                    location = temp.text.replace('Location:', '').replace('\n', '').split(',', 1)
        except:
            pass
        try:
            temp = soup.find('div', {'class': 'reqResult'}).find('div', {'class': 'jobDesc'}).text
            try:
                job_desc = 'Job Summary: ' + temp.split('Job Summary:', 1)[1].split('Essential Functions:', 1)[0]
            except:
                pass
            try:
                job_responsibilities = 'Essential Functions: ' + temp.split('Essential Functions:', 1)[1].split('Knowledge and Skills Requirements:', 1)[0]
            except:
                try:
                    job_responsibilities = 'Essential Functions: ' + temp.split('Essential Functions:', 1)[1]
                except:
                    pass
            try:
                min_req = 'Knowledge and Skill Requirements:' + temp.split('Knowledge and Skill Requirements:', 1)[1].split('Working Conditions:', 1)[0]
            except:
                try:
                    min_req = 'Knowledge and Skill Requirements:' + temp.split('Knowledge and Skill Requirements:', 1)[1]
                except:
                    pass
            try:
                Work_hours = temp.split('Working Conditions:', 1)[1].replace('\n', ' ').replace('Â ', '').strip()
            except:
                pass
        except:
            pass
        data = {
            'Link': link,
            'Title': title,
            'Department': department,
            'location_City': location[0],
            'location_state': location[1],
            'Country': 'US',
            'job_desc': job_desc,
            'job_responsibilities': job_responsibilities,
            'min_req': min_req,
            'Work_hours': Work_hours
        }
        # print(data)
        df = pd.DataFrame([data])
        df.to_csv('alphapointe' + n + '.csv', mode='a', header=not os.path.exists('alphapointe' + n + '.csv'), encoding='utf-8-sig', index=False)
    print('============== Final Data Saved ==================')


if __name__ == '__main__':
    get_data()
