# email_system.py
import smtplib
import time
import threading
import re
import json
import os
from dotenv import load_dotenv
load_dotenv()
from difflib import get_close_matches
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==========================================================
# ---------- CONFIGURATION ----------
# ==========================================================
EMAIL_CONTACTS_FILE = "email_contacts.json"
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")
SENDER_EMAIL = GMAIL_USER
SENDER_PASSWORD = GMAIL_PASS

# ==========================================================
# ---------- ENHANCED JSON EMAIL CONTACTS SYSTEM ----------
# ==========================================================

def load_email_contacts():
    """JSON file se email contacts load kare"""
    try:
        if os.path.exists(EMAIL_CONTACTS_FILE):
            with open(EMAIL_CONTACTS_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
            save_email_contacts(default_contacts)
            return default_contacts
    except Exception as e:
        print(f"Error loading contacts: {e}")
        return {}

def save_email_contacts(contacts):
    """Email contacts ko JSON file mein save kare"""
    try:
        with open(EMAIL_CONTACTS_FILE, 'w', encoding='utf-8') as file:
            json.dump(contacts, file, indent=4)
        return True
    except Exception as e:
        print(f"Error saving contacts: {e}")
        return False

def add_email_contact(name, email):
    """Naya contact JSON file mein add kare"""
    try:
        contacts = load_email_contacts()
        contacts[name.lower()] = email
        return save_email_contacts(contacts)
    except Exception as e:
        print(f"Error adding contact: {e}")
        return False

def get_email_by_name(name):
    """Name se email address return kare"""
    contacts = load_email_contacts()
    return contacts.get(name.lower())

def list_all_contacts():
    """Tamam contacts ki list return kare"""
    return load_email_contacts()

def get_contacts_list_text():
    """Contacts ki list ko text format mein return kare"""
    contacts = list_all_contacts()
    if contacts:
        contact_list = []
        for name, email in contacts.items():
            contact_list.append(f"{name}: {email}")
        return ", ".join(contact_list)
    else:
        return "No contacts saved yet."

# ==========================================================
# ---------- ENHANCED SMART NAME MATCHING SYSTEM ----------
# ==========================================================

def find_best_name_match(user_input):
    """User input ke liye best name match find kare"""
    contacts = load_email_contacts()
    contact_names = list(contacts.keys())
    user_input = user_input.lower().strip()

    print(f"Searching for: '{user_input}' in contacts: {contact_names}")

    # 1. Direct match
    if user_input in contacts:
        print(f"Direct match found: {user_input}")
        return contacts[user_input]

    # 2. Fuzzy matching
    fuzzy_matches = get_close_matches(user_input, contact_names, n=3, cutoff=0.5)
    if fuzzy_matches:
        print(f"Fuzzy match found: {fuzzy_matches[0]} for {user_input}")
        return contacts[fuzzy_matches[0]]

    # 3. Partial word matching
    for contact_name in contact_names:
        user_words = user_input.split()
        contact_words = contact_name.split()

        for user_word in user_words:
            for contact_word in contact_words:
                if user_word in contact_word or contact_word in user_word:
                    if len(user_word) > 2:
                        print(f"Partial match: '{user_word}' in '{contact_name}'")
                        return contacts[contact_name]

    # 4. Sound-based corrections
    common_mispronunciations = {
        "sad": "saad", "sard": "saad", "sardar": "saad",
        "raja": "raza", "rajaa": "raza", "razza": "raza",
        "daniyal": "daniyal", "danyal": "daniyal", "danial": "daniyal",
        "bhai": "bhai", "brother": "bhai", "bahi": "bhai",
        "awab": "awab", "awabb": "awab", "aab": "awab",
        "ad": "ad", "aad": "ad", "sial": "sial", "siaal": "sial"
    }

    corrected_input = user_input
    for wrong, correct in common_mispronunciations.items():
        corrected_input = corrected_input.replace(wrong, correct)

    if corrected_input != user_input:
        print(f"Corrected '{user_input}' to '{corrected_input}'")
        if corrected_input in contacts:
            print(f"Corrected match found: {corrected_input}")
            return contacts[corrected_input]

    # 5. First-name matching
    for contact_name in contact_names:
        contact_first = contact_name.split()[0]
        user_first = user_input.split()[0]

        if contact_first == user_first:
            print(f"First name match: '{user_first}' in '{contact_name}'")
            return contacts[contact_name]

    print(f"No match found for: {user_input}")
    return None

# ==========================================================
# ---------- ENHANCED SMART RECIPIENT PARSING ----------
# ==========================================================

def parse_recipients(input_text):
    """Voice input se recipients parse kare"""
    recipients = []

    if not input_text:
        return recipients

    print(f"Raw input received: '{input_text}'")

    clean_input = re.sub(r'^(send|email|to|for|and|)\s+', '', input_text.lower())
    parts = re.split(r'\b(?:and|,)\b|\s+', clean_input)
    parts = [p.strip() for p in parts if p.strip() and len(p) > 1]

    print(f"Cleaned parts: {parts}")

    for part in parts:
        print(f"Processing: '{part}'")

        # Email checking
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_matches = re.findall(email_pattern, part)

        if email_matches:
            recipients.extend(email_matches)
            print(f"Email found: {email_matches}")
        else:
            email = find_best_name_match(part)
            if email:
                recipients.append(email)
                print(f"Name matched: '{part}' -> {email}")
            else:
                print(f"No match for: '{part}'")

    unique_recipients = list(set(recipients))
    print(f"Final recipients: {unique_recipients}")

    return unique_recipients

# ==========================================================
# ---------- ENHANCED EMAIL SENDING SYSTEM ----------
# ==========================================================

from email.mime.base import MIMEBase
from email import encoders

def send_email(subject, body, recipients, delay_seconds=0, attachments=None):
    """Background email sending with optional attachments"""

    def task():
        if delay_seconds > 0:
            print(f"Waiting {delay_seconds} seconds before sending email...")
            time.sleep(delay_seconds)

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)

            for receiver_email in recipients:
                message = MIMEMultipart()
                message["From"] = SENDER_EMAIL
                message["To"] = receiver_email
                message["Subject"] = subject
                message.attach(MIMEText(body, "plain"))

                # Handle attachments
                if attachments:
                    for file_path in attachments:
                        try:
                            if os.path.exists(file_path):
                                with open(file_path, "rb") as attachment:
                                    part = MIMEBase("application", "octet-stream")
                                    part.set_payload(attachment.read())
                                
                                encoders.encode_base64(part)
                                part.add_header(
                                    "Content-Disposition",
                                    f"attachment; filename= {os.path.basename(file_path)}",
                                )
                                message.attach(part)
                                print(f"Attached: {file_path}")
                            else:
                                print(f"Attachment not found: {file_path}")
                        except Exception as e:
                            print(f"Error attaching file {file_path}: {e}")

                server.sendmail(SENDER_EMAIL, receiver_email, message.as_string())
                print(f"Email sent to: {receiver_email}")

            server.quit()
            return True, "Email has been sent successfully."

        except Exception as e:
            print("Error:", e)
            return False, f"Could not send the email. Error: {str(e)}"

    thread = threading.Thread(target=task)
    thread.daemon = True
    thread.start()

    return True, "Email sending started in background."

# ==========================================================
# ---------- ENHANCED TIME PARSING ----------
# ==========================================================

def parse_delay_time(delay_input):
    """Time formats ko seconds mein convert kare"""
    if not delay_input:
        return 10

    delay_input = delay_input.lower().replace(" ", "")
    print(f"Parsing time input: '{delay_input}'")

    try:
        if ":" in delay_input:
            try:
                minutes, sec = map(int, delay_input.split(":"))
                return minutes * 60 + sec
            except:
                pass

        numbers = re.findall(r'\d+', delay_input)
        if numbers:
            return int(numbers[0])

        time_units = {
            'second': 1, 'sec': 1,
            'minute': 60, 'min': 60,
            'hour': 3600, 'hr': 3600
        }

        for unit, mul in time_units.items():
            if unit in delay_input:
                numbers = re.findall(r'\d+', delay_input)
                if numbers:
                    return int(numbers[0]) * mul

    except Exception as e:
        print(f"Time parsing error: {e}")

    return 10

# ==========================================================
# ---------- SMART CONTACT SUGGESTIONS ----------
# ==========================================================

def get_smart_suggestions(user_input=""):
    contacts = list_all_contacts()
    suggestions = []

    if user_input:
        user_input = user_input.lower()
        for name in contacts:
            if user_input in name:
                suggestions.append(name)
            elif any(word in name for word in user_input.split()):
                suggestions.append(name)

    if not suggestions:
        suggestions.extend(contacts.keys())
        for name in contacts.keys():
            if "saad" in name:
                suggestions.extend(["saad", "sad raza", "saad raza"])
            if "daniyal" in name:
                suggestions.extend(["daniyal", "daniyal bhai"])
            if "awab" in name:
                suggestions.append("awab")
            if "ad" in name:
                suggestions.append("ad sial")

    return list(set(suggestions))[:5]

def get_contact_suggestions_text():
    suggestions = get_smart_suggestions()
    if suggestions:
        return "You can say: " + ", ".join(suggestions)
    return "Please say a contact name clearly."

# ==========================================================
# ---------- VALIDATION ----------
# ==========================================================

def validate_email_input(input_text):
    if not input_text:
        return False, "I didn't hear anything. Please try again."

    if input_text.isdigit():
        return False, "That sounds like a number. Please say a contact name."

    if len(input_text) < 2:
        return False, "That's too short. Please say a full name."

    return True, "Valid input"

# ==========================================================
# ---------- TESTING ----------
# ==========================================================

def test_name_matching():
    test_cases = [
        "saad raza",
        "sad raza",
        "sard raza",
        "saad raja",
        "daniyal bhai",
        "daniyal brother",
        "awab",
        "ad sial",
        "sad raja"
    ]

    print("Testing name matching system...")
    for test in test_cases:
        result = find_best_name_match(test)
        print(f"'{test}' -> {result}")
