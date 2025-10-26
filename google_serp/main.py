import requests
import time
import gspread
import random
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from google.oauth2.service_account import Credentials

from bs4 import BeautifulSoup
import parsepy  # Import your parse.py module


def process_url(url):
    # Try to find the '.com' in the URL
    com_index = url.find('.com')
    if com_index != -1:
        # If '.com' is found, truncate everything after '.com'
        return url[:com_index + 4]
    else:
        # If '.com' is not found, remove '.â€¦:'
        return re.sub(r"\.â€¦:", "", url)
    
# Function to extract emails from a given text
def extract_emails(text):
    return parsepy.extract_first_email_from_url(text)

def is_website_available(url):
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
            return "Available", url
        return "Not Available", url
    except requests.exceptions.RequestException:
        return "Not Available", url
    except Exception as e:
        return f"Error: {str(e)}", url
    

# ✅ 1. GOOGLE SHEETS AUTHENTICATION  
scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("direct-abacus-429205-g5-eb671ae10207.json", scopes=scope)
client = gspread.authorize(creds)

# ✅ 2. OPEN THE GOOGLE SHEET  
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1taj9-JoZigfLU1rWMbF81PHp-poCzji0qAQ0eDBHESI/edit?gid=0"
spreadsheet = client.open_by_url(spreadsheet_url)
worksheet = spreadsheet.worksheet("SEARCHES")

# ✅ 3. GET SEARCH QUERIES FROM GOOGLE SHEET  
data = worksheet.get_all_values()

pages_to_check = ["/", "/contact", "/about", "/about-us", "/contacts", "/contact-us", "/contact_us.php"]

# ✅ 4. SET UP SELENIUM WEBDRIVER  
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Run in background
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--ignore-certificate-errors")
options.add_argument("start-maximized")
options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ✅ 5. LOOP THROUGH SEARCH TERMS  
i = 0
for row in data:
    if i == 0:  # Skip headers
        i += 1
        continue
    
    return_worksheet = spreadsheet.worksheet(f"RETURN {str(i)}")
    return_worksheet.clear()
    return_worksheet.append_row(["Title", "Website", "Description"])
    full_enriched_worksheet = spreadsheet.worksheet(f"FULL ENRICHED {str(i)}")
    full_enriched_worksheet.clear()
    full_enriched_worksheet.append_row(["Title", "Website", "Location", "Email"])
    
    search_term = row[2]  # Get search term from column C
    print(f"Searching for: {search_term}")

    # ✅ 6. OPEN GOOGLE SEARCH

    for page_index in range(0, 100):
        start = page_index*10
        search_url = f"https://www.google.com/search?q={search_term}&start={start}"
        driver.get(search_url)
        time.sleep(random.uniform(3, 6))  # Sleep to avoid detection

        # ✅ 7. SCRAPE SEARCH RESULTS  
        results = driver.find_elements(By.CSS_SELECTOR, "div.tF2Cxc")  # Google search results container
        if len(results) == 0:
            break

        search_results = []
        for result in results:  # Get top 5 results
            title = result.find_element(By.TAG_NAME, "h3").text
            link = result.find_element(By.TAG_NAME, "a").get_attribute("href")
            try:
                desc = result.find_element(By.CSS_SELECTOR, "div.VwiC3b").text
            except:
                desc = ""

            return_worksheet.append_row([title, link, desc])

            is_available, checked_url = is_website_available(link)

            email = ""

            if is_available == "Available":

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
                }

                # Check for emails on email_pages
                for page in pages_to_check:
                    try:
                        full_url = checked_url.rstrip('/') + page
                        print(full_url)
                        response = requests.get(full_url, headers=headers, timeout=20)
                        soup = BeautifulSoup(response.text, 'html.parser')
                        text_content = ' '.join([p.get_text() for p in
                                                soup.find_all(['p', 'div', 'span', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])])
                        email = extract_emails(text_content)
                        
                        if email:
                            full_enriched_worksheet.append_row([title, link, row[1], email])
                            break  # Exit the loop if emails are found on any page
                    except requests.exceptions.RequestException as e:
                        continue
                    except Exception as e:
                        continue
            
            search_results.append([title, link, desc])
        
        # # ✅ 8. WRITE RESULTS TO GOOGLE SHEETS  
        # row_index = i  # Row number to update
        # if search_results:
        #     worksheet.update(f"D{row_index}:E{row_index}", search_results)  # Writing results into columns D & E

        time.sleep(random.uniform(2, 4))  # Sleep before next search

    i += 1

# ✅ 9. CLOSE BROWSER AFTER SCRAPING  
driver.quit()
print("✅ Done scraping and saving results to Google Sheets.")


