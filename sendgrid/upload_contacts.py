import csv
import requests
import json

# Your SendGrid API key
SENDGRID_API_KEY = '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'

# Example usage
file_path = 'Hospital Sendgrid Upload Format.csv'  # Make sure to use the correct path
new_list_name = 'test_contacts'  # new list name


# Open and read the CSV file
def create_list_to_sendgrid(list_name):
    # Step 1: Create a New List
    create_list_url = "https://api.sendgrid.com/v3/marketing/lists"
    create_list_data = {
        "name": list_name
    }
    create_list_headers = {
        'Authorization': f'Bearer {SENDGRID_API_KEY}',
        'Content-Type': 'application/json'
    }

    # Send request to create a new list
    create_list_response = requests.post(create_list_url, headers=create_list_headers, json=create_list_data)

    if create_list_response.status_code == 201:
        print("New contact list created successfully!")
        return create_list_response.json()["id"]
    else:
        print(f"Failed to create list: {create_list_response.status_code}, {create_list_response.text}")
        exit()


# Function to get all contacts
def find_contact_by_email(email):
    url = "https://api.sendgrid.com/v3/marketing/contacts/search/emails"
    headers = {
        'Authorization': f'Bearer {SENDGRID_API_KEY}',
        'Content-Type': 'application/json'
    }

    data = {
        "emails": [email],
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        contacts_data = response.json()
        contacts = contacts_data.get('result', [])
        return contacts
    else:
        return None


# Open and read the CSV file
def read_csv(file_path):
    contacts = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)  # Use DictReader to read each row as a dictionary
        # Get the first row which contains the column names
        columns = csv_reader.fieldnames  # This gives you the column headers

        for row in csv_reader:
            contact = {}
            email = row['Email'].lower().strip()
            if email == '':
                continue
            find_contact = find_contact_by_email(email)
            
            if find_contact:
                contact = find_contact[email]["contact"]
            else:
                contact = {
                    "custom_fields": {}  # Initialize custom fields as empty dict
                }

            # Iterate through all columns and add them to 'custom_fields' in contact
            for column, value in row.items():
                if value:
                    if column == "Email" or column == "email":
                        contact["email"] = value
                    elif column == "phone_number":
                        contact["phone_number"] = value
                    elif column == "address_line_1":
                        contact["address_line_1"] = value
                    elif column == "postal_code":
                        contact["postal_code"] = value
                    elif column == "City" or column == "city":
                        contact["city"] = value
                    elif column == "state_province_region":
                        contact["state_province_region"] = value
                    else:
                        if column == "HospPatientCardQty" or column == "TotalHospRequested":
                            contact["custom_fields"][column] = int(value)
                        else:
                            contact["custom_fields"][column] = value

            contacts.append(contact)

    return contacts


# Function to upload contacts to SendGrid
def upload_contacts_to_sendgrid(list_id, contacts):
    add_contacts_url = f"https://api.sendgrid.com/v3/marketing/contacts"
    add_contacts_data = {
        "list_ids": [list_id],
        "contacts": contacts
    }
    
    headers = {
        'Authorization': f'Bearer {SENDGRID_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Send the contacts to SendGrid
    response = requests.put(add_contacts_url, headers=headers, json=add_contacts_data)
    
    if response.status_code == 202:
        print(f"Successfully uploaded {len(contacts)} contacts.")
    else:
        print(f"Failed to upload contacts: {response.status_code}, {response.text}")


list_id = create_list_to_sendgrid(new_list_name)  # Create new list
contacts = read_csv(file_path)  # Read the contacts from the CSV file
upload_contacts_to_sendgrid(list_id, contacts)  # Upload contacts to SendGrid