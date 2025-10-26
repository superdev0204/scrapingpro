import requests
from bs4 import BeautifulSoup
import json
import csv
import time
from datetime import datetime
import random
import re

SCRAPER_API_KEY = 'fb5ba301bdc2ad880be6b081fe626753'

def replace_non_alphanumeric(filename):
    try:
        with open(filename, 'r') as file:
            clean_contents = []
            content = file.readlines()
            for line in content:
                clean_line = re.sub('[^A-Za-z0-9]+', '-', line.strip()).lower()
                clean_contents.append(clean_line)
            with open('list.txt', 'w') as clean_file:
                for line in clean_contents:
                    clean_file.write(line + '\n')
    except FileNotFoundError:
        return "File not found"
    except Exception as e:
        return str(e)

def get_link(position):
    print(f"Start Crawling Key word: {position}")
    h0_url = f"https://www.homes.com/{position}/"
    payload = {'api_key': SCRAPER_API_KEY, 'url': h0_url}
    xx=requests.get('https://api.scraperapi.com', params=payload)
    soup = BeautifulSoup(xx.content, 'html.parser')
    total_pages = soup.find('p', class_='search-results').text.strip()
    total_pages = int(total_pages.split(' of ')[1])
    
    try:
        script_tag = soup.find_all('script', {'type': 'application/ld+json'})[2]
    except:
        script_tag = soup.find_all('script', {'type': 'application/ld+json'})[1]
    script_content = script_tag.string
    json_data = json.loads(script_content)
    pridata= json_data["mainEntity"]["itemListElement"]
    
    return total_pages, pridata

def get_all_data(position):
    with open(f'output_{position}.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Address", "City", "State", "Zip", "Price", "Realtor Name", "Realtor Office", "Office Number", "Realtor License Number"])
        total_pages, pridata = get_link(position)
        if total_pages == 1:
            for data in pridata:
                url=data["url"]
                rows=run_url(url)
                while rows is None:
                    if rows is None:
                        # Optional: Sleep for a short duration to avoid overwhelming the server
                        time.sleep(1)
                    rows = run_url(url)   
                csv_writer.writerows(rows)
        else:
            for i in range(1, total_pages+1):
                h1_url = f"https://www.homes.com/{position}/p{i}"
                payload = {'api_key': SCRAPER_API_KEY, 'url': h1_url}
                h1=requests.get('https://api.scraperapi.com', params=payload)
                soup = BeautifulSoup(h1.content, 'html.parser')
                try:
                    script_tag = soup.find_all('script', {'type': 'application/ld+json'})[2]
                except:
                    script_tag = soup.find_all('script', {'type': 'application/ld+json'})[1]
                script_content = script_tag.string
                json_data = json.loads(script_content)
                datas  = json_data["mainEntity"]["itemListElement"]
                for data in datas:
                    url=data["url"]
                    rows=run_url(url)
                    while rows is None:
                        if rows is None:
                            # Optional: Sleep for a short duration to avoid overwhelming the server
                            time.sleep(1)
                        rows = run_url(url)                        
                    csv_writer.writerows(rows)
                    # time.sleep(random.randint(1,5))
     
def run_url(home_url):
    print(f"[INFO]: Fetching URL: {home_url}")
    try:
        payload = {'api_key': SCRAPER_API_KEY, 'url': home_url}
        response=requests.get('https://api.scraperapi.com', params=payload)
        if response.status_code != 200:
            print(f"Failed to fetch data from {home_url} with status code {response.status_code}")
            return None
        soup = BeautifulSoup(response.content, 'html.parser')
        script_tag = soup.find_all('script', {'type': 'application/ld+json'})[0]
        script_content = script_tag.string
        data = json.loads(script_content)
        try:
            realtor_name = soup.find('a', class_='agent-information agent-information-fullname standard-link text-only').text.strip()
        except:
            realtor_name = 'N/A'
        try:
            realtor_office = soup.find('span', class_='agent-information agent-information-agency-name').text.strip()
        except:
            realtor_office = 'N/A'
        try:
            realtor_office_number = soup.find('span', class_='agent-information agent-information-idx-contact').text.strip().split(': ')[1]
        except:
            realtor_office_number = 'N/A'
        try:
            realtor_office_license = soup.find('span', class_='agent-information agent-information-license-number').text.strip().replace("License ", "")
        except:
            realtor_office_license = 'N/A'
        rows = []
        rows.append([
            data["mainEntity"]["address"].get('streetAddress', 'N/A'),
            data["mainEntity"]["address"].get('addressLocality', 'N/A'),
            data["mainEntity"]["address"].get('addressRegion', 'N/A'),
            data["mainEntity"]["address"].get('postalCode', 'N/A'),
            data["offers"].get('price', 'N/A'),
            realtor_name, 
            realtor_office, 
            realtor_office_number, 
            realtor_office_license
        ])
        return rows
    except Exception as e:
        print(f"[ERR]: {str(e)}")        

def main():
    replace_non_alphanumeric('list.txt')
    try:
        with open('./list.txt', 'r') as file:
            key_words = file.read().splitlines()
        for key_word in key_words:
            get_all_data(key_word)
        print(f"[SUCCESSFULLY]: Data was saved in results file")
    except Exception as e:
        print(e)

main()