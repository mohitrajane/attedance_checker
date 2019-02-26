#!/usr/bin/env python3
import time
import json
import os
import lxml
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
     for i in attendance_dict:
        if i.startswith('Sub_'):
            if(attendance_dict[i][3] < 75.00) and attendance_dict[i][2] != 0:
                no_of_hour_left = hours_needed(attendance_dict[i],0)
                print('Attendance shortage:{}\nClass required(to reach 75%):{}'.format(attendance_dict[i][0],no_of_hour_left))

def trim_attendance(attendance_dict):
    for i in attendance_dict:
        if i.startswith('Sub_'):
            if(attendance_dict[i][3] >75.00):
                trim_to_75 = hours_needed(attendance_dict[i],1)
                print('Subject:{} you can cut:{}'.format(attendance_dict[i][0],trim_to_75))



def main():
    login_url = 'http://202.88.252.52/fisat/'
    admission_no = input('Enter admission no:')
    password = input('Enter password(DOB in format yyyymmdd):')
    login_details = {
        'userid' : admission_no,
        'password' : password
    }
   
    #To check if user data exit 
    if(os.path.isfile(admission_no+".json")):
        if_update=input("\nUpdate data(Y/N):")
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
    trim_attendance(attendance_dict)
    
    with open(admission_no+'.json','w') as output:
        json.dump(attendance_dict,output)
    browser.quit()

if __name__ == '__main__':
    
    main()
    
