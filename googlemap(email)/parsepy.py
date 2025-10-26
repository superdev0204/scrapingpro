import phonenumbers
from phonenumbers import geocoder
import requests
from geopy.geocoders import Nominatim
import re
from bs4 import BeautifulSoup


def extract_first_email_from_url(content):
    try:
        # Extract emails from text
        email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        emails = set(re.findall(email_regex, content))

        return emails

        # # Extract emails from href="mailto:"
        # for a_tag in soup.find_all("a", href=True):
        #     if a_tag["href"].startswith("mailto:"):
        #         email = a_tag["href"].replace("mailto:", "").split("?")[0]
        #         emails.add(email)

        # return list(emails)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    return None

def extract_phone_numbers_from_url(content):
    try:
        # Parse the HTML content of the webpage using BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # Extract text content and href attributes from the HTML
        text_content = content
        href_links = [a.get('href') for a in soup.find_all('a')]

        # Attempt to find phone numbers after specific words
        phone_number = None
        phone_words = ["Phone", "Call", "Call at", "Phone at", "phone at", "call at"]
        for word in phone_words:
            phone_number = find_phone_after_word(text_content, word)
            if phone_number:
                break

        # If no phone number is found after specific words, check href links for tel: links
        if not phone_number:
            for href in href_links:
                if href and href.startswith("tel:"):
                    phone_number = href[4:]  # Extract the phone number after "tel:"
                    break

        # If still no phone number is found, use the general pattern
        if not phone_number:
            phone_number = find_phone_with_pattern(text_content)

        if phone_number and validate_us_phone_number(phone_number):
            return format_phone_number(phone_number)
        return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


def find_phone_after_word(text, word):
    # Search for phone numbers after the specified word
    pattern = rf"{word}\s*:\s*(\d{3}[-.\s]?\d{3}[-.\s]?\d{4}|\(\d{3}\)\s*\d{3}[-.\s]?\d{4})"
    match = re.search(pattern, text, re.I)  # Case-insensitive search
    if match:
        return match.group(1)
    return None


def find_phone_with_pattern(text):
    phone_pattern = r"\(\d{3}\) \d{3}-\d{4}"
    phone_numbers = re.findall(phone_pattern, text)

    # If a phone number is found, return the first one
    if phone_numbers:
        return phone_numbers[0]  # phone_numbers[0] is a tuple, return the full match
    else:
        # Combined pattern: Matches various phone number formats including international with +1
        phone_pattern = (
            r'\b('
            r'(\+\d\s?)?'  # Optional international prefix +1 with optional space
            r'(\(\d{3}\)|\d{3})'  # Area code with or without parentheses
            r'[\s.-]?'  # Optional separator (space, dot, or dash)
            r'\d{3}'  # Three digits
            r'[\s.-]?'  # Optional separator (space, dot, or dash)
            r'\d{4}'  # Four digits
            r')\b'
        )
        phone_numbers = re.findall(phone_pattern, text)

        if phone_numbers:
            return phone_numbers[0][0]  # phone_numbers[0] is a tuple, return the full match

    # If no phone number is found, return None
    return None

def find_phone_by_lib(text):
    phone_numbers = []
    for match in phonenumbers.PhoneNumberMatcher(text, "US"):
        phone_numbers.append(phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164))

    if phone_numbers:
        most_common_phone = max(set(phone_numbers), key=phone_numbers.count)
        return most_common_phone

    return None

def find_phone_region(number):
    us_number = phonenumbers.parse(number, "US")
    geo = geocoder.description_for_number(us_number, "us")

    if geo:
        return str(geo)
    else:
        return None

def validate_us_phone_number(phone_number):
    # Check if the phone number matches the common US format
    pattern = r'^(?:\(\d{3}\)\s?|\d{3}[-.\s]?)\d{3}[-.\s]?\d{4}$'
    return bool(re.match(pattern, phone_number))


def format_phone_number(phone_number):
    # Convert phone number to the standard format (XXX) XXX-XXXX
    digits = re.sub(r'\D', '', phone_number)
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"


def extract_last_zip_code(text):
    # US ZIP codes can be 5 digits or 5-4 format, e.g., 12345 or 12345-6789
    zip_regex = r"\b\d{5}(?:-\d{4})?\b"
    matches = re.findall(zip_regex, text)

    if matches:
        # Return the last ZIP code found
        return matches[-1]
    else:
        return None


def get_state_from_zipcode(zipcode):
    # Initialize the Nominatim geocoder with a user agent
    geolocator = Nominatim(user_agent="my_geocoder")

    try:
        # Geocode the ZIP code
        location = geolocator.geocode(zipcode, country_codes="US")

        if location:
            # Extract the address components
            address_components = location.raw.get("address", {})

            # Extract the state
            state = address_components.get("state", "")

            if location:
                return location
    except Exception as e:
        return f"An error occurred: {e}"