import requests
from bs4 import BeautifulSoup
import json
import csv
import time
from datetime import datetime
import random
import re
import os

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timezone


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


SCRAPER_API_KEY = 'fb5ba301bdc2ad880be6b081fe626753'
# PROXIES = {
#     "http": f"http://scraperapi.render=true:{SCRAPER_API_KEY}@proxy-server.scraperapi.com:8001",
#     "https": f"http://scraperapi.render=true:{SCRAPER_API_KEY}@proxy-server.scraperapi.com:8001"
# }

from_email = 'admin@uniquefleetautoclub.com'
from_email_password = 'Uniquechobits1@1377'
to_emails = ["aburkhead@findlayinternational.com", "superdev0205@outlook.com"]

processed_json_file = f'processed.json'
processed_json_data = json_exist_data(processed_json_file)

def send_email(file_name, subject, body):
    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = from_email
    # msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # Open the CSV file in binary mode
    with open(file_name, 'rb') as attachment:
        # Create a MIMEBase object
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        # Encode the payload using Base64
        encoders.encode_base64(part)
        # Add header as key/value pair to attachment part
        part.add_header('Content-Disposition', f'attachment; filename={file_name}')
        # Attach the attachment to the MIMEMultipart object
        msg.attach(part)

    # Create SMTP session
    with smtplib.SMTP('smtp.ionos.com', 587) as server:
        server.starttls()  # Enable security
        server.login(from_email, from_email_password)  # Log in to your email account
        # Send email to each recipient
        for to_email in to_emails:
            msg['To'] = to_email
            server.send_message(msg)  # Send the email
            del msg['To']  # Remove the To field for the next iteration

    print("Email sent successfully!")


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

def convert_date(avai):
    if avai == '0':
        return 'Available Now'
    elif avai != 'N/A':
        try:
            avai_datetime = datetime.fromtimestamp(float(avai) / 1000)
            return "Available at " + avai_datetime.strftime('%m/%d/%Y')
        except ValueError:
            return avai
    else:
        return 'N/A'

def return_av_lease(soup):
    avai = "Off Market"  # Initialize avai
    lease = "No Information"  # Initialize lease
    elements = soup.find_all(class_='Text-c11n-8-100-1__sc-aiai24-0 hdp__sc-1hoxd7t-2 jbRdkh iWQNvU')
    for element in elements:
        if 'Available' in element.text:
            avai = element.text
    leases = soup.find_all(class_='Text-c11n-8-100-1__sc-aiai24-0 jbRdkh')
    for lease_element in leases:
        if 'Lease' in lease_element.text:
            lease = lease_element.text
    return avai,lease

def get_avai(url):
    burp0_url = f"https://www.zillow.com:443{url}"
    burp0_cookies = {"zguid": "24|%2466e4f44f-5861-4651-9656-855b5a2d0df0", 
                     "zjs_anonymous_id": "%2266e4f44f-5861-4651-9656-855b5a2d0df0%22", 
                     "zjs_user_id": "%22X1-ZUqjw3rjbr1hc9_4n5nw%22", 
                     "zg_anonymous_id": "%22fa9e5d2f-c22b-4e44-8d2f-566d95a94a2c%22", 
                     "_pxvid": "17fe4d28-8c94-11ef-9bb4-16a0f7ee56f2", 
                     "AWSALB": "JnD3hu79G0K/uiDpqw5CX9uUswS5YXca7raSftwTQMTCnI1OZosGozyVb7+NasThAcezO4iiiTBiXOPNAJyNdD8nDVz4ZE2HTZuJb+rgCY37BcA8krsxIUg1FFZn", 
                     "AWSALBCORS": "JnD3hu79G0K/uiDpqw5CX9uUswS5YXca7raSftwTQMTCnI1OZosGozyVb7+NasThAcezO4iiiTBiXOPNAJyNdD8nDVz4ZE2HTZuJb+rgCY37BcA8krsxIUg1FFZn", 
                     "_ga": "GA1.2.1291462491.1729175317", "_gid": "GA1.2.640570142.1729175317", 
                     "_px3": "600153cd345c86d349b2ad982f8676e5a8f1ea56ad26053f45b309103dabe468:qZDLdgZvv56wR2J2Oh1IeHPoDVh+JZdNgJB8kgZPOexmGaFA3nQfokUMj+WfCf/+oTNDDWIol3rmY4Tw0mo8OA==:1000:/GwKU+Fq+h75XeDzNtJ7JzNY2iAIQYhd33pwNm15+mQxfkE33ubiNqMzSzGT8FEmeUt9KyDd17a4XHaR9IigtOtUUXhFXjaEhrNZGKfVuGFmcADi21WHUgbfJ8Fuob06A7TSwo//BEuonBU8AjqIcKJ/ThE6mht63gSDP+tcn2bBSbOuKKk8xG2VJfRvxsT8jvRo+Il4bxKv67IlVsh20qk/PWiaAuNOvQKc9Ye8RNg=", 
                     "_gcl_au": "1.1.948413509.1729175318", 
                     "_pin_unauth": "dWlkPU1HTXpZelZpT0RZdE5qZzJPQzAwTmpVd0xUaGlPV0V0TURGak1UazBOMlZqTW1RMw", 
                     "_scid": "wAeJ8pb9VKN_d_qSPkwjysQcRXw9HB1u", 
                     "_fbp": "fb.1.1729175320152.700787459305873457", 
                     "_tt_enable_cookie": "1", 
                     "_ttp": "l8_XqtA4S4tjJcXYTmCndHhrFix", 
                     "tfpsi": "f71ad07b-1abb-464c-8b58-baf22f845fc9", 
                     "_clck": "1y2akle%7C2%7Cfq3%7C0%7C1751", 
                     "_sctr": "1%7C1729098000000", "_clsk": "7hsgkt%7C1729183934243%7C70%7C0%7Cq.clarity.ms%2Fcollect", "g_state": "{\"i_l\":0}", "search": "6|1731775930692%7Crect%3D41.23488143862529%2C-73.95959615707397%2C41.20808941910242%2C-74.00980710983276%26rid%3D831324%26disp%3Dmap%26mdm%3Dauto%26p%3D1%26z%3D1%26listPriceActive%3D1%26type%3Dhouse%2Ccondo%2Ctownhouse%2Capartment%26fs%3D0%26fr%3D1%26mmm%3D0%26rs%3D0%26ah%3D0%26singlestory%3D0%26housing-connector%3D0%26parking-spots%3Dnull-%26abo%3D0%26garage%3D0%26pool%3D0%26ac%3D0%26waterfront%3D0%26finished%3D0%26unfinished%3D0%26cityview%3D0%26mountainview%3D0%26parkview%3D0%26waterview%3D0%26hoadata%3D1%26zillow-owned%3D0%263dhome%3D0%26featuredMultiFamilyBuilding%3D0%26student-housing%3D0%26income-restricted-housing%3D0%26military-housing%3D0%26disabled-housing%3D0%26senior-housing%3D0%26excludeNullAvailabilityDates%3D0%26isRoomForRent%3D0%26isEntirePlaceForRent%3D1%26ita%3D0%26stl%3D0%26fur%3D0%26os%3D0%26ca%3D0%26np%3D0%26hasDisabledAccess%3D0%26hasHardwoodFloor%3D0%26areUtilitiesIncluded%3D0%26highSpeedInternetAvailable%3D0%26elevatorAccessAvailable%3D0%26commuteMode%3Ddriving%26commuteTimeOfDay%3Dnow%09%09831324%09%7B%22isList%22%3Atrue%2C%22isMap%22%3Atrue%7D%09%09%09%09%09", "__gads": "ID=fa0d01b742e4f578:T=1729175354:RT=1729183930:S=ALNI_MZF7EGaoRM33CRmybOimIcYM21pjg", "__gpi": "UID=00000f4766ae0848:T=1729175354:RT=1729183930:S=ALNI_MYTPbBPVwcuyDAsmbLaA5IBCLJxZA", "__eoi": "ID=a5a0afc37c2a862c:T=1729175354:RT=1729183930:S=AA-AfjYLf-5leTZYwSXFsbB16og0", "FSsampler": "1870515537", "zgsession": "1|5fdf14e3-0986-4774-a27b-cdbd4c7d83cc", "JSESSIONID": "E856DE4FA14B59EC2E7EB03F568A8A5C", "pxcts": "77ab62ad-8ca4-11ef-915f-aab49f37b036", "DoubleClickSession": "true", "ZILLOW_SSID": "1|AAAAAVVbFRIBVVsVEmAgSpxsoVTCM3V6oxVITXWl0HnIkZsC6GoDxYeu9DJZdn8l03lBKD9zSkLsDowgpwOD%2FssINO7ZAlPYPw", "ZILLOW_SID": "1|AAAAAVVbFRIBVVsVEu5PpbsCkHNFpsqjWqyP6KU%2FR41P6DqW2wADeIsnkaubk0o7Jzu4VqU0tRRRC7mjDm4lUfBRl2XM5h2A2A", "userid": "X|3|f050b377d535096%7C2%7CVtJcGWp00Vs32LcbnR3Wf9a3UaThUMl-XA37tIEQLEE%3D", "loginmemento": "1|e89437c63784e1017b1f04fe7574fff23d07949e39817e5b57e3abb63b923c07", "_dd_s": "rum=0&expire=1729185151356", "_uetsid": "1ab245308c9411ef83aa11591c1f167f", "_uetvid": "1ab270e08c9411efbe498955ce6d09cc", "_rdt_uuid": "1729175320143.1ac615ed-0e6f-43c5-b542-7d8a50092aea", "_scid_r": "04eJ8pb9VKN_d_qSPkwjysQcRXw9HB1u-TQwAw"}
    burp0_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0", 
                     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate, br", "Upgrade-Insecure-Requests": "1", "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "none", "Sec-Fetch-User": "?1", "Priority": "u=0, i", "Te": "trailers"}
    try:
        # xx = requests.get(burp0_url, headers=burp0_headers, cookies=burp0_cookies)
        payload = {'api_key': SCRAPER_API_KEY, 'url': burp0_url}
        xx=requests.get('https://api.scraperapi.com', params=payload)
        html_content = xx.content
        soup = BeautifulSoup(html_content, 'html.parser')
        avai, lease= return_av_lease(soup)
    except:
        avai='No Infor'
        lease='No Infor'
    return avai,lease
 
def get_link(position, max_retries=30, delay=5):
    attempt = 0
    while True:
        try:
            print(f"Start Crawling Keyword: {position}, Attempt {attempt+1}")
            z0_url = f"https://www.zillow.com/{position}/rentals/"
            payload = {'api_key': SCRAPER_API_KEY, 'url': z0_url}
            response = requests.get('https://api.scraperapi.com', params=payload)
            response.raise_for_status()  # Raise HTTPError for bad responses
            
            soup = BeautifulSoup(response.content, 'html.parser')
            script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
            if not script_tag:
                raise ValueError("Script tag not found")
            
            json_data = json.loads(script_tag.string)
            total_pages = json_data["props"]["pageProps"]["searchPageState"]["cat1"]["searchList"]["totalPages"]
            pridata = json_data["props"]["pageProps"]["searchPageState"]["cat1"]["searchResults"]["listResults"]
            
            # Success
            return total_pages, pridata
        
        except (requests.RequestException, ValueError, json.JSONDecodeError) as e:
            attempt += 1
            print(f"Error: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
            if max_retries and attempt >= max_retries:
                print("Max retries reached. Exiting...")
                return None, None

# def get_link(position):
#     print(f"Start Crawling Key word: {position}")
#     z0_url = f"https://www.zillow.com/{position}/rentals/"
#     z0_headers = {"Sec-Ch-Ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\"", "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"Windows\"", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.71 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Sec-Fetch-Site": "none", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "en-US,en;q=0.9", "Priority": "u=0, i"}
#     # burp0_cookies = {"zguid": "24|%2466e4f44f-5861-4651-9656-855b5a2d0df0", "zjs_anonymous_id": "%2266e4f44f-5861-4651-9656-855b5a2d0df0%22", "zjs_user_id": "%22X1-ZUqjw3rjbr1hc9_4n5nw%22", "zg_anonymous_id": "%22fa9e5d2f-c22b-4e44-8d2f-566d95a94a2c%22", "_pxvid": "17fe4d28-8c94-11ef-9bb4-16a0f7ee56f2", "AWSALB": "z/5jYeUndo3BkMk5/18hDPAWe0ahFqgiVlED/Z7HxyJA7uy9YrZQZUKRRcCwbuk5ZJVPLQJrLqJ2pisV+qg8uEJ33D8q6zOhPnhjzTSO3gyj/ynwwTZvZQSU/1fe", "AWSALBCORS": "z/5jYeUndo3BkMk5/18hDPAWe0ahFqgiVlED/Z7HxyJA7uy9YrZQZUKRRcCwbuk5ZJVPLQJrLqJ2pisV+qg8uEJ33D8q6zOhPnhjzTSO3gyj/ynwwTZvZQSU/1fe", "_ga": "GA1.2.1291462491.1729175317", "_gid": "GA1.2.640570142.1729175317", "_px3": "7c5552d5d8f0be823063d7da5b8419f15c8fdc961b2298219450329ba9aa5846:31vtndYDBss2vzfSjcCcJ/hzFfTfuaqF/HXRPul1SuvwQepUj1f4nZrSjCnTe6k/4nHjJwIgrRlHsgxHRg/ZFA==:1000:jBYvcf4aO4rYnpsP8tMbgu8m72UeeRI4Ca5dlmZOio1dTnds1qZXyk6UwhZjZYyJDQtePHXn7PExoT63Z1RLFhkFMU6vlD9sA+K3ZmEbA6p5zSaAGu9XrJniX+vewWGEl1vBYvMI/4dzdDeb5v2PzCTpjqMipEDeho14QRCC00fJEmosQgr/tlmWmLJI3vd0Wj1nc3qWmTrubEsKlSueHwXhBh7wBaZwqsbhnu3+7/Y=", "_gcl_au": "1.1.948413509.1729175318", "_pin_unauth": "dWlkPU1HTXpZelZpT0RZdE5qZzJPQzAwTmpVd0xUaGlPV0V0TURGak1UazBOMlZqTW1RMw", "_scid": "wAeJ8pb9VKN_d_qSPkwjysQcRXw9HB1u", "_fbp": "fb.1.1729175320152.700787459305873457", "_tt_enable_cookie": "1", "_ttp": "l8_XqtA4S4tjJcXYTmCndHhrFix", "tfpsi": "f71ad07b-1abb-464c-8b58-baf22f845fc9", "_clck": "1y2akle%7C2%7Cfq3%7C0%7C1751", "_sctr": "1%7C1729098000000", "_clsk": "7hsgkt%7C1729182480439%7C67%7C0%7Cq.clarity.ms%2Fcollect", "g_state": "{\"i_l\":0}", "search": "6|1731774475672%7Crect%3D41.37533607867494%2C-73.65913887792968%2C40.946268771386066%2C-74.4625141220703%26rid%3D2515%26disp%3Dmap%26mdm%3Dauto%26p%3D1%26z%3D0%26listPriceActive%3D1%26type%3Dhouse%2Ccondo%2Ctownhouse%2Capartment%26fs%3D0%26fr%3D1%26mmm%3D0%26rs%3D0%26ah%3D0%26singlestory%3D0%26housing-connector%3D0%26parking-spots%3Dnull-%26abo%3D0%26garage%3D0%26pool%3D0%26ac%3D0%26waterfront%3D0%26finished%3D0%26unfinished%3D0%26cityview%3D0%26mountainview%3D0%26parkview%3D0%26waterview%3D0%26hoadata%3D1%26zillow-owned%3D0%263dhome%3D0%26featuredMultiFamilyBuilding%3D0%26student-housing%3D0%26income-restricted-housing%3D0%26military-housing%3D0%26disabled-housing%3D0%26senior-housing%3D0%26excludeNullAvailabilityDates%3D0%26isRoomForRent%3D0%26isEntirePlaceForRent%3D1%26ita%3D0%26stl%3D0%26fur%3D0%26os%3D0%26ca%3D0%26np%3D0%26hasDisabledAccess%3D0%26hasHardwoodFloor%3D0%26areUtilitiesIncluded%3D0%26highSpeedInternetAvailable%3D0%26elevatorAccessAvailable%3D0%26commuteMode%3Ddriving%26commuteTimeOfDay%3Dnow%09%092515%09%7B%22isList%22%3Atrue%2C%22isMap%22%3Atrue%7D%09%09%09%09%09", "__gads": "ID=fa0d01b742e4f578:T=1729175354:RT=1729182387:S=ALNI_MZF7EGaoRM33CRmybOimIcYM21pjg", "__gpi": "UID=00000f4766ae0848:T=1729175354:RT=1729182387:S=ALNI_MYTPbBPVwcuyDAsmbLaA5IBCLJxZA", "__eoi": "ID=a5a0afc37c2a862c:T=1729175354:RT=1729182387:S=AA-AfjYLf-5leTZYwSXFsbB16og0", "FSsampler": "1870515537", "_rdt_uuid": "1729175320143.1ac615ed-0e6f-43c5-b542-7d8a50092aea", "_scid_r": "0oeJ8pb9VKN_d_qSPkwjysQcRXw9HB1u-TQwAg", "zgsession": "1|5fdf14e3-0986-4774-a27b-cdbd4c7d83cc", "_dd_s": "rum=0&expire=1729183282222", "JSESSIONID": "E856DE4FA14B59EC2E7EB03F568A8A5C", "pxcts": "77ab62ad-8ca4-11ef-915f-aab49f37b036", "DoubleClickSession": "true", "ZILLOW_SSID": "1|AAAAAVVbFRIBVVsVEmAgSpxsoVTCM3V6oxVITXWl0HnIkZsC6GoDxYeu9DJZdn8l03lBKD9zSkLsDowgpwOD%2FssINO7ZAlPYPw", "ZILLOW_SID": "1|AAAAAVVbFRIBVVsVEu5PpbsCkHNFpsqjWqyP6KU%2FR41P6DqW2wADeIsnkaubk0o7Jzu4VqU0tRRRC7mjDm4lUfBRl2XM5h2A2A", "userid": "X|3|f050b377d535096%7C2%7CVtJcGWp00Vs32LcbnR3Wf9a3UaThUMl-XA37tIEQLEE%3D", "loginmemento": "1|e89437c63784e1017b1f04fe7574fff23d07949e39817e5b57e3abb63b923c07", "_uetsid": "1ab245308c9411ef83aa11591c1f167f", "_uetvid": "1ab270e08c9411efbe498955ce6d09cc"}    
#     # xx=requests.get(z0_url, headers=z0_headers, cookies=burp0_cookies)
#     print(z0_url)
#     payload = {'api_key': SCRAPER_API_KEY, 'url': z0_url}
#     xx=requests.get('https://api.scraperapi.com', params=payload)
#     soup = BeautifulSoup(xx.content, 'html.parser')    
#     script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
    
#     script_content = script_tag.string
#     json_data = json.loads(script_content)
#     total_pages = json_data["props"]["pageProps"]["searchPageState"]["cat1"]["searchList"]["totalPages"]
#     pridata= json_data["props"]["pageProps"]["searchPageState"]["cat1"]["searchResults"]["listResults"]
#     return total_pages, pridata

def run_url(burp0_url):
    global processed_json_data, processed_json_file
    print(f"[INFO]: Fetching URL: {burp0_url}")
    burp0_cookies = {"zguid": "24|%2466e4f44f-5861-4651-9656-855b5a2d0df0", "zjs_anonymous_id": "%2266e4f44f-5861-4651-9656-855b5a2d0df0%22", "zjs_user_id": "%22X1-ZUqjw3rjbr1hc9_4n5nw%22", "zg_anonymous_id": "%22fa9e5d2f-c22b-4e44-8d2f-566d95a94a2c%22", "_pxvid": "17fe4d28-8c94-11ef-9bb4-16a0f7ee56f2", "AWSALB": "z/5jYeUndo3BkMk5/18hDPAWe0ahFqgiVlED/Z7HxyJA7uy9YrZQZUKRRcCwbuk5ZJVPLQJrLqJ2pisV+qg8uEJ33D8q6zOhPnhjzTSO3gyj/ynwwTZvZQSU/1fe", "AWSALBCORS": "z/5jYeUndo3BkMk5/18hDPAWe0ahFqgiVlED/Z7HxyJA7uy9YrZQZUKRRcCwbuk5ZJVPLQJrLqJ2pisV+qg8uEJ33D8q6zOhPnhjzTSO3gyj/ynwwTZvZQSU/1fe", "_ga": "GA1.2.1291462491.1729175317", "_gid": "GA1.2.640570142.1729175317", "_px3": "7c5552d5d8f0be823063d7da5b8419f15c8fdc961b2298219450329ba9aa5846:31vtndYDBss2vzfSjcCcJ/hzFfTfuaqF/HXRPul1SuvwQepUj1f4nZrSjCnTe6k/4nHjJwIgrRlHsgxHRg/ZFA==:1000:jBYvcf4aO4rYnpsP8tMbgu8m72UeeRI4Ca5dlmZOio1dTnds1qZXyk6UwhZjZYyJDQtePHXn7PExoT63Z1RLFhkFMU6vlD9sA+K3ZmEbA6p5zSaAGu9XrJniX+vewWGEl1vBYvMI/4dzdDeb5v2PzCTpjqMipEDeho14QRCC00fJEmosQgr/tlmWmLJI3vd0Wj1nc3qWmTrubEsKlSueHwXhBh7wBaZwqsbhnu3+7/Y=", "_gcl_au": "1.1.948413509.1729175318", "_pin_unauth": "dWlkPU1HTXpZelZpT0RZdE5qZzJPQzAwTmpVd0xUaGlPV0V0TURGak1UazBOMlZqTW1RMw", "_scid": "wAeJ8pb9VKN_d_qSPkwjysQcRXw9HB1u", "_fbp": "fb.1.1729175320152.700787459305873457", "_tt_enable_cookie": "1", "_ttp": "l8_XqtA4S4tjJcXYTmCndHhrFix", "tfpsi": "f71ad07b-1abb-464c-8b58-baf22f845fc9", "_clck": "1y2akle%7C2%7Cfq3%7C0%7C1751", "_sctr": "1%7C1729098000000", "_clsk": "7hsgkt%7C1729182480439%7C67%7C0%7Cq.clarity.ms%2Fcollect", "g_state": "{\"i_l\":0}", "search": "6|1731774475672%7Crect%3D41.37533607867494%2C-73.65913887792968%2C40.946268771386066%2C-74.4625141220703%26rid%3D2515%26disp%3Dmap%26mdm%3Dauto%26p%3D1%26z%3D0%26listPriceActive%3D1%26type%3Dhouse%2Ccondo%2Ctownhouse%2Capartment%26fs%3D0%26fr%3D1%26mmm%3D0%26rs%3D0%26ah%3D0%26singlestory%3D0%26housing-connector%3D0%26parking-spots%3Dnull-%26abo%3D0%26garage%3D0%26pool%3D0%26ac%3D0%26waterfront%3D0%26finished%3D0%26unfinished%3D0%26cityview%3D0%26mountainview%3D0%26parkview%3D0%26waterview%3D0%26hoadata%3D1%26zillow-owned%3D0%263dhome%3D0%26featuredMultiFamilyBuilding%3D0%26student-housing%3D0%26income-restricted-housing%3D0%26military-housing%3D0%26disabled-housing%3D0%26senior-housing%3D0%26excludeNullAvailabilityDates%3D0%26isRoomForRent%3D0%26isEntirePlaceForRent%3D1%26ita%3D0%26stl%3D0%26fur%3D0%26os%3D0%26ca%3D0%26np%3D0%26hasDisabledAccess%3D0%26hasHardwoodFloor%3D0%26areUtilitiesIncluded%3D0%26highSpeedInternetAvailable%3D0%26elevatorAccessAvailable%3D0%26commuteMode%3Ddriving%26commuteTimeOfDay%3Dnow%09%092515%09%7B%22isList%22%3Atrue%2C%22isMap%22%3Atrue%7D%09%09%09%09%09", "__gads": "ID=fa0d01b742e4f578:T=1729175354:RT=1729182387:S=ALNI_MZF7EGaoRM33CRmybOimIcYM21pjg", "__gpi": "UID=00000f4766ae0848:T=1729175354:RT=1729182387:S=ALNI_MYTPbBPVwcuyDAsmbLaA5IBCLJxZA", "__eoi": "ID=a5a0afc37c2a862c:T=1729175354:RT=1729182387:S=AA-AfjYLf-5leTZYwSXFsbB16og0", "FSsampler": "1870515537", "_rdt_uuid": "1729175320143.1ac615ed-0e6f-43c5-b542-7d8a50092aea", "_scid_r": "0oeJ8pb9VKN_d_qSPkwjysQcRXw9HB1u-TQwAg", "zgsession": "1|5fdf14e3-0986-4774-a27b-cdbd4c7d83cc", "_dd_s": "rum=0&expire=1729183282222", "JSESSIONID": "E856DE4FA14B59EC2E7EB03F568A8A5C", "pxcts": "77ab62ad-8ca4-11ef-915f-aab49f37b036", "DoubleClickSession": "true", "ZILLOW_SSID": "1|AAAAAVVbFRIBVVsVEmAgSpxsoVTCM3V6oxVITXWl0HnIkZsC6GoDxYeu9DJZdn8l03lBKD9zSkLsDowgpwOD%2FssINO7ZAlPYPw", "ZILLOW_SID": "1|AAAAAVVbFRIBVVsVEu5PpbsCkHNFpsqjWqyP6KU%2FR41P6DqW2wADeIsnkaubk0o7Jzu4VqU0tRRRC7mjDm4lUfBRl2XM5h2A2A", "userid": "X|3|f050b377d535096%7C2%7CVtJcGWp00Vs32LcbnR3Wf9a3UaThUMl-XA37tIEQLEE%3D", "loginmemento": "1|e89437c63784e1017b1f04fe7574fff23d07949e39817e5b57e3abb63b923c07", "_uetsid": "1ab245308c9411ef83aa11591c1f167f", "_uetvid": "1ab270e08c9411efbe498955ce6d09cc"}
    burp0_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate, br", "Upgrade-Insecure-Requests": "1", "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "none", "Sec-Fetch-User": "?1", "Priority": "u=0, i", "Te": "trailers"}
    try:
        # response = requests.get(burp0_url, headers=burp0_headers, cookies=burp0_cookies)
        payload = {'api_key': SCRAPER_API_KEY, 'url': burp0_url}
        response=requests.get('https://api.scraperapi.com', params=payload)
        # time.sleep(random.randint(4,8))
        if response.status_code != 200:
            print(f"Failed to fetch data from {burp0_url} with status code {response.status_code}")
            if response.status_code == 404:
                return response.status_code
            return None
        soup = BeautifulSoup(response.content, 'html.parser')
        available,leaseterm = return_av_lease(soup)          
        script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
        script_content = script_tag.string
        data = json.loads(script_content)
        rows = []
        building_info = data.get("props", {}).get("pageProps", {}).get("componentProps", {}).get("initialReduxState", {}).get("gdp", {}).get("building", {})
        client_info = data.get("props", {}).get("pageProps", {}).get("componentProps", {}).get("gdpClientCache", {})
        if client_info:
            index = client_info.find("homeStatus")
            # Check if the substring was found
            if index != -1:
                index = index + 13
                # Extract the substring of 5 characters starting from the found index
                result = client_info[index:index + 10]
                if result.find("FOR_RENT") == -1:
                    print("It is not active rental properties")
                    return rows
        
        if building_info and isinstance(building_info, dict):
            street_address = building_info.get("streetAddress", "N/A")
            building_name = building_info.get("buildingName", "") or street_address
            city = building_info.get("city", "N/A")
            state = building_info.get("state", "N/A")
            zipcode = building_info.get("zipcode", "N/A")
            floor_plans = building_info.get("floorPlans", [])
            ungrouped_units = building_info.get("ungroupedUnits", [])
            disc = building_info.get("description", "N/A")
            
            if disc and disc != "N/A":
                disc = disc.replace("\n", ".").replace(",", "-")
            if floor_plans:
                for i, plan in enumerate(floor_plans):
                    units = plan.get('units', None)  # Lấy thông tin units, có thể là None
                    lease_term = plan.get('leaseTerm', 'N/A')
                    if lease_term and lease_term != "N/A":
                        lease_term = lease_term.replace("\n", ".").replace(",", "-")# Lấy leaseTerm từ kế hoạch sàn
                    bedrooms = plan.get('beds', 'N/A')
                    bathrooms = plan.get('baths', 'N/A')
                    sqft = plan.get('sqft', 'N/A')
                    price = plan.get('minPrice', 'N/A')  # Lấy minPrice nếu không có unit
                    unit_number = plan.get('name', 'N/A')
                    if unit_number is None:
                        unit_number = "N/A"
                    avai=plan.get('availableFrom','N/A')# Lấy tên plan làm unit_number nếu không có unit
                    av=convert_date(avai)
                    if units:  # Kiểm tra nếu units không phải là None hoặc rỗng
                        for j, unit in enumerate(units):
                            unit_number = unit.get('unitNumber', 'N/A')
                            if unit_number is None:
                                unit_number = "N/A"
                            price = unit.get('price', 'N/A')
                            sqft = unit.get('sqft', 'N/A')
                            avai = unit.get('availableFrom', 'N/A')
                            av=convert_date(avai)
                            if price is not None and int(price) >= 2500:
                                rows.append([
                                    building_name,
                                    street_address,
                                    city,
                                    state,
                                    zipcode,
                                    bedrooms,
                                    bathrooms,
                                    unit_number,
                                    price,
                                    sqft,
                                    av,      # Availability
                                    lease_term,  # Leasing Term lấy từ kế hoạch sàn
                                    disc        # Description
                                ])
                                print("[success]: unit_number = " + unit_number)
                    else:  # Nếu không có units, lấy thông tin từ kế hoạch sàn
                        if price is not None and int(price) >= 2500:
                            rows.append([
                                building_name,
                                street_address,
                                city,
                                state,
                                zipcode,
                                bedrooms,
                                bathrooms,
                                unit_number,  # Lấy từ kế hoạch sàn
                                price,        # Lấy minPrice từ kế hoạch sàn
                                sqft,         # Lấy từ kế hoạch sàn
                                av,        # Availability
                                lease_term,   # Leasing Term
                                disc          # Description
                            ])
                            print("[success]: unit_number = " + unit_number)
            elif ungrouped_units:
                for k, unit in enumerate(ungrouped_units):                    
                    listingType = unit.get('listingType', 'N/A')
                    unit_number = unit.get('unitNumber', 'N/A')
                    price = unit.get('price', 'N/A')

                    bedrooms = unit.get('beds', 'N/A')
                    bathrooms = unit.get('baths', 'N/A')
                    sqft = unit.get('sqft', 'N/A')
                    hdpUrl=unit.get('hdpUrl', 'N/A')
                    if listingType == "FOR_RENT" and unit_number is not None and price is not None and int(price) >= 2500:
                        avai,lease= get_avai(hdpUrl)
                        rows.append([
                            building_name,
                            street_address,
                            city,
                            state,
                            zipcode,
                            bedrooms,
                            bathrooms,
                            unit_number,
                            price,
                            sqft,
                            avai,  # Availability
                            lease,  # Leasing Term
                            disc   # Description
                        ])
                        print("[success]: unit_number = " + unit_number)
            else:
                print("[WARN]: No floor plans or ungrouped units found.")
        else:
            try:
                gdp_cache = json.loads(data['props']['pageProps']['componentProps']['gdpClientCache'])
                first_key = next(iter(gdp_cache))
                property_data = gdp_cache[first_key]['property']
                desc=property_data.get('description', 'N/A')
                if desc and desc != "N/A":
                    desc = desc.replace("\n", " ").replace(",", "-")
                if property_data.get('price', 'N/A') is not None and int(property_data.get('price', 'N/A')) >= 2500:
                    rows.append([
                        "No Information",  # Building Name
                        property_data.get('streetAddress', 'N/A'),
                        property_data.get('city', 'N/A'),
                        property_data.get('state', 'N/A'),
                        property_data.get('zipcode', 'N/A'),
                        property_data.get('bedrooms', 'N/A'),
                        property_data.get('bathrooms', 'N/A'),
                        "No Information",  # Unit Number
                        property_data.get('price', 'N/A'),
                        property_data.get('livingArea', 'N/A'),  # SQFT
                        available,  # Availability
                        leaseterm,  # Leasing Term
                        desc
                        # Description
                    ])
            except Exception as e:
                print(f"[ERR2]: {str(e)}")

        processed_json_data.append(burp0_url)
        write_json_file(processed_json_data, processed_json_file)
        return rows
    except Exception as e:
        print(f"[ERR1]: {str(e)}")

def main():
    global processed_json_data, processed_json_file
    replace_non_alphanumeric('list.txt')
    try:
        with open('./list.txt', 'r') as file:
            key_words = file.read().splitlines()
        
        file_name = f'output_zillow.csv'
        # Check if the file exists
        file_exists = os.path.exists(file_name)
        with open(file_name, 'a', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            if not file_exists:
                csv_writer.writerow(["Complex Name", "Address", "City", "State", "Zip", "Bedrooms", "Bathrooms", "Unit Number", "Price", "SQFT", "Availability", "Leasing Term", "Description"])

            for key_word in key_words:
                data_slug = key_word.replace(',', '').replace(' ', '-').lower()
                if data_slug not in processed_json_data:
                    total_pages, pridata = get_link(key_word)
                    if total_pages == 1:
                        for data in pridata:
                            price_scrap = False
                            if "unformattedPrice" in data:
                                if int(data["unformattedPrice"]) >= 2500:
                                    price_scrap = True
                            else:
                                priceData = data["units"]
                                for item in priceData:   
                                    cleaned_price = item["price"].replace('$', '').replace(',', '').replace('+', '')
                                    if cleaned_price.isnumeric():
                                        if int(cleaned_price) >= 2500:
                                            price_scrap = True
                                            break
                            url=data["detailUrl"]
                            if "https://www.zillow.com" not in url:
                                url = "https://www.zillow.com" + url
                            if url not in processed_json_data and price_scrap == True and url != "https://www.zillow.com/apartments/oakland-ca/experience-the-one-piedmont-lifestyle-oakland's-newest-majestic-contemporary-oasis-right-on-piedm.../CgJ9FK/":
                                rows=run_url(url)
                                csv_writer.writerows(rows)
                            # time.sleep(1)           
                    else:
                        for i in range(1, total_pages):
                            while True:  # Start a loop to retry on error
                                try:
                                    z1_url = f"https://www.zillow.com:443/{key_word}/rentals/{i}_p/"
                                    z1_headers = {"Accept-Encoding": "gzip, deflate, br", "Accept": "*/*", "Accept-Language": "en-US;q=0.9,en;q=0.8", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.71 Safari/537.36", "Cache-Control": "max-age=0", "Referer": "https://www.zillow.com/ca/fsbo/2_p"}
                                    # burp0_cookies = {"zguid": "24|%2466e4f44f-5861-4651-9656-855b5a2d0df0", "zjs_anonymous_id": "%2266e4f44f-5861-4651-9656-855b5a2d0df0%22", "zjs_user_id": "%22X1-ZUqjw3rjbr1hc9_4n5nw%22", "zg_anonymous_id": "%22fa9e5d2f-c22b-4e44-8d2f-566d95a94a2c%22", "_pxvid": "17fe4d28-8c94-11ef-9bb4-16a0f7ee56f2", "AWSALB": "z/5jYeUndo3BkMk5/18hDPAWe0ahFqgiVlED/Z7HxyJA7uy9YrZQZUKRRcCwbuk5ZJVPLQJrLqJ2pisV+qg8uEJ33D8q6zOhPnhjzTSO3gyj/ynwwTZvZQSU/1fe", "AWSALBCORS": "z/5jYeUndo3BkMk5/18hDPAWe0ahFqgiVlED/Z7HxyJA7uy9YrZQZUKRRcCwbuk5ZJVPLQJrLqJ2pisV+qg8uEJ33D8q6zOhPnhjzTSO3gyj/ynwwTZvZQSU/1fe", "_ga": "GA1.2.1291462491.1729175317", "_gid": "GA1.2.640570142.1729175317", "_px3": "7c5552d5d8f0be823063d7da5b8419f15c8fdc961b2298219450329ba9aa5846:31vtndYDBss2vzfSjcCcJ/hzFfTfuaqF/HXRPul1SuvwQepUj1f4nZrSjCnTe6k/4nHjJwIgrRlHsgxHRg/ZFA==:1000:jBYvcf4aO4rYnpsP8tMbgu8m72UeeRI4Ca5dlmZOio1dTnds1qZXyk6UwhZjZYyJDQtePHXn7PExoT63Z1RLFhkFMU6vlD9sA+K3ZmEbA6p5zSaAGu9XrJniX+vewWGEl1vBYvMI/4dzdDeb5v2PzCTpjqMipEDeho14QRCC00fJEmosQgr/tlmWmLJI3vd0Wj1nc3qWmTrubEsKlSueHwXhBh7wBaZwqsbhnu3+7/Y=", "_gcl_au": "1.1.948413509.1729175318", "_pin_unauth": "dWlkPU1HTXpZelZpT0RZdE5qZzJPQzAwTmpVd0xUaGlPV0V0TURGak1UazBOMlZqTW1RMw", "_scid": "wAeJ8pb9VKN_d_qSPkwjysQcRXw9HB1u", "_fbp": "fb.1.1729175320152.700787459305873457", "_tt_enable_cookie": "1", "_ttp": "l8_XqtA4S4tjJcXYTmCndHhrFix", "tfpsi": "f71ad07b-1abb-464c-8b58-baf22f845fc9", "_clck": "1y2akle%7C2%7Cfq3%7C0%7C1751", "_sctr": "1%7C1729098000000", "_clsk": "7hsgkt%7C1729182480439%7C67%7C0%7Cq.clarity.ms%2Fcollect", "g_state": "{\"i_l\":0}", "search": "6|1731774475672%7Crect%3D41.37533607867494%2C-73.65913887792968%2C40.946268771386066%2C-74.4625141220703%26rid%3D2515%26disp%3Dmap%26mdm%3Dauto%26p%3D1%26z%3D0%26listPriceActive%3D1%26type%3Dhouse%2Ccondo%2Ctownhouse%2Capartment%26fs%3D0%26fr%3D1%26mmm%3D0%26rs%3D0%26ah%3D0%26singlestory%3D0%26housing-connector%3D0%26parking-spots%3Dnull-%26abo%3D0%26garage%3D0%26pool%3D0%26ac%3D0%26waterfront%3D0%26finished%3D0%26unfinished%3D0%26cityview%3D0%26mountainview%3D0%26parkview%3D0%26waterview%3D0%26hoadata%3D1%26zillow-owned%3D0%263dhome%3D0%26featuredMultiFamilyBuilding%3D0%26student-housing%3D0%26income-restricted-housing%3D0%26military-housing%3D0%26disabled-housing%3D0%26senior-housing%3D0%26excludeNullAvailabilityDates%3D0%26isRoomForRent%3D0%26isEntirePlaceForRent%3D1%26ita%3D0%26stl%3D0%26fur%3D0%26os%3D0%26ca%3D0%26np%3D0%26hasDisabledAccess%3D0%26hasHardwoodFloor%3D0%26areUtilitiesIncluded%3D0%26highSpeedInternetAvailable%3D0%26elevatorAccessAvailable%3D0%26commuteMode%3Ddriving%26commuteTimeOfDay%3Dnow%09%092515%09%7B%22isList%22%3Atrue%2C%22isMap%22%3Atrue%7D%09%09%09%09%09", "__gads": "ID=fa0d01b742e4f578:T=1729175354:RT=1729182387:S=ALNI_MZF7EGaoRM33CRmybOimIcYM21pjg", "__gpi": "UID=00000f4766ae0848:T=1729175354:RT=1729182387:S=ALNI_MYTPbBPVwcuyDAsmbLaA5IBCLJxZA", "__eoi": "ID=a5a0afc37c2a862c:T=1729175354:RT=1729182387:S=AA-AfjYLf-5leTZYwSXFsbB16og0", "FSsampler": "1870515537", "_rdt_uuid": "1729175320143.1ac615ed-0e6f-43c5-b542-7d8a50092aea", "_scid_r": "0oeJ8pb9VKN_d_qSPkwjysQcRXw9HB1u-TQwAg", "zgsession": "1|5fdf14e3-0986-4774-a27b-cdbd4c7d83cc", "_dd_s": "rum=0&expire=1729183282222", "JSESSIONID": "E856DE4FA14B59EC2E7EB03F568A8A5C", "pxcts": "77ab62ad-8ca4-11ef-915f-aab49f37b036", "DoubleClickSession": "true", "ZILLOW_SSID": "1|AAAAAVVbFRIBVVsVEmAgSpxsoVTCM3V6oxVITXWl0HnIkZsC6GoDxYeu9DJZdn8l03lBKD9zSkLsDowgpwOD%2FssINO7ZAlPYPw", "ZILLOW_SID": "1|AAAAAVVbFRIBVVsVEu5PpbsCkHNFpsqjWqyP6KU%2FR41P6DqW2wADeIsnkaubk0o7Jzu4VqU0tRRRC7mjDm4lUfBRl2XM5h2A2A", "userid": "X|3|f050b377d535096%7C2%7CVtJcGWp00Vs32LcbnR3Wf9a3UaThUMl-XA37tIEQLEE%3D", "loginmemento": "1|e89437c63784e1017b1f04fe7574fff23d07949e39817e5b57e3abb63b923c07", "_uetsid": "1ab245308c9411ef83aa11591c1f167f", "_uetvid": "1ab270e08c9411efbe498955ce6d09cc"}
                                    # z1=requests.get(z1_url, headers=z1_headers, cookies=burp0_cookies)
                                    payload = {'api_key': SCRAPER_API_KEY, 'url': z1_url}
                                    z1=requests.get('https://api.scraperapi.com', params=payload)
                                    soup = BeautifulSoup(z1.content, 'html.parser')
                                    script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
                                    script_content = script_tag.string
                                    json_data = json.loads(script_content)
                                    datas  = json_data["props"]["pageProps"]["searchPageState"]["cat1"]["searchResults"]["listResults"]
                                    print(f"Tatal Page: {total_pages}, Current Page: {str(i)}")
                                    for data in datas:
                                        price_scrap = False
                                        if "unformattedPrice" in data:
                                            if int(data["unformattedPrice"]) >= 2500:
                                                price_scrap = True
                                        else:
                                            if "units" in data:                                                
                                                priceData = data["units"]
                                                for item in priceData:
                                                    cleaned_price = item["price"].replace('$', '').replace(',', '').replace('+', '')
                                                    if cleaned_price.isnumeric():
                                                        if int(cleaned_price) >= 2500:
                                                            price_scrap = True
                                                            break
                                        url=data["detailUrl"]
                                        if "https://www.zillow.com" not in url:
                                            url = "https://www.zillow.com" + url
                                        
                                        if url not in processed_json_data and price_scrap == True and url != "https://www.zillow.com/apartments/oakland-ca/experience-the-one-piedmont-lifestyle-oakland's-newest-majestic-contemporary-oasis-right-on-piedm.../CgJ9FK/":
                                            rows=run_url(url)
                                            if rows == 404:
                                                continue
                                            t = 0
                                            while rows is None:
                                                if t > 5:
                                                    break
                                                if rows is None:
                                                    # Optional: Sleep for a short duration to avoid overwhelming the server
                                                    time.sleep(1)
                                                rows = run_url(url)
                                                t = t+1
                                            csv_writer.writerows(rows)
                                        # time.sleep(random.randint(1,5))

                                    break

                                except Exception as e:
                                    print(f"[ERR1]: {str(e)}") 
                                    time.sleep(5)  # Optional: wait before retrying

                    processed_json_data.append(data_slug)
                    write_json_file(processed_json_data, processed_json_file)
        
        # Get the current date
        current_date = datetime.now().date()

        print("Current date:", current_date)

        new_file_name = f'output_zillow({current_date.strftime("%Y%m%d")}).csv'
        
        if os.path.exists(new_file_name):
            print(f"The file {new_file_name} already exists. Choose a different name.")
        else:
            os.rename(file_name, new_file_name)
            print(f"File renamed from {file_name} to {new_file_name}")

        send_email(
            new_file_name,
            subject="Zillow CSV File Attached",
            body="Please find the attached CSV file.",
        )
        print(f"[SUCCESSFULLY]: Data was saved in results file")
    except Exception as e:
        print(e)

main()