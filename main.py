import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

def login(login_url,login_details):
    browser.get(login_url)
    username = browser.find_element_by_name('userid')
    password = browser.find_element_by_name('password')
    username.send_keys(login_details['userid'])
    password.send_keys(login_details['password'])
    login_attempt = browser.find_element_by_xpath('/html/body/div[2]/div/div[3]/div[2]/form/div/div/input')
    login_attempt.click()
    

if __name__ == '__main__':
    login_url = 'http://202.88.252.52/fisat/'
    #admission_no = input('Enter admission no:')
    #password = input('Enter password(DOB in format yyyymmdd):')
    login_details = {
        'userid' : '49616',
        'password' : '19980830'
    }
    options = Options()
    options.headless = True
    browser = webdriver.Firefox(options=options, executable_path='geckodriver')
    login(login_url,login_details)
    browser.find_element_by_xpath('/html/body/div[3]/div/div[1]/div/div/ul/li[3]').click()
    time.sleep(3)
    browser.find_element_by_xpath('/html/body/div[3]/div/div[2]/div/div/div[2]/div[1]').click()
    time.sleep(10)
    data = browser.page_source
    soup = BeautifulSoup(data,'lxml')
    table_list = soup.find(class_='atnd_info_box')
    #print(table_list)
    time.sleep(1)
    subject_list = table_list.find_all('tbody')
    #print(subject_list)
    for tr in subject_list:
        rows = tr.find_all('tr')
        for row in rows:
            cols=row.find_all('td')
            cols=[x.text.strip() for x in cols]
            print(cols)

    print("HERE\n")
    #print(subject_list)
    browser.quit()
    
