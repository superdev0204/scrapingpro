import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone, date

# Create SMTP session
try:
    s = smtplib.SMTP('smtp.ionos.com', 587)  # Corrected SMTP server address
    s.starttls()  # Start TLS for security

    # Authentication
    s.login("admin@uniquefleetautoclub.com", "Uniquechobits1@1377")  # Ensure credentials are correct

    # Create the MIME message
    msg = MIMEMultipart()
    msg['From'] = "admin@uniquefleetautoclub.com"
    msg['To'] = "superdev0205@outlook.com"
    msg['Subject'] = "Subject of the Email"

    # Body of the email
    body = "This is the message you need to send"
    msg.attach(MIMEText(body, 'plain'))

    # Sending the mail
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    print("Email sent successfully!")
    
    # Get the current date and time in UTC
    current_utc_datetime = datetime.now(timezone.utc)
    print("Current UTC date and time:", current_utc_datetime)

except Exception as e:
    print(f"Failed to send email: {e}")

finally:
    # Terminating the session
    s.quit()
