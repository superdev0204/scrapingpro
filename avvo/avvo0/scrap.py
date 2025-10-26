import requests
from bs4 import BeautifulSoup
import json
import csv
import time
from datetime import datetime
import random
import re
import os

SCRAPER_API_KEY = 'ea43d088ba0105b57a49658716beeca1'

def write_json_file(data,filename):
    while 1:
        try:
            with open(filename, 'w',encoding='utf-8') as outfile:
                json.dump(data, outfile,indent=4)
            break
        except Exception as error:
            print("Error in writing Json file: ",error)
            time.sleep(1)

def read_json_file(filename):
    data = {}
    with open(filename,encoding='utf-8') as json_data:
        data = json.load(json_data)
    return data

def is_file_exist(filename):
    if os.path.exists(filename):
        return True
    else:
        return False

def json_exist_data(fileName):
    json_data = []
    if is_file_exist(fileName):
        json_data = read_json_file(fileName)
    return json_data

def scrap_website(url):
    payload = {'api_key': SCRAPER_API_KEY, 'url': url}
    response=requests.get('https://api.scraperapi.com', params=payload)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Step 2: Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

def get_profile_info(soup):
    name = soup.find('h1', class_='profile-name').get_text()
    licenses = soup.find_all('div', class_='license')
    license_info = ""
    for license in licenses:
        license_info = license.find('h4', class_='license-title').get_text(separator=' ', strip=True) + "|"
        try:
            license_info = license_info + license.find('p', class_='license-state').find_all('span')[0].get_text(strip=True) + license.find('p', class_='license-state').find_all('span')[1].get_text(strip=True) + "|"
        except:
            license_info = license_info
        try:
            license_info = license_info + license.find('p', class_='license-acquired-date').find_all('span')[0].get_text(strip=True) + license.find('p', class_='license-acquired-date').find_all('span')[1].get_text(strip=True) + "|"
        except:
            license_info = license_info
        try:
            license_info = license_info + license.find('span', class_='status-pill').get_text(strip=True) + "|"
        except:
            license_info = license_info
        try:
            license_info = license_info + license.find('p', class_='license-status').get_text(strip=True)
        except:
            license_info = license_info
        license_info = license_info + "\n"
    license_info = license_info.strip()
    script_tag = soup.find_all('script', {'type': 'application/ld+json'})[0]
    script_content = script_tag.string
    data = json.loads(script_content)
    print(data['@id'])
    street = data['address']['streetAddress']
    city = data['address']['addressLocality']
    state = data['address']['addressRegion']
    zip = data['address']['postalCode']
    
    try:
        description = soup.find('div', id='bio-content').find('p').get_text()
    except:
        description = ""

    practice_areas_tags = soup.find_all('div', class_='practice-area-detail')
    practice_areas = ""
    for practice_area_tag in practice_areas_tags:
        practice_areas = practice_areas + practice_area_tag.find_all('strong')[0].get_text() + ": " + practice_area_tag.find_all('strong')[1].get_text() + "\n"
    practice_areas = practice_areas.strip()

    try:
        honors_tags = soup.find('section', class_='honors-container').find_all('div', class_='experience')
        honors = ""
        for honors_tag in honors_tags:
            honors = honors + honors_tag.get_text(separator='|', strip=True) + "\n"
        honors = honors.strip()
    except:
        honors = ""

    try:
        work_experience_tags = soup.find('section', class_='work-experience-container').find_all('div', class_='experience')
        work_experiences = ""
        for work_experience_tag in work_experience_tags:
            work_experiences = work_experiences + work_experience_tag.get_text(separator='|', strip=True) + "\n"
        work_experiences = work_experiences.strip()
    except:
        work_experiences = ""

    try:
        associations_tags = soup.find('section', class_='associations-container').find_all('div', class_='experience')
        associations = ""
        for associations_tag in associations_tags:
            associations = associations + associations_tag.get_text(separator='|', strip=True) + "\n"
        associations = associations.strip()
    except:
        associations = ""

    try:
        education_tags = soup.find('section', class_='education-container').find_all('div', class_='experience')
        educations = ""
        for education_tag in education_tags:
            educations = educations + education_tag.get_text(separator='|', strip=True) + "\n"
        educations = educations.strip()
    except:
        educations = ""

    try:
        speaking_engagements_tags = soup.find('section', class_='speaking-engagement-container').find_all('div', class_='experience')
        speaking_engagements = ""
        for speaking_engagements_tag in speaking_engagements_tags:
            speaking_engagements = speaking_engagements + speaking_engagements_tag.get_text(separator='|', strip=True) + "\n"
        speaking_engagements = speaking_engagements.strip()
    except:
        speaking_engagements = ""

    try:
        publications_tags = soup.find('section', class_='publications-container').find_all('div', class_='experience')
        publications = ""
        for publications_tag in publications_tags:
            publications = publications + publications_tag.get_text(separator='|', strip=True) + "\n"
        publications = publications.strip()
    except:
        publications = ""

    try:
        language = soup.find('div', class_='languages-list').get_text(separator='|', strip=True)
    except:
        language = ""

    rows = []
    rows.append([
        name,
        license_info,
        street,
        city,
        state,
        zip, 
        description, 
        practice_areas, 
        honors,
        work_experiences,
        associations,
        educations,
        speaking_engagements,
        publications,
        language,
    ])
    return rows


processed_json_file = f'processed.json'
processed_json_data = json_exist_data(processed_json_file)

def main():
    global processed_json_data, processed_json_file
    
    file_name = f'output_lawyers.csv'
    # Check if the file exists
    file_exists = os.path.exists(file_name)

    with open(file_name, 'a', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        if not file_exists:
            csv_writer.writerow(["Name", "License", "Street Address", "City", "State", "Zip", "Description", "Practice Areas", "Honors", "Work Experience", "Associations", "Education", "Speaking Engagements", "Publications", "Language"])
        url = "https://www.avvo.com/"
        soup = scrap_website(url)
        states = soup.find('div', class_='states').find_all('a')

        i=0
        for state in states:
            i=i+1
            if i!=5:
                continue
            print(f'State: {state.get_text()}')
            url = "https://www.avvo.com" + state['href']

            if url not in processed_json_data:                
                soup = scrap_website(url)
                cities = soup.find('div', class_='all-cities').find_all('a')

                for city in cities:
                    print(f'City: {city.get_text()}')
                    city_url = "https://www.avvo.com" + city['href']

                    if city_url not in processed_json_data:                        
                        soup = scrap_website(city_url)
                        lawyers = soup.find_all('h3', class_='profile-name')

                        for lawyer in lawyers:
                            profile_url = lawyer.find('a')['href']

                            if profile_url not in processed_json_data:
                                profile_soup = scrap_website(profile_url)
                                profile = get_profile_info(profile_soup)
                                csv_writer.writerows(profile)

                                processed_json_data.append(profile_url)
                                write_json_file(processed_json_data, processed_json_file)

                        processed_json_data.append(city_url)
                        write_json_file(processed_json_data, processed_json_file)

                        while 1:
                            try:
                                next_link = "https://www.avvo.com" + soup.find('nav', class_='pagination').find('a', rel='next')['href']
                                soup = scrap_website(next_link)

                                if next_link not in processed_json_data:                                    
                                    lawyers = soup.find_all('h3', class_='profile-name')

                                    for lawyer in lawyers:
                                        profile_url = lawyer.find('a')['href']

                                        if profile_url not in processed_json_data:
                                            profile_soup = scrap_website(profile_url)
                                            profile = get_profile_info(profile_soup)
                                            csv_writer.writerows(profile)
                                            
                                            processed_json_data.append(profile_url)
                                            write_json_file(processed_json_data, processed_json_file)

                                    processed_json_data.append(next_link)
                                    write_json_file(processed_json_data, processed_json_file)
                            except:
                                break                        

                processed_json_data.append(url)
                write_json_file(processed_json_data, processed_json_file)

main()