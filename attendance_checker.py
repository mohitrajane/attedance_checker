#!/usr/bin/env python3

# In-build modules
import time
import json
import os
import urllib.request

# 3rd party modules
try:
    import lxml
except ImportError:
    print("Couldn't find lxml.\nQuitting....")
    exit(0)
try:
    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.common.keys import Keys
except ImportError:
    print("Couldn't find Selenium.\nQuitting.....")
    exit(0)
try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Couldn't find bs4.\nQuitting....")
    exit(0)


def login(login_url, login_details):
    """Log into students portal """
    global browser
    browser.get(login_url)
    username = browser.find_element_by_name('userid')
    password = browser.find_element_by_name('password')
    username.send_keys(login_details['userid'])
    password.send_keys(login_details['password'])
    login_attempt = browser.find_element_by_xpath(
        '/html/body/div[2]/div/div[3]/div[2]/form/div/div/input'
    )
    login_attempt.click()


def extract_data(table_raw, attendance_dict):
    """get attendance data from raw HTML"""
    attendance = list()
    attendance_raw = table_raw.find_all('tbody')
    for tr in attendance_raw:
        rows = tr.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            attendance.append([x.text.strip() for x in cols])

    for i in range(1, len(attendance)):
        subject_name = attendance[i][0].split(' ', 1)[1]
        total_period = int(attendance[i][1])
        period_attendented = int(attendance[i][2])
        percentage = float(attendance[i][3].split('%')[0])
        subject = [subject_name, period_attendented, total_period, percentage]
        attendance_dict['Sub_{}'.format(i)] = subject
    try:
        last_update = attendance[0][1]
        attendance_dict['last_update'] = last_update
    except IndexError:
        # print("Couldn't fetch data")
        print("NoDataFound")
        return('NoDataFound')
        sys.exit(0)


def attendance_check(admission_no, password):
    """Takes admission no and password returns attendance details and image of student """

    login_url = 'http://202.88.252.52/fisat/'
    admission_no = str(admission_no)
    password = str(password)
    login_details = {
        'userid': admission_no,
        'password': password
    }

    # selinium initializing options
    options = Options()
    options.headless = True
    global browser
    browser = webdriver.Firefox(options=options, executable_path='geckodriver')
    attendance_dict = {}
    login(login_url, login_details)
    try:
        name = browser.find_element_by_class_name('log_data').text.strip()
    except:
        print('User name or password is wrong')
        # return('Login')
        exit(0)
    name = name.split(',')
    attendance_dict['name'] = name[0]
    attendance_dict['admission_no'] = name[1].split('\n')[0]
    browser.find_element_by_xpath(
        '/html/body/div[3]/div/div[1]/div/div/ul/li[3]'
    ).click()
    time.sleep(2)
    browser.find_element_by_xpath(
        '/html/body/div[3]/div/div[2]/div/div/div[2]/div[3]'
    ).click()
    # Bellow method is to get the latest sem
    # browser.find_element_by_xpath(
    #   '/html/body/div[3]/div/div[2]/div/div/div[2]/div[1]'
    # ).click()
    time.sleep(5)

    data = browser.page_source
    soup = BeautifulSoup(data, 'lxml')
    # table_raw = soup.find(class_='atnd_info_box')
    # bellow is only done for presentation purpose
    table_raw = soup.find(
        "div", attrs={"class": "atnd_info_box", "id": "sem2"}
    )
    time.sleep(1)

    extract_data(table_raw, attendance_dict)
    browser.find_element_by_xpath('/html/body/div[3]/div/div[1]/div/div/ul/li[2]').click()
    time.sleep(2)

    # get image
    img_data = browser.page_source
    soup = BeautifulSoup(img_data, 'lxml')
    img_div = soup.find("div", {"id": "profile_img"})
    # print(img_div)
    img_src = img_div.find('img')['src']
    with urllib.request.urlopen(img_src) as response:
        img = response.read()
    return(attendance_dict, img)

if __name__ == '__main__':
    attendance_check()
