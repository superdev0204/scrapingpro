from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import os
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import pandas as pd
import re
import csv
import json
import requests
from selenium.webdriver.support.ui import WebDriverWait
from urllib.parse import urljoin
from urllib.parse import urlparse
from datetime import datetime
import random
from seleniumwire import webdriver   # selenium-wire replaces selenium.webdriver for driver creation
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

SCRAPER_API_KEY = '1bb99fbfce94706f840c47c2b6a3cfa6'

options = webdriver.ChromeOptions()
print("Crawler Logs: Starting the crawler....")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("start-maximized")
options.add_argument("--disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument('--no-sandbox')
options.add_argument('--disable-application-cache')
options.add_argument('--disable-gpu')
options.add_argument("--disable-dev-shm-usage")
# Set a custom user-agent to mimic a normal browser
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

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

def scrap_website(url, premium=False, max_retries=10, backoff_factor=1.5, timeout=100):
    """
    Function to scrape a webpage using ScraperAPI with retry on failure.

    Args:
    - url (str): The URL of the webpage to scrape.
    - max_retries (int): Maximum number of retries if request fails.
    - backoff_factor (float): Backoff multiplier for each retry attempt.
    - timeout (int): Timeout for the request in seconds.

    Returns:
    - BeautifulSoup object if successful, or None if the request fails after retries.
    """
    attempt = 0

    while attempt < max_retries:
        attempt += 1
        print(f"Attempt {attempt}/{max_retries} to fetch: {url}")
        
        payload = {'api_key': SCRAPER_API_KEY, 'url': url}
        if premium:
            payload = {'api_key': SCRAPER_API_KEY, 'url': url, 'ultra_premium': 'true', 'max_cost': 30}
            
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            response = requests.get('https://api.scraperapi.com', params=payload, headers=headers, timeout=timeout)
            
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                print("Successfully retrieved the page!")
                # Parse the HTML content and return the BeautifulSoup object
                return BeautifulSoup(response.content, 'html.parser')
            elif response.status_code == 404:
                break
            else:
                print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

        except requests.exceptions.RequestException as e:
            # Handle request exceptions (e.g., timeout, connection error)
            print(f"Error occurred: {e}")
        
        # If the request fails, sleep for a backoff period before retrying
        backoff_time = backoff_factor ** attempt  # Exponential backoff
        print(f"Retrying in {round(backoff_time, 2)} seconds...")
        time.sleep(backoff_time)
    
    # If we exhaust the retries without success
    print("Failed to retrieve the page after multiple attempts.")
    return None

# def scrap_website(url):
#     payload = {'api_key': SCRAPER_API_KEY, 'url': url}
#     response=requests.get('https://api.scraperapi.com', params=payload)
    
#     # Check if the request was successful
#     if response.status_code == 200:
#         # Step 2: Parse the HTML content
#         soup = BeautifulSoup(response.content, 'html.parser')
#         return soup
#     else:
#         print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

def create_driver_with_auth(proxy_user, proxy_pass, proxy_host, proxy_port, headless=False):
    global options
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")

    # selenium-wire specific proxy config
    proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
    seleniumwire_options = {
        'proxy': {
            'http': proxy_url,
            'https': proxy_url,
            'no_proxy': 'localhost,127.0.0.1'  # optional
        }
    }

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options, seleniumwire_options=seleniumwire_options)
    # options.add_argument(f'--proxy-server=http://{proxy_host}:{proxy_port}')
    # driver = webdriver.Chrome(options=options)
    return driver


processed_json_file = f'processed.json'
processed_json_data = json_exist_data(processed_json_file)

def main():
    global processed_json_data, processed_json_file, driver

    # proxy_user = "VGE1CE"
    # proxy_pass = "NB8oF0"
    # proxy_host = "45.133.223.228"
    # proxy_port = "8000"
    
    proxy_user = "WherhlIK9Y"
    proxy_pass = "Yph5t8xhtn"
    proxy_host = "137.155.17.61"
    proxy_port = "9396"

    driver = create_driver_with_auth(proxy_user, proxy_pass, proxy_host, proxy_port)

    root_url = "https://www.zocdoc.com/specialty"
    driver.get(root_url)
    time.sleep(20)
    
    # root_soup = scrap_website(root_url)
    
    file_name = f'output_doctors.csv'
    # Check if the file exists
    file_exists = os.path.exists(file_name)

    with open(file_name, 'a', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)

        if not file_exists:
            csv_writer.writerow(["Provider Name", "Specialty", "Description", "Insurances", "Popular Visit Reasons", "Street", "City", "State", "Zip", "Practice Names", "Educations", "Languages", "Gender", "NPI Number"])
        
        specialties = driver.find_elements(By.XPATH, "//a[@data-test='specialty-link']")
        
        # specialties = root_soup.find_all('a', {'data-test': 'specialty-link'})
        
        i=0
        for specialty in specialties:
            i=i+1
            specialty_name = specialty.text.strip()
            print(f'Specialty: {specialty_name}')
            url = specialty.get_attribute('href')
            if "https://www.zocdoc.com" not in url:
                url = f"https://www.zocdoc.com{url}"

            if url not in processed_json_data:
                print(url)
                soup = scrap_website(url)
                cities = []
                for div in soup.find_all('div', {'data-test': 'expandable-list-section-list'}):
                    for a in div.find_all('a'):
                        cities.append({
                            'name': a.text.strip(),
                            'href': a['href']
                        })

                for city in cities:
                    print(f"City: {city['name']}")
                    for page in range(1, 7):
                        city_url = f"{city['href']}/{page}"
                        if "https://www.zocdoc.com" not in city_url:
                            city_url = f"https://www.zocdoc.com{city_url}"
                            
                        if city_url not in processed_json_data:
                            print(city_url)
                            profiles = []
                            try:
                                # if page == 1:
                                #     city_url = city['href']
                                # else:
                                #     city_url = f"{city['href']}/{page}"
                                
                                soup_city = scrap_website(city_url)
                                for card in soup_city.find_all('div', {'data-test': 'doctor-card'}):
                                    # Check if card has either 'doctor-card-photo-with-video' or 'doctor-card-photo'
                                    if card.find('div', {'data-test': 'doctor-card-photo-with-video'}) or card.find('div', {'data-test': 'doctor-card-photo'}):
                                        # Extract the <a> tag with doctor's name
                                        profile = card.find('a', {'data-test': 'doctor-card-info-name'})
                                        if profile:
                                            profiles.append(profile)
                            except Exception as e:
                                print(f"Error scraping city URL {city_url}: {e}")

                            # if len(profiles) < 1:
                            #     break

                            for profile in profiles:
                                print(f'profile: {profile.get_text()}')
                                profile_url = profile['href']
                                if "https://www.zocdoc.com" not in profile_url:
                                    profile_url = f"https://www.zocdoc.com{profile_url}"
                                    
                                if profile_url not in processed_json_data:
                                    print(profile_url)
                                    driver.get(profile_url)
                                    time.sleep(20)
                                    # soup_profile = scrap_website(profile_url, True)
                                    
                                    # if soup_profile == None:
                                    #     continue
                                    
                                    # # Extract provider name
                                    # try:
                                    #     provider_name = soup_profile.find('span', {'data-test': 'provider-name'}).text.strip()
                                    # except AttributeError:
                                    #     provider_name = ""
                                        
                                    # try:
                                    #     # Find spans with data-test="preview-span"
                                    #     preview_spans = soup_profile.find('section', {'data-test': 'AboutProfessional-section'}).find_all('span', {'data-test': 'preview-span'})
                                        
                                    #     # Find spans with class containing "sc-1opoey3-2"
                                    #     class_spans = soup_profile.find('section', {'data-test': 'AboutProfessional-section'}).find_all('span', class_='sc-1opoey3-2')

                                    #     # Merge all text
                                    #     all_spans = preview_spans + class_spans

                                    #     # Use get_attribute('textContent') in case .text misses dynamic content
                                    #     description = " ".join([span.get_text(strip=True) for span in all_spans if span.get_text(strip=True)])
                                    # except Exception as e:
                                    #     description = ""

                                    # # Extract insurances
                                    # try:
                                    #     insurances = soup_profile.find('div', {'data-test': 'in-network-insurances-text-content'}).text.strip()
                                    # except AttributeError:
                                    #     insurances = ""

                                    # # Extract visit reasons (titles from visit reason elements)
                                    # try:
                                    #     visit_reason_elements = soup_profile.find('div', {'data-test': 'visit-reasons-list'}).find('div', {'data-test': 'desktop-view'}).find_all('div', {'data-test': 'visit-reason'})
                                    #     titles = [el.get('title') for el in visit_reason_elements if el.get('title')]
                                    #     visit_reasons = ", ".join(titles)
                                    # except:
                                    #     visit_reasons = ""

                                    # # Extract address components
                                    # try:
                                    #     address = soup_profile.find('div', {'data-test': 'location-card-address-container'})
                                    #     street = address.find('span', {'itemprop': 'streetAddress'}).text.strip() if address else ""
                                    #     city_name = address.find('span', {'itemprop': 'addressLocality'}).get('content').strip() if address else ""
                                    #     state = address.find('span', {'itemprop': 'addressRegion'}).get('content').strip() if address else ""
                                    #     zip_code = address.find('span', {'itemprop': 'postalCode'}).text.strip() if address else ""
                                    # except:
                                    #     street = city_name = state = zip_code = ""
                                        
                                    # # Extract practice names (links in Practice-section)
                                    # try:
                                    #     practice_elements = soup_profile.find('section', {'data-test': 'Practice-section'}).find_all('a', {'data-test': 'profile-practice-link'})
                                    #     practice_names = [el.text.strip() for el in practice_elements if el.text.strip()]
                                    #     practice_string = ", ".join(practice_names)
                                    # except:
                                    #     practice_string = ""

                                    # try:
                                    #     education_elements = soup_profile.find('ul', {'data-test': 'education-list'}).find_all('span', {'data-test': 'education-item'})
                                    #     education_list = [el.text.strip() for el in education_elements if el.text.strip()]
                                    #     education_text = "\n".join(education_list)
                                    # except:
                                    #     education_text = ""

                                    # # Extract languages
                                    # try:
                                    #     language_elements = soup_profile.find('section', {'data-test': 'Languages-section'}).find('ul').find_all('li')
                                    #     languages = [el.text.strip() for el in language_elements if el.text.strip()]
                                    #     languages_text = ", ".join(languages)
                                    # except:
                                    #     try:
                                    #         languages_text = soup_profile.find('div', {'data-test': 'provider-languages'}).text.strip()
                                    #     except:
                                    #         languages_text = ""

                                    # # Extract gender
                                    # try:
                                    #     gender = soup_profile.find('p', {'data-test': 'provider-gender'}).text.strip()
                                    # except AttributeError:
                                    #     gender = ""

                                    # # Extract NPI number
                                    # try:
                                    #     npi_number = soup_profile.find('section', {'data-test': 'NPI-section'}).find('p').text.strip()
                                    # except AttributeError:
                                    #     npi_number = ""

                                    try:
                                        continue_button = WebDriverWait(driver, 5).until(
                                            EC.element_to_be_clickable((By.XPATH, '//button[@data-test="overlay-primary-button"]'))
                                        )
                                        continue_button.click()
                                        time.sleep(1)
                                        print("Clicked the 'Continue' button after waiting.")
                                    except:
                                        provider_name = ""

                                    try:
                                        provider_name = driver.find_element(By.XPATH, "//span[@data-test='provider-name']").text
                                    except:
                                        continue

                                    try:
                                        # Find spans with data-test="preview-span"
                                        preview_spans = driver.find_elements(
                                            By.XPATH,
                                            '//section[@data-test="AboutProfessional-section"]//span[@data-test="preview-span"]'
                                        )

                                        # Find spans with class containing "sc-1opoey3-2"
                                        class_spans = driver.find_elements(
                                            By.XPATH,
                                            '//section[@data-test="AboutProfessional-section"]//span[contains(@class, "sc-1opoey3-2")]'
                                        )

                                        # Merge all text
                                        all_spans = preview_spans + class_spans

                                        # Use get_attribute('textContent') in case .text misses dynamic content
                                        description = " ".join([
                                            el.get_attribute("textContent").strip()
                                            for el in all_spans
                                            if el.get_attribute("textContent").strip()
                                        ])
                                    except Exception as e:
                                        description = ""

                                    try:
                                        insurances = driver.find_element(By.XPATH, "//div[@data-test='in-network-insurances-text-content']").text
                                    except:
                                        insurances = ""

                                    try:
                                        visit_reason_elements = driver.find_elements(By.XPATH, "//div[@data-test='visit-reasons-list']/div[@data-test='desktop-view']/div[@data-test='visit-reason']")
                                        # Extract title attributes
                                        titles = [el.get_attribute("title") for el in visit_reason_elements if el.get_attribute("title")]
                                        # Join them into a single string
                                        visit_reasons = ", ".join(titles)
                                    except:
                                        visit_reasons = ""

                                    try:
                                        # Locate the address container
                                        address = driver.find_element(By.XPATH, '//div[@data-test="location-card-address-container"]')
                                    except:
                                        address = ""

                                    # Extract individual components
                                    try:
                                        street = address.find_element(By.XPATH, './/span[@itemprop="streetAddress"]').text.strip()
                                    except:
                                        street = ""
                                    try:
                                        city_name = address.find_element(By.XPATH, './/span[@itemprop="addressLocality"]').get_attribute("content").strip()
                                    except:
                                        city_name = ""
                                    try:
                                        state = address.find_element(By.XPATH, './/span[@itemprop="addressRegion"]').get_attribute("content").strip()
                                    except:
                                        state = ""
                                    try:
                                        zip_code = address.find_element(By.XPATH, './/span[@itemprop="postalCode"]').text.strip()
                                    except:
                                        zip_code = ""

                                    try:
                                        # Find all practice links inside the Practice-section
                                        practice_elements = driver.find_elements(
                                            By.XPATH,
                                            '//section[@data-test="Practice-section"]//a[@data-test="profile-practice-link"]'
                                        )

                                        # Extract their text content
                                        practice_names = [el.text.strip() for el in practice_elements if el.text.strip()]

                                        # Join them into a single string
                                        practice_string = ", ".join(practice_names)
                                    except:
                                        practice_string = ""

                                    try:
                                        # Find all education items
                                        education_elements = driver.find_elements(
                                            By.XPATH, '//ul[@data-test="education-list"]//span[@data-test="education-item"]'
                                        )

                                        # Extract and clean text
                                        education_list = [el.text.strip() for el in education_elements if el.text.strip()]

                                        # Join with line breaks
                                        education_text = "\n".join(education_list)
                                    except:
                                        education_text = ""

                                    try:
                                        # Find all languages in the Languages section
                                        language_elements = driver.find_elements(
                                            By.XPATH, '//section[@data-test="Languages-section"]//ul/li'
                                        )

                                        # Extract text
                                        languages = [el.text.strip() for el in language_elements if el.text.strip()]

                                        # Join into a single string like "a, b, c"
                                        languages_text = ", ".join(languages)
                                    except:
                                        try:
                                            languages_text = driver.find_element(By.XPATH, '//div[@data-test="provider-languages"]').text
                                        except:
                                            languages_text = ""

                                    try:
                                        gender = driver.find_element(By.XPATH, "//p[@data-test='provider-gender']").text
                                    except:
                                        gender = ""

                                    try:
                                        npi_number = driver.find_element(By.XPATH, "//section[@data-test='NPI-section']/p").text
                                    except:
                                        npi_number = ""

                                    rows = []
                                    rows.append([
                                        provider_name,
                                        specialty_name,
                                        description,
                                        insurances,
                                        visit_reasons,
                                        street,
                                        city_name, 
                                        state, 
                                        zip_code, 
                                        practice_string,
                                        education_text,
                                        languages_text,
                                        gender,
                                        npi_number,
                                    ])

                                    csv_writer.writerows(rows)

                                    print(f"Successfully {profile_url}")

                                    processed_json_data.append(profile_url)
                                    write_json_file(processed_json_data, processed_json_file)
                            
                            # city_url = f"{city['href']}/{page}"
                            # if "https://www.zocdoc.com" not in city_url:
                            #     city_url = f"https://www.zocdoc.com{city_url}"
                                
                            processed_json_data.append(city_url)
                            write_json_file(processed_json_data, processed_json_file)

                processed_json_data.append(url)
                write_json_file(processed_json_data, processed_json_file)

main()