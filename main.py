#!/usr/bin/env python3

#In-build modules
import time
import json
import os
import argparse

#3rd party modules
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

def check_arg(args=None):
    parser = argparse.ArgumentParser(description='Know your attendance details ')
    parser.add_argument('-U','--update',help='Update attendance details',default='Y')
    parser.add_argument('-u','--user',type=int,help='username for web portal',default=-1)
    parser.add_argument('-p','--password',type=int,help='password for web portal',default=-1)
    parser.add_argument('-c','--cli',help='For all the CLI people out there :)' ,default='N')
    results = parser.parse_args(args)
    return (results.update,results.user,results.password,results.cli)

def login(login_url,login_details):
    browser.get(login_url)
    username = browser.find_element_by_name('userid')
    password = browser.find_element_by_name('password')
    username.send_keys(login_details['userid'])
    password.send_keys(login_details['password'])
    login_attempt = browser.find_element_by_xpath('/html/body/div[2]/div/div[3]/div[2]/form/div/div/input')
    login_attempt.click()

#get attendance data from the web page
def extract_data(table_raw,attendance_dict):
    attendance = list()
    attendance_raw = table_raw.find_all('tbody')
    for tr in attendance_raw:
        rows = tr.find_all('tr')
        for row in rows:
            cols=row.find_all('td')
            attendance.append([x.text.strip() for x in cols])

    for i in range(1,len(attendance)):
        subject_name = attendance[i][0].split(' ',1)[1]
        total_period = int(attendance[i][1])
        period_attendented = int(attendance[i][2])
        percentage = float(attendance[i][3].split('%')[0])
        subject = [subject_name,period_attendented,total_period,percentage]
        attendance_dict['Sub_{}'.format(i)] = subject
    last_update = attendance[0][1]
    attendance_dict['last_update'] = last_update

#to find number of hours required to get 75% atendance
def hours_needed(sub,mode):
    current_hour = sub[1]
    total_hour = sub[2]
    percentage = sub[3]
    if mode == 0:
        no_of_hour_left = 0
        while percentage < 75.00:
            current_hour += 1
            total_hour +=1
            percentage = (current_hour/total_hour) *100
            no_of_hour_left += 1
        return no_of_hour_left
    if mode == 1:
        trim_to_75 = 0
        while percentage > 75.00:
            total_hour += 1
            percentage = (current_hour/total_hour) * 100
            trim_to_75 += 1
        return trim_to_75


def read_json():
    with open(admission_no+'.json','r') as admission_json:
        attendance_dict = json.load(admission_json)
    find_shortage(attendance_dict)
    trim_attendance(attendance_dict)

def find_shortage(attendance_dict):
    print('\n-------------\nShortage For\n-------------')
    for i in attendance_dict:
        if i.startswith('Sub_'):
            if(attendance_dict[i][3] < 75.00) and attendance_dict[i][2] != 0:
                no_of_hour_left = hours_needed(attendance_dict[i],0)
                print('{} : {}(Class required)'.format(attendance_dict[i][0],no_of_hour_left))

def trim_attendance(attendance_dict):
    print('\n-------\nCan Cut\n-------')
    for i in attendance_dict:
        if i.startswith('Sub_'):
            if(attendance_dict[i][3] >75.00):
                trim_to_75 = hours_needed(attendance_dict[i],1)
                print('{} : {}'.format(attendance_dict[i][0],trim_to_75))





if __name__ == '__main__':

    if_update,admission_no,password,cli=check_arg()
    #print("Update:{}[{}],User name: {}[{}], password: {}[{}], CLI:{}[{}]".format(if_update,type(if_update),admission_no,type(admission_no),password,type(password),cli,type(cli)))

    if cli == 'N':
        try:
            from PyQt5.QtWidgets import QApplication,QLabel
        except ImportError:
            print("cant import PyQt5, install pyqt5 or use cli:).\nQuitting....") 
            exit(0)
        app = QApplication([])
        label = QLabel('Attendacne checker')
        label.show()
        app.exec_()

    login_url = 'http://202.88.252.52/fisat/'
    if admission_no == -1 or password == -1:
        admission_no = input('Enter admission no:')
        password = input('Enter password(DOB in format yyyymmdd):')

    admission_no = str(admission_no)
    password = str(password)
    login_details = {
        'userid' : admission_no,
        'password' : password
    }

    #To check if user data exit
    if(os.path.isfile(admission_no+".json")):
        if if_update == 'N' or if_update == 'n':
            read_json()
            exit()

    #selinium initilizing options
    options = Options()
    options.headless = True
    browser = webdriver.Firefox(options=options, executable_path='geckodriver')
    attendance_dict = {}
    login(login_url,login_details)

    name = browser.find_element_by_class_name('log_data').text.strip()
    name = name.split(',')
    attendance_dict['name'] = name[0]
    attendance_dict['admission_no'] = name[1].split('\n')[0]
    browser.find_element_by_xpath('/html/body/div[3]/div/div[1]/div/div/ul/li[3]').click()
    time.sleep(3)
    browser.find_element_by_xpath('/html/body/div[3]/div/div[2]/div/div/div[2]/div[1]').click()
    time.sleep(10)

    data = browser.page_source
    soup = BeautifulSoup(data,'lxml')
    table_raw = soup.find(class_='atnd_info_box')
    time.sleep(1)

    extract_data(table_raw,attendance_dict)
    find_shortage(attendance_dict)
    trim_attendance(attendance_dict) #to find how many hours can be cut

    with open(admission_no+'.json','w') as output:
        json.dump(attendance_dict,output)
    browser.quit()