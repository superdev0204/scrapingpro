Instructions for Using the SendGrid Contact Upload Script

Overview
This Python script is designed to create a new contact list in SendGrid and upload contacts from a CSV file into that list. The script utilizes the SendGrid API to manage contacts and lists.

Prerequisites
Python 3.x installed on your machine.
The requests library installed. You can install it using pip:

pip install requests

A valid SendGrid API key. Replace the placeholder in the script with your actual API key.
CSV File Format
The CSV file should contain a header row with at least one column named "Email". Additional columns can be added for custom fields. An example of the CSV format is shown below:

Email, FirstName, LastName
john.doe@example.com, John, Doe
jane.smith@example.com, Jane, Smith

Execution:

The script first creates a new list in SendGrid.
It then reads the contacts from the specified CSV file.
Finally, it uploads the contacts to the newly created list.

How to Run the Script
Update the SENDGRID_API_KEY with your actual SendGrid API key.
Update the file_path variable with the path to your CSV file.
Update the new_list_name variable with your desired list name.

method 1: 
please run the start.bat file.

method2: 
Open a terminal or command prompt.
Navigate to the directory where the script is saved.
Run the script using the command:

py upload_contacts.py

Troubleshooting
Ensure that the CSV file is correctly formatted.
Check your API key and permissions in SendGrid if you encounter authentication errors.
Review the response messages printed in the terminal for any errors during the execution.