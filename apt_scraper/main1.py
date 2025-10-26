from utils import *
from helper_class import *
from proxy_interface import *
import os
import sys
from dotenv import load_dotenv

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

        price_cond = '1500'
        home_cond = 'apartment'
        moving_date_days = '2024078'

        for index, data in enumerate(input_data):

            data_slug = data.replace(',', '').replace(' ', '-').lower()
            display_label_data = data_slug
            print('(zone) ', index, ' / ', len(input_data), ' : ', data, ' : ', data_slug)

            if data_slug not in processed_json_data:

                page_num = 1

                while 1:

                    current_url = f'https://www.apartments.com/apartments/{data_slug}/over-{price_cond}/{page_num}/?mid={moving_date_days}'

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

                    all_apartments = soup.find('div', id='placardContainer').ul.find_all('li', class_='mortar-wrapper')

                    print('Total Listings: ', page_num, ' : ', len(all_apartments))

                    for apt_index, apartment in enumerate(all_apartments):

                        #enable.debug
                        #if page_num < 13:
                        #    page_num = page_num + 1
                        #    continue

                        try:
                            apartment_name = apartment.find('div', class_='property-title')['title']
                        except:
                            try:
                                apartment_name = apartment.find('p', class_='property-title')['title']
                            except:
                                continue

                        apartment_url = apartment.find('article')['data-url']
                        apartment_id = apartment.find('article')['data-listingid']

                        print(index,'=>',display_label_data, ' (index) ', page_num, ' : (pages) ', apt_index, ' / ', len(all_apartments), ' : ', apartment_name)

                        if apartment_url not in processed_json_data:

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

                                property_name = soup.find('h1', id='propertyName').text.strip()
                                street_address = soup.find('div', id='propertyAddressRow').h2.span.text.strip()

                                if street_address.endswith(','):
                                    street_address = street_address[:-1]

                                city = soup.find('div', id='propertyAddressRow').h2.span.find_next_sibling('span').text.strip()
                                state = soup.find('div', id='propertyAddressRow').find('span', class_='stateZipContainer').find_all('span')[0].text.strip()
                                zip_code = soup.find('div', id='propertyAddressRow').find('span', class_='stateZipContainer').find_all('span')[1].text.strip()

                                print(property_name, ' : ', street_address, ' : ', city, ' : ', state, ' : ', zip_code)

                                try:
                                    all_buildings = soup.find('div', id='pricingView').find_all('div', class_='pricingGridItem multiFamily hasUnitGrid')
                                except:
                                    all_buildings = []

                                has_units = True

                                if not all_buildings:
                                    try:
                                        all_buildings = soup.find('div', id='pricingView').find_all('div', class_='pricingGridItem multiFamily')
                                    except:
                                        all_buildings = []
                                    has_units = False

                                complete_data = []

                                apartment_saved = []

                                for building in all_buildings:

                                    building_name = building.find('span', class_='modelName').text.strip()
                                    rent_range = building.find('span', class_='rentLabel').text.strip()
                                    bath = building.find('span', string=re.compile('bath')).text.strip().split()[0]

                                    rent_range = ' '.join(rent_range.split())

                                    try:
                                        bed = building.find('span', string=re.compile('bed')).text.strip().split()[0]
                                    except:
                                        bed = building.find('span', string=re.compile('Studio')).text.strip()

                                    print(building_name, ' : ', rent_range, ' : ', bed, ' : ', bath)

                                    if has_units:

                                        all_units = building.find('div', class_=re.compile('unitGridContainer')).find_all('li', class_=re.compile('unitContainer'))

                                        for unit in all_units:

                                            unit_num = unit['data-unit']
                                            # unit_price = unit['data-maxrent']
                                            unit_price = unit.find('span', {'data-monetaryunittype':'USD'}).text.strip().replace(',', '').replace('$', '')
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

                                    else:

                                        print('has no units------------------')

                                        try:
                                            unit_size = building.find('span', string=re.compile('sq ft')).text.strip().split('sq ft')[0].strip()
                                        except:
                                            unit_size = ''

                                        unit_available = building.find('span', class_='availabilityInfo').text.strip()
                                        unit_num = ''
                                        unit_price = rent_range

                                        unit_price = ' '.join(unit_price.split())

                                        if 'Not Available' not in unit_available:

                                            if '–' in unit_price:
                                                int_unit_price = unit_price.split('–')[1]
                                            else:
                                                int_unit_price = unit_price


                                            ################################################################################
                                            # kan-72::we will need to replace carriage return and make sure we are in-line
                                            ################################################################################
                                            if self.utils.has_carriage_return(int_unit_price):
                                                print('---------------has_no_units.carriage.return.remove')
                                                unit_price = self.utils.remove_carriage_display(unit_price)
                                                int_unit_price = self.utils.remove_all_chars(int_unit_price)
                                            ################################################################################

                                            if unit_price.lower() != 'call for rent':
                                                int_unit_price = int(int_unit_price.replace('$', '').replace(',', '').split('.')[0].split('/')[0])

                                            if unit_price.lower() == 'call for rent' or int_unit_price >= int(price_cond):

                                                complete_data.append([
                                                    data,
                                                    apartment_url,
                                                    property_name,
                                                    street_address,
                                                    city,
                                                    state,
                                                    zip_code,
                                                    building_name,
                                                    rent_range,
                                                    bed,
                                                    bath,
                                                    unit_num,
                                                    unit_price,
                                                    unit_size,
                                                    unit_available
                                                ])

                                        else:
                                            print('Unit Unavailable...')

                                    print()

                                if complete_data:
                                    self.writing_output_file(complete_data)

                            processed_json_data.append(apartment_url)
                            self.helper.write_json_file(processed_json_data, processed_json_file)

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

if __name__ == "__main__":

    handle = MAINCLASS()
    handle.start_scraping()

    print('\n\nALL DONE, PLEASE CLOSE THIS CONSOLE AND CHECK THE OUTPUT IN OUTPUT_DATA FOLDER\n\n')