import requests
import sys
from bs4 import BeautifulSoup
import json
import threading
from requests.exceptions import ProxyError, SSLError, Timeout
import time
import re
import os
from sys import platform

with open("config.json", "r+", errors="ignore") as config_file:
    data = json.load(config_file)

ddddd = open(data["file"], "r", encoding="utf-8").read().splitlines()


def parse_blob(blob):
    regex = re.findall("(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})",blob)
    return regex


def parse_number(number):
    build_number = ""
    tmp = number.replace(')', '').replace('(','').replace('-','').replace(' ','')
    first3 = tmp[0:3]
    middle3 = tmp[3:6]
    last4 = tmp[6:10]
    build_number = f'{first3}-{middle3}-{last4}'
    return build_number
    


def send_request(blob):
    i = 0 
    done = open("done.txt", "a")
    try:
        phone_numbers = parse_blob(blob)
        if not phone_numbers:
            done.write(blob +"| NO NUMBERS\n")
            done.close()
            return
        for n in phone_numbers: 
            number = parse_number(n)
            url = f'https://www.yellowpages.ca/fs/1-{number}/'
            r = requests.get(url, timeout=5,verify=True, proxies={"http":data["proxies"],"https":data["proxies"]})
            if r.status_code == 404:
                return
            try:
                soup = BeautifulSoup(r.text, 'html.parser')
                carrier_html = soup.find(class_="phone__details")
                carrier_html_items = carrier_html.find('strong')
                phone_number = carrier_html_items.contents[0]
            except:
                phone_number = "UNKNOWN"

            print(f"{n} - {phone_number}")
            if i == 0:
                done.write(blob +"| "+ phone_number +" | ")
            elif i > 0:
                done.write(phone_number + " | ")
            i+=1
        done.write("\n")
        done.close()


    except SSLError: return send_request(blob)
    except ProxyError: return send_request(blob)
    except Exception as e:
        print("[ERROR] Timeout/Ratelimit, Retrying!")
        return send_request(blob)
        
if platform == "linux" or platform == "linux2":
    os.system("clear")
elif platform == "win32":
    os.system("cls")

print("\x1b[1;32m***************************")
print("\x1b[1;32m*        \x1b[1;31mstarting...     \x1b[1;32m *")
print("\x1b[1;32m***************************\x1b[00m")
 time.sleep(3)

for nummy in ddddd:
    while True:
        if threading.active_count() <= data["max_threads"]:
            threading.Thread(target=send_request, args=(nummy,)).start()
            break
        print("[THREAD] THREAD POOL FINISHED, RESTARTING!")
        time.sleep(0.3)



