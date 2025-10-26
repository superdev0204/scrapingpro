from utils import *
from helper_class import *
from proxy_interface import *
import os
import sys
from dotenv import load_dotenv

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timezone

load_dotenv()

class MAINCLASS():

    def __init__(self):
        self.helper = Helper()
        self.utils = Utils()

        self.data_folder = self.helper.checking_folder_existence('./output_data/')
        self.log_folder = self.helper.checking_folder_existence(self.data_folder + 'log/')
        self.output_file = self.data_folder + 'complete_data_apartments.csv'

        api_key = os.getenv('API_KEY')
        self.proxy_interface = PROXYCLASSNEW(api_key)

        self.headers = []
        self.headers_length = 0

        self.from_email = 'admin@uniquefleetautoclub.com'
        self.from_email_password = 'Uniquechobits1@1377'
        self.to_emails = ["aburkhead@findlayinternational.com", "superdev0205@outlook.com"]

    def send_email(self, subject, body):
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        # msg['To'] = self.to_email
        msg['Subject'] = subject

        # Attach the body with the msg instance
        msg.attach(MIMEText(body, 'plain'))

        # Get the current date
        current_date = datetime.now().date()

        print("Current date:", current_date)

        new_file_name = self.data_folder + f'complete_data_apartments({current_date.strftime("%Y%m%d")}).csv'
        
        if os.path.exists(new_file_name):
            print(f"The file {new_file_name} already exists. Choose a different name.")
        else:
            os.rename(self.output_file, new_file_name)
            print(f"File renamed from {self.output_file} to {new_file_name}")
            self.output_file = new_file_name

        # Open the CSV file in binary mode
        with open(self.output_file, 'rb') as attachment:
            # Create a MIMEBase object
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            # Encode the payload using Base64
            encoders.encode_base64(part)
            # Add header as key/value pair to attachment part
            part.add_header('Content-Disposition', f'attachment; filename=complete_data_apartments({current_date.strftime("%Y%m%d")}).csv')
            # Attach the attachment to the MIMEMultipart object
            msg.attach(part)

        # Create SMTP session
        with smtplib.SMTP('smtp.ionos.com', 587) as server:
            server.starttls()  # Enable security
            server.login(self.from_email, self.from_email_password)  # Log in to your email account
            # Send email to each recipient
            for to_email in self.to_emails:
                msg['To'] = to_email
                server.send_message(msg)  # Send the email
                del msg['To']  # Remove the To field for the next iteration

        print("Email sent successfully!")


    def writing_output_file(self, sub_list):

        if self.helper.is_file_exist(self.output_file):
            csv_data = self.helper.reading_csv(self.output_file)
        else:
            csv_data = [self.helper.read_json_file('./headers.json')]

        csv_data.extend(sub_list)
        self.helper.writing_csv(csv_data,self.output_file)

        print("Writing Output File Done...")

    def start_scraping(self):

        processed_json_file = f'{self.log_folder}processed.json'
        processed_json_data = self.helper.json_exist_data(processed_json_file)

        input_data = self.helper.read_txt_file('./input_data.txt')

        price_cond = '2500'
        home_cond = 'apartment'
        moving_date_days = '20250101'#30

        for index, data in enumerate(input_data):

            data_slug = data.replace(',', '').replace(' ', '-').lower()
            display_label_data = data_slug
            print('(zone) ', index, ' / ', len(input_data), ' : ', data, ' : ', data_slug)

            if data_slug not in processed_json_data:

                page_num = 1

                while 1:

                    current_url = f'https://www.apartments.com/{data_slug}/over-{price_cond}/{page_num}/?mid={moving_date_days}'

                    soup = self.proxy_interface.make_soup_url(current_url)

                    # check if soup contains = Unauthorized request
                    if "Unauthorized" in str(soup):
                        print (soup)
                        sys.exit(0)

                    if "https://www.scraperapi.com/support/" in str(soup):
                        print (soup)
                        sys.exit(0)

                    if "exhausted the API Credits" in str(soup):
                        print (soup)
                        sys.exit(0)


                    self.helper.write_random_file(soup, 'file.html')

                    try:
                        all_apartments = soup.find('div', id='placardContainer').ul.find_all('li', class_='mortar-wrapper')
                    except:
                        break

                    print('Total Listings: ', page_num, ' : ', len(all_apartments))

                    for apt_index, apartment in enumerate(all_apartments):

                        try:
                            # Try to find the property title in both <p> and <div> elements
                            apartment_name_tag = apartment.find('p', class_='property-title') or apartment.find('div', class_='property-title')

                            if apartment_name_tag:
                                # Get the title from the 'title' attribute or fallback to inner text
                                apartment_name = apartment_name_tag.get('title', '').strip() or apartment_name_tag.find('span', class_='js-placardTitle').text.strip()
                                print(f"Scraped apartment name: {apartment_name}")
                            else:
                                apartment_name = "No Title"
                                print("No property title found, setting as 'No Title'")
    
                            # Scraping apartment URL as an example of other data fields
                            apartment_url = apartment.find('article')['data-url']                            
                            
                            print(f"Scraped apartment URL: {apartment_url}")

                        except Exception as e:
                            print(f"Error fetching apartment data: {e}")
                            apartment_name = "No Title"
                        
                        try:
                            apartment_url = apartment.find('article')['data-url']
                            apartment_id = apartment.find('article')['data-listingid']
                        except:
                            continue

                        print(index,'=>',display_label_data, ' (index) ', page_num, ' : (pages) ', apt_index, ' / ', len(all_apartments), ' : ', apartment_name)

                        if apartment_url not in processed_json_data:
                            repeat = 0
                            while True:
                                try:
                                    soup = self.proxy_interface.make_soup_url(apartment_url)
                                    
                                    self.helper.write_random_file(soup, 'file.html')

                                    json_data = soup.find('script', type='application/ld+json').string.strip()
                                    json_data = json.loads(json_data)

                                    self.helper.write_json_file(json_data, 'json_data.json')

                                    try:
                                        description = json_data['about']['description']
                                    except:
                                        description = ''

                                    if 'Apartments For Rent' not in soup.title.text.strip():

                                        try:
                                            property_name = soup.find('h1', id='propertyName').text.strip()
                                        except:
                                            try:
                                                property_name = soup.find('span', id='propertyName').text.strip()
                                            except:
                                                break
                                            
                                        try:
                                            street_address = soup.find('div', class_='delivery-address').h1.text.strip()
                                            city = soup.find('div', id='propertyAddressRow').h2.span.text.strip()
                                        except:
                                            street_address = soup.find('span', class_='delivery-address').span.text.strip()
                                            city = soup.find('div', id='propertyAddressRow').h2.span.find_next_sibling('span').text.strip()

                                        if street_address.endswith(','):
                                            street_address = street_address[:-1]

                                        state = soup.find('div', id='propertyAddressRow').find('span', class_='stateZipContainer').find_all('span')[0].text.strip()
                                        zip_code = soup.find('div', id='propertyAddressRow').find('span', class_='stateZipContainer').find_all('span')[1].text.strip()

                                        print(property_name, ' : ', street_address, ' : ', city, ' : ', state, ' : ', zip_code)

                                        built_in = 'N/A'
                                        # Find all feesPoliciesCard sections
                                        sections = soup.find_all('div', class_='mortar-wrapper feesPoliciesCard twoCols with-bullets-card')
                                        # Look for the section with "Property Information"
                                        for section in sections:
                                            header = section.find('h4', class_='header-column')
                                            if header and 'Property Information' in header.get_text():
                                                # Extract data from the “Property Information” section
                                                property_info_items = section.find_all('li', class_='with-bullets')
                                                property_data = [item.get_text(strip=True) for item in property_info_items]
                                                for item in property_data:
                                                    if re.search('Built in', item):
                                                        built_in = item.replace('Built in', '').strip()

                                        try:
                                            all_buildings = soup.find('div', id='pricingView').find_all('div', class_=['pricingGridItem', 'multiFamily', 'hasUnitGrid'])
                                        except:
                                            all_buildings = []

                                        has_units = True

                                        if not all_buildings:
                                            try:
                                                all_buildings = soup.find('div', id='pricingView').find_all('div', class_=['pricingGridItem', 'multiFamily'])
                                            except:
                                                all_buildings = []
                                            has_units = False

                                        complete_data = []

                                        apartment_saved = []
                                        # Scraping detailed apartment data if available
                                        for building in all_buildings:
                                            
                                            building_name = building.find('span', class_='modelName').text.strip()
                                            rent_range = building.find('span', class_='rentLabel').text.strip()

                                            try:
                                                bath = building.find('span', class_='detailsLabel').find('span', string=re.compile('Bath')).text.strip().split()[0]
                                            except:
                                                bath = building.find('span', class_='detailsLabel').find('span', string=re.compile('bath')).text.strip().split()[0]                          

                                            try:
                                                bed = building.find('span', class_='detailsLabel').find('span', string=re.compile('Bed')).text.strip().split()[0]
                                            except:
                                                try:
                                                    bed = building.find('span', class_='detailsLabel').find('span', string=re.compile('bed')).text.strip().split()[0]
                                                except:
                                                    try:
                                                        bed = building.find('span', class_='detailsLabel').find('span', string=re.compile('Studio')).text.strip()
                                                    except:
                                                        bed = building.find('span', class_='detailsLabel').find('span', string=re.compile('studio')).text.strip()

                                            print(building_name, ' : ', rent_range, ' : ', bed, ' : ', bath)

                                            if has_units:

                                                try:
                                                    all_units = building.find('div', class_=re.compile('unitGridContainer')).find_all('li', class_=re.compile('unitContainer'))
                                                except:
                                                    continue

                                                for unit in all_units:

                                                    unit_num = unit['data-unit']
                                                    # unit_price = unit.find('span', {'data-monetaryunittype':'USD'}).text.strip().replace(',', '').replace('$', '')
                                                    unit_price = unit.find('span', string=re.compile('price')).find_next_sibling('span').text.strip().replace(',', '').replace('$', '')
                                                    unit_size = unit.find('span', string=re.compile('square feet')).find_next_sibling('span').text.strip()
                                                    unit_available = unit.find('span', class_='dateAvailable').span.nextSibling.strip()

                                                    if '–' in unit_price:
                                                        int_unit_price = unit_price.split('–')[1]
                                                    else:
                                                        int_unit_price = unit_price

                                                    ################################################################################
                                                    # kan-72::we will need to replace carriage return and make sure we are in-line
                                                    ################################################################################
                                                    if self.utils.has_carriage_return(int_unit_price):
                                                        print('---------------has_units.carriage.return.remove')
                                                        unit_price = self.utils.remove_carriage_display(unit_price)
                                                        int_unit_price = self.utils.remove_all_chars(int_unit_price)
                                                    ################################################################################

                                                    print(int_unit_price, ' (lol): (har)', unit_price)

                                                    if unit_price.lower() != 'call for rent':
                                                        int_unit_price = int(int_unit_price.replace('$', '').replace(',', '').split('.')[0])

                                                    if 'call for rent' not in unit_price.lower() and int_unit_price < int(price_cond):
                                                        continue

                                                    print(unit_num, ' : ', unit_price, ' : ', unit_size, ' : ', unit_available)

                                                    unique_apartment = f'{building_name}_{unit_num}_{unit_price}'

                                                    if 'Not Available' not in unit_available and unique_apartment not in apartment_saved:

                                                        complete_data.append([
                                                            data,
                                                            apartment_url,
                                                            property_name,
                                                            street_address,
                                                            city,
                                                            state,
                                                            zip_code,
                                                            built_in,
                                                            building_name,
                                                            rent_range,
                                                            bed,
                                                            bath,
                                                            unit_num,
                                                            unit_price,
                                                            unit_size,
                                                            unit_available
                                                        ])

                                                        apartment_saved.append(unique_apartment)

                                        # If no detailed unit data, scrape price, size, and availability from other elements
                                        if not all_buildings:
                                            try:
                                                # Extract the unit price
                                                unit_price_label = soup.find('div', class_='priceBedRangeInfoContainer').find('p', string=re.compile('Monthly Rent'))
                                                if unit_price_label:
                                                    unit_price = unit_price_label.find_next('p', class_='rentInfoDetail').text.strip()

                                                    if '–' in unit_price:
                                                        int_unit_price = unit_price.split('–')[1]
                                                    else:
                                                        int_unit_price = unit_price

                                                    ################################################################################
                                                    # kan-72::we will need to replace carriage return and make sure we are in-line
                                                    ################################################################################
                                                    if self.utils.has_carriage_return(int_unit_price):
                                                        print('---------------has_units.carriage.return.remove')
                                                        unit_price = self.utils.remove_carriage_display(unit_price)
                                                        int_unit_price = self.utils.remove_all_chars(int_unit_price)
                                                    ################################################################################

                                                    print(int_unit_price, ' (lol): (har)', unit_price)

                                                    if unit_price.lower() != 'call for rent':
                                                        int_unit_price = int(int_unit_price.replace('$', '').replace(',', '').split('.')[0])

                                                    if 'call for rent' not in unit_price.lower() and int_unit_price < int(price_cond):
                                                        continue
                                                else:
                                                    unit_price = "N/A"
                                            except Exception as e:
                                                unit_price = "N/A"
                                                print(f"Failed to extract unit_price: {e}")
                                            
                                            try:
                                                # Extract the unit size
                                                unit_size_label = soup.find('div', class_='priceBedRangeInfoContainer').find('p', string=re.compile('Square Feet'))
                                                if unit_size_label:
                                                    unit_size = unit_size_label.find_next('p', class_='rentInfoDetail').text.strip()
                                                else:
                                                    unit_size = "N/A"
                                            except Exception as e:
                                                unit_size = "N/A"
                                                print(f"Failed to extract unit_size: {e}")
                                            
                                            try:
                                                unit_available = soup.find('span', class_='availabilityInfo').text.strip()
                                            except Exception as e:
                                                unit_available = "N/A"
                                                print(f"Failed to extract unit_available: {e}")
                                            
                                            complete_data.append([
                                                data,
                                                apartment_url,
                                                property_name,
                                                street_address,
                                                city,
                                                state,
                                                zip_code,
                                                "N/A",  # No built in
                                                "N/A",  # No building name
                                                unit_price,
                                                "N/A",  # No bed info
                                                "N/A",  # No bath info
                                                "N/A",  # No unit number
                                                unit_price,
                                                unit_size,
                                                unit_available
                                            ])
                                            print(f"Scraped with fallback: {property_name} : {unit_price} : {unit_size} : {unit_available}")

                                        if complete_data:
                                            self.writing_output_file(complete_data)

                                    processed_json_data.append(apartment_url)
                                    self.helper.write_json_file(processed_json_data, processed_json_file)

                                    break
                                
                                except AttributeError as e:
                                    if repeat > 2:
                                        break
                                    print(f"AttributeError occurred: {e}. Retrying...")
                                    # Optionally, you can add a delay before retrying
                                    time.sleep(2)  # Wait for 2 seconds before retrying
                                except Exception as e:
                                    if repeat > 2:
                                        break
                                    print(f"An unexpected error occurred: {e}. Retrying...")
                                    time.sleep(2)  # Wait for 2 seconds before retrying

                                repeat = repeat + 1

                        else:
                            print('apartment_url already processed...')

                        print('-'*50)
                        print()

                    if len(all_apartments) < 40:
                        break

                    page_num += 1

                processed_json_data.append(data_slug)
                self.helper.write_json_file(processed_json_data, processed_json_file)

            else:
                print('Already Processed...')

            print('-'*50)
            print()

        self.send_email(
            subject="Apt CSV File Attached",
            body="Please find the attached CSV file.",
        )

if __name__ == "__main__":

    handle = MAINCLASS()
    handle.start_scraping()

    print('\n\nALL DONE, PLEASE CLOSE THIS CONSOLE AND CHECK THE OUTPUT IN OUTPUT_DATA FOLDER\n\n')
