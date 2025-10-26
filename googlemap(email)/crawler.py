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

import parsepy  # Import your parse.py module


class GoogleMaps:
    def __init__(self):
        options = webdriver.ChromeOptions()
        print("Crawler Logs: Starting the crawler....")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("start-maximized")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-application-cache')
        options.add_argument('--disable-gpu')
        options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=options)
        self.actionChains = ActionChains(self.driver)
        self.wait = WebDriverWait(self.driver, 20)
        self.driver.get("https://www.google.com/maps")
        language_code = "en-US"
        self.driver.execute_script(f"document.documentElement.lang = '{language_code}';")
        self.driver.refresh()
        
        # File paths
        self.cities_file = "cities.txt"
        self.output_file = "googlemap_results.csv"
        self.progress_file = "scraping_progress.csv"

        # Load progress
        self.start_keyword = ''
        self.start_city = ''
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as csvfile_progress:
                reader_progress = csv.reader(csvfile_progress)
                for row_progress in reader_progress:
                    try:
                        self.start_keyword = str(row_progress[0])
                    except IndexError:
                        self.start_keyword = ''
                    try:
                        self.start_city = str(row_progress[1])
                    except IndexError:
                        self.start_city = ''

        # Load city list
        if os.path.exists(self.cities_file):
            with open(self.cities_file, "r", encoding="utf-8") as f:
                self.usa_cities = [line.strip() for line in f if line.strip()]
        else:
            self.usa_cities = []

        # Prepare CSV output file if not exists
        if not os.path.exists(self.output_file):
            with open(self.output_file, 'w', newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["name", "phone", "email", "location", "website"])  # header

        self.template = " in "
        self.pages_to_check = []

        self.processed_json_file = f'processed.json'
        self.processed_json_data = self.json_exist_data(self.processed_json_file)

    def calculate_percentage_of_numbers(self,phone):
        total_characters = len(phone)
        digit_count = sum(1 for char in phone if char.isdigit())
        percentage = (digit_count / total_characters) * 100
        return percentage
    
    # Function to extract emails from a given text
    def extract_emails(self, text):
        return parsepy.extract_first_email_from_url(text)
    
    def is_website_available(self, url):
        try:
            # Ensure that the URL includes "http://"
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "http://" + url

            # Remove ".â€¦:" from the URL
            # url = process_url(url)

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            response = requests.get(url, headers=headers, timeout=20)  # Added a timeout to prevent hanging

            # Check for common success status codes (200, 201, 202, etc.)
            if response.status_code // 100 == 2:
                # Parse the HTML
                soup = BeautifulSoup(response.text, "html.parser")

                # Find all <a> tags
                links = soup.find_all("a")
                self.pages_to_check = [url]

                parsed_url = urlparse(url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                # Look for href containing 'contact'
                for link in links:
                    href = link.get("href")
                    if href and "contact" in href.lower():
                        full_url = urljoin(base_url, href)
                        self.pages_to_check.append(full_url)
                        break
                # Look for href containing 'about'
                for link in links:
                    href = link.get("href")
                    if href and "contact" in href.lower():
                        full_url = urljoin(base_url, href)
                        self.pages_to_check.append(full_url)
                        break

                return "Available", url
            return "Not Available", url
        except requests.exceptions.RequestException:
            return "Not Available", url
        except Exception as e:
            return f"Error: {str(e)}", url
    
    def write_json_file(self, data,filename):
        while 1:
            try:
                with open(filename, 'w',encoding='utf-8') as outfile:
                    json.dump(data, outfile,indent=4)
                break
            except Exception as error:
                print("Error in writing Json file: ",error)
                time.sleep(1)

    def read_json_file(self, filename):
        data = {}
        with open(filename,encoding='utf-8') as json_data:
            data = json.load(json_data)
        return data

    def is_file_exist(self, filename):
        if os.path.exists(filename):
            return True
        else:
            return False

    def json_exist_data(self, fileName):
        json_data = []
        if self.is_file_exist(fileName):
            json_data = self.read_json_file(fileName)
        return json_data
    
    def load_keywords(self):
        return [
            'vineyards',
            'wine cellar builders',
            'architects',
            'custom home designers',
            'custom home builders',
        ]

    def google_map_crawler(self):
        try:
            time.sleep(3)
            keywords = self.load_keywords()
            keyword_flag = (self.start_keyword == '')
            city_flag = (self.start_city == '')

            
            for keyword_row in keywords:
                if(keyword_row == self.start_keyword):
                    keyword_flag = True

                index = 0

                while index < len(self.usa_cities):
                    city = self.usa_cities[index]
                    complete_keyword = keyword_row + self.template + city + ', USA'
                    if complete_keyword not in self.processed_json_data:                        
                        print(f"Crawler Logs: Crawling Google Maps for keyword: {complete_keyword}.")
                        try:
                            self.driver.get(f"https://www.google.com/maps/search/{complete_keyword}")
                            time.sleep(8)

                            window_handles = self.driver.window_handles
                            if len(window_handles) > 1:
                                self.driver.switch_to.window(window_handles[0])

                            results = self.driver.find_elements(
                                By.XPATH, "//a[@class='hfpxzc']")
                            break_condition = False
                            focus_element = self.driver.find_element(
                                By.ID, 'zero-input')
                            
                            if len(results) > 0:
                                while not break_condition:
                                    temp = results[-1]
                                    self.actionChains.scroll_to_element(
                                        results[-1]).perform()
                                    self.actionChains.move_to_element(
                                        focus_element).click().perform()
                                    for i in range(3):
                                        self.actionChains.send_keys(
                                            Keys.ARROW_DOWN).perform()
                                        time.sleep(1)
                                    # self.wait_for_element_location_to_be_stable(temp)

                                    results = self.wait.until(EC.presence_of_all_elements_located(
                                        (By.XPATH, "//a[@class='hfpxzc']")))
                                    if results[-1] == temp:
                                        break_condition = True

                            self.google_map_scrapper(complete_keyword)

                            self.processed_json_data.append(complete_keyword)
                            self.write_json_file(self.processed_json_data, self.processed_json_file)

                        except Exception as e:
                            print("Crawler Error:", str(e))
                            self.driver.get("https://www.google.com/maps")
                            pass
                    else:
                        if keyword_flag and city == self.start_city:
                            city_flag = True
                        index += 1
                        continue

                    index += 1
        finally:
            print("Crawler Logs: Scraping finished. Crawler is Stopping.")
            self.driver.quit()

    def google_map_scrapper(self, keyword):
        print(f"Crawler Logs: Scraping results for {keyword}.")
        results = self.driver.find_elements(By.CLASS_NAME, 'hfpxzc')
        # print(len(results))
        try:
            for idx, result_element in enumerate(results):
                # Click the element and wait for popup
                self.actionChains.move_to_element(result_element).click().perform()
                time.sleep(3)  # wait for popup to load

                # Scrape details from the popup
                name, phone, location, website = self.google_map_inner_link_scrap()

                if not website:
                    continue  # retry same element

                if website == location:
                    location = ""

                # Skip if website already processed
                if website in self.processed_json_data:
                    continue

                # Check website availability
                is_available, checked_url = self.is_website_available(website)

                email = ""

                if is_available == "Available":

                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
                    }

                    # Check for emails on email_pages
                    for page in self.pages_to_check:
                        try:
                            response = requests.get(page, headers=headers, timeout=20)
                            soup = BeautifulSoup(response.text, 'html.parser')
                            text_content = soup.get_text(separator=" ")
                            
                            # text_content = ' '.join([p.get_text() for p in
                            #                         soup.find_all(['p', 'div', 'span', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])])
                            emails = self.extract_emails(text_content)
                            # Extract emails from href="mailto:"
                            for a_tag in soup.find_all("a", href=True):
                                if a_tag["href"].startswith("mailto:"):
                                    email = a_tag["href"].replace("mailto:", "").split("?")[0]
                                    emails.add(email)

                            emails = ", ".join(list(emails))

                            if emails:
                                # match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", email)
                                # if match:
                                #     email = match.group()
                                # Save results and mark website as processed
                                self.save_to_csv([name, phone, emails, location, website])
                                print(f"Crawler Logs: Company: {name} saved.")
                                self.processed_json_data.append(website)
                                self.write_json_file(self.processed_json_data, self.processed_json_file)
                                break

                        except requests.exceptions.RequestException as e:
                            print(f"Request error for {page}: {e}")
                        except Exception as e:
                            print(f"Error checking page {page}: {e}")

        except Exception as e:
            print(f"Crawler Error on element {idx}: {str(e)}")


    def google_map_inner_link_scrap(self):
        inner_link_html = BeautifulSoup(self.driver.page_source, "lxml")
        name = inner_link_html.find('h1', 'DUwDvf lfPIob').text.strip()

        try:
            location = inner_link_html.find(
                'div', 'Io6YTe fontBodyMedium kR99db fdkmkc').text.strip()
        except:
            location = ""

        try:
            # Find the span with the phone icon
            phone_icon = inner_link_html.find_all("span", class_="google-symbols NhBTye PHazN")[0]
            
            if phone_icon:
                # Get the parent container (the <div class="AeaXub"> or button that contains both icon + number)
                parent = phone_icon.find_parent("div", class_="AeaXub")
                
                # Inside that parent, grab the phone number div
                phone_div = parent.find("div", class_="Io6YTe fontBodyMedium kR99db fdkmkc")
                
                phone = phone_div.get_text(strip=True) if phone_div else "Not Available"

                check_percentage = self.calculate_percentage_of_numbers(phone)
                if check_percentage<20:
                    phone_icon = inner_link_html.find_all("span", class_="google-symbols NhBTye PHazN")[1]
                    if phone_icon:
                        # Get the parent container (the <div class="AeaXub"> or button that contains both icon + number)
                        parent = phone_icon.find_parent("div", class_="AeaXub")
                        
                        # Inside that parent, grab the phone number div
                        phone_div = parent.find("div", class_="Io6YTe fontBodyMedium kR99db fdkmkc")
                        
                        phone = phone_div.get_text(strip=True) if phone_div else "Not Available"
                    else:
                        phone = "Not Available"
            else:
                phone = "Not Available"
        except Exception as e:
            phone = "Not Available"
        
        # try:
        #     phone = inner_link_html.find_all(
        #         'div', 'Io6YTe fontBodyMedium kR99db fdkmkc')[2].text.strip()
        # except:
        #     phone = "Not Available"

        try:
            link_tag = inner_link_html.find("a", {"data-item-id": "authority"})

            if link_tag and link_tag.has_attr("href"):
                website = link_tag["href"]
            else:
                website = ""
        except:
            website = ""

        return name, phone, location, website

    def save_to_csv(self, row):
        with open(self.output_file, 'a', newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)


# Run crawler
if __name__ == "__main__":
    crawler = GoogleMaps()
    time.sleep(5)
    crawler.google_map_crawler()
