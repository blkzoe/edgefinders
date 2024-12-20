import imapclient
import email
from email.header import decode_header
import time
from bs4 import BeautifulSoup  # Import to handle HTML content
import re  # Import for regular expression handling
import requests  # Import for sending requests to Discord and Telegram
from keep_alive import keep_alive

# Your Yahoo email credentials
EMAIL = "udokpanzoe@yahoo.com"
PASSWORD = "lhlkkjmexlhidskp"

# Your Discord webhook URL
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1305517670237605898/apm5Eh66-xUV4Cf01NnMp9dKOnzDGpZlRJpx54sYcZ4pQb-ruoxepZkQjKxYkrRoAICJ"

# Your Telegram Bot Token and Chat ID
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"

# Define the keywords you want to search between
KEYWORD1 = "[N.R.S ALGO]"  # "keyword1"
KEYWORD2 = "[N.R.S ALGO]"  # "keyword2"

# Function to send text to Discord
def send_to_discord(message):
    data = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print("Message sent to Discord successfully.")
        else:
            print(f"Failed to send message to Discord. Status code: {response.status_code}")
    except Exception as e:
        print("Error sending message to Discord:", str(e))

# Function to send text to Telegram
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("Message sent to Telegram successfully.")
        else:
            print(f"Failed to send message to Telegram. Status code: {response.status_code}")
    except Exception as e:
        print("Error sending message to Telegram:", str(e))

# Function to fetch and print the most recent email
def fetch_and_print_latest_email():
    # Connect to Yahoo's IMAP server
    server = imapclient.IMAPClient('imap.mail.yahoo.com', ssl=True)
    try:
        # Login to your Yahoo Mail account
        server.login(EMAIL, PASSWORD)

        # Select the inbox folder
        server.select_folder('INBOX', readonly=True)

        # Search for all emails and sort them by most recent
        messages = server.search(['ALL'])
        if not messages:
            print("No messages found.")
            return None

        # Get the most recent email ID
        latest_msg_id = messages[-1]

        # Check if we have already seen this email
        if latest_msg_id == fetch_and_print_latest_email.last_seen_id:
            return None  # Don't print the same email twice

        fetch_and_print_latest_email.last_seen_id = latest_msg_id

        # Fetch the email
        raw_message = server.fetch([latest_msg_id], ['RFC822'])[latest_msg_id][b'RFC822']
        email_message = email.message_from_bytes(raw_message)

        # Get email details
        subject, encoding = decode_header(email_message['Subject'])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or 'utf-8')
        from_ = email_message.get('From')

        print(f"Subject: {subject}")
        print(f"From: {from_}")

        # Extract the email body
        body = None
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if content_type == "text/plain" and "attachment" not in content_disposition:
                    # Get the plain text email body
                    body = part.get_payload(decode=True).decode()
                    break
                elif content_type == "text/html" and not body:
                    # Fallback to extracting text from HTML if plain text is not available
                    html_content = part.get_payload(decode=True).decode()
                    # Use BeautifulSoup to extract plain text from HTML
                    soup = BeautifulSoup(html_content, "html.parser")
                    body = soup.get_text()
        else:
            # If the email is not multipart, just get the payload
            content_type = email_message.get_content_type()
            if content_type == "text/plain":
                body = email_message.get_payload(decode=True).decode()
            elif content_type == "text/html":
                # Use BeautifulSoup to extract plain text from HTML
                html_content = email_message.get_payload(decode=True).decode()
                soup = BeautifulSoup(html_content, "html.parser")
                body = soup.get_text()

        if body:
            # Search for text between the two keywords, including the keywords
            pattern = f"({re.escape(KEYWORD1)}.*?{re.escape(KEYWORD2)})"
            match = re.search(pattern, body, re.DOTALL)
            if match:
                extracted_text = match.group(1)
                print("Extracted Text:", extracted_text)
                # Send the extracted text to Discord and Telegram
                send_to_discord(extracted_text)
                # send_to_telegram(extracted_text)
            else:
                print("No matching text found between the specified keywords.")
        else:
            print("No plain text body found.")

    except Exception as e:
        print("Error:", str(e))

    finally:
        # Logout and close the connection
        server.logout()

# Initialize the last seen email ID
fetch_and_print_latest_email.last_seen_id = None

# Run the script every minute
keep_alive()
while True:
    keep_alive()
    fetch_and_print_latest_email()
    time.sleep(60)
