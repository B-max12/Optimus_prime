import os
import threading 
import datetime
import random
import speech_recognition as sr
import webbrowser
import time
import pyautogui
import tempfile
import asyncio
import subprocess
import re
import sys 
import time 
import getpass
import docx
import cryptography 
import cv2
import smtplib
from playsound3 import playsound
from music_player import MusicPlayer
from note_tracker import NoteTracker
import task_manager
from whatsapp_messenger import WhatsAppMessenger
from conversation_memory import ConversationMemory
import calculator
import navigation
from wish_me import wishme
from password_manager import PasswordManager, ScreenLock
from features import Features
import calendar_manager
from health_reminders import HealthReminders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Initialize global variables
youtube_active = False
youtube_driver = None
voice_lock= threading.Lock()
note_tracker = NoteTracker()
whatsapp_messenger = WhatsAppMessenger()
memory = ConversationMemory()
features = Features()
health_reminders = HealthReminders()
load_dotenv()




# ==========================================================
# ---------- VOICE SYSTEM (ElevenLabs v2.26.1+ - Final Fix) ----------
# ==========================================================
from elevenlabs import ElevenLabs
import os

# Get API key from environment variables
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    print("[CRITICAL ERROR] ELEVENLABS_API_KEY not found in .env file. Voice will not work.")
    # You can choose to exit here if the voice is critical
    # import sys
    # sys.exit(1) 

# Initialize the ElevenLabs client
try:
    eleven_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
except Exception as e:
    print(f"[Error initializing ElevenLabs client]: {e}")
    eleven_client = None

def speak(text):
    """Generates and plays audio using the ElevenLabs v2.26.1+ library."""
    if not eleven_client:
        print("Cannot speak: ElevenLabs client was not initialized.")
        return

    try:
        print(f"Optimus: {text}")
        
        # Generate the audio using the client instance
        # The voice ID for "Adam" is "pNInz6obpgDQGcFmaJgB"
        audio_stream = eleven_client.generate(
            text=text,
            voice="pNInz6obpgDQGcFmaJgB",
            model="eleven_monolingual_v1",
            stream=True  # Use streaming for faster playback
        )
        
        # Play the audio stream directly
        eleven_client.play(audio_stream)

    except Exception as e:
        print(f"[Error in speak (ElevenLabs)]: {e}")
        print("Please ensure your .env file exists and contains the correct ELEVENLABS_API_KEY.")

# ==========================================================
# ---------- VOICE INPUT ----------
# ==========================================================
def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nListening...")
        r.pause_threshold = 1
        try:
            r.adjust_for_ambient_noise(source, duration=1)
        except Exception:
            pass
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=15)
        except sr.WaitTimeoutError:
            speak("I didn't catch any sound.")
            return None
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language="en-US")
        print(f"You said: {query}\n")
    except Exception:
        speak("Could you please repeat that?")
        return None
    return query.lower()

# ==========================================================
# ---------- APPLICATION MANAGEMENT ----------
# ==========================================================
def open_application(app_name):
    """
    Open applications using Windows Start Menu
    """
    try:
        speak(f"Opening {app_name}")
        pyautogui.press("super")
        time.sleep(1)
        pyautogui.typewrite(app_name)
        time.sleep(2)
        pyautogui.press("enter")
        time.sleep(2)
        speak(f"{app_name} should be opening now.")
        return True
    except Exception as e:
        print(f"Error opening application: {e}")
        speak(f"Sorry, I couldn't open {app_name}.")
        return False

def close_application(app_name):
    """
    Close applications using taskkill
    """
    try:
        app_processes = {
            'notepad': 'notepad.exe',
            'calculator': 'calculator.exe',
            'paint': 'mspaint.exe',
            'word': 'winword.exe',
            'excel': 'excel.exe',
            'powerpoint': 'powerpnt.exe',
            'chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'edge': 'msedge.exe',
            'file explorer': 'explorer.exe',
            'command prompt': 'cmd.exe',
            'task manager': 'taskmgr.exe',
            'browser': 'chrome.exe'
        }
        process_name = app_processes.get(app_name.lower(), f"{app_name}.exe")
        speak(f"Closing {app_name}")
        result = subprocess.run(
            f"taskkill /f /im {process_name}", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            speak(f"{app_name} has been closed successfully")
            return True
        else:
            if "not found" in result.stderr.lower() or "no tasks" in result.stdout.lower():
                speak(f"{app_name} is not running or already closed")
            else:
                speak(f"Could not close {app_name}")
            return False
    except Exception as e:
        print(f"Error closing application: {e}")
        speak(f"Sorry, I couldn't close {app_name}")
        return False

def parse_application_name(query, command_type="open"):
    remove_words = ["optimus", "please", "can you", "could you", "would you"]
    for word in remove_words:
        query = query.replace(word, "")
    if command_type == "open":
        query = query.replace("open", "").strip()
    elif command_type == "close":
        query = query.replace("close", "").replace("stop", "").replace("exit", "").strip()
    return query
# ==========================================================
# ---------- NOTE TRACKING FUNCTIONS ----------
# ==========================================================
def add_voice_note():
    speak("What's the note you want to add?")
    note_text = takecommand()
    
    if note_text:
        speak("Which category should I put this note in?")
        category = takecommand()
        
        if not category:
            category = "general"
        
        note = note_tracker.add_note(note_text, category)
        speak(f"Note added to {category} category.")
        print(f"Note added: {note_text} (Category: {category})")
    else:
        speak("I couldn't understand your note. Please try again.")

def search_notes():
    speak("What would you like to search for?")
    query = takecommand()
    
    if query:
        results = note_tracker.search_notes(query)
        
        if results:
            speak(f"I found {len(results)} notes matching your search.")
            for i, note in enumerate(results[:5]):  # Limit to first 5 results
                speak(f"Note {i+1}: {note['text'][:50]}... in category {note['category']}")
        else:
            speak("I couldn't find any notes matching your search.")
    else:
        speak("I couldn't understand your search query. Please try again.")

def export_notes():
    speak("What format would you like to export your notes in? You can choose from JSON, TXT, MD, DOCX, or CSV.")
    format_type = takecommand()
    
    if format_type:
        speak("Do you want to export all notes or notes from a specific category?")
        choice = takecommand()
        
        category = None
        if choice and "category" in choice:
            speak("Which category?")
            category = takecommand()
        
        success, message = note_tracker.export_notes(format_type, category)
        
        if success:
            speak(f"Success! {message}")
        else:
            speak(f"Sorry, {message}")
    else:
        speak("I couldn't understand the export format. Please try again.")

def sync_with_google():
    speak("Do you want to sync all notes or notes from a specific category?")
    choice = takecommand()
    
    category = None
    if choice and "category" in choice:
        speak("Which category?")
        category = takecommand()
    
    success, message = note_tracker.sync_with_google_docs(category)
    
    if success:
        speak(f"Success! {message}")
    else:
        speak(f"Sorry, {message}")

def list_categories():
    categories = note_tracker.get_all_categories()
    
    if categories:
        speak(f"You have notes in {len(categories)} categories:")
        for category in categories:
            speak(category)
    else:
        speak("You don't have any notes yet.")

#==========================================================
# ---------- WHATSAPP COMMANDS ----------
# ==========================================================
def process_whatsapp_command(query):
    # Open WhatsApp
    if "open whatsapp" in query or "start whatsapp" in query:
        speak("Opening WhatsApp...")
        result = whatsapp_messenger.open_whatsapp()
        speak(result)
    
    # Send message
    elif "send message" in query or "whatsapp message" in query:
        speak("Who would you like to send message to?")
        name = takecommand()
        
        if not name or "cancel" in name:
            speak("Operation cancelled.")
            return
        
        speak("What message would you like to send?")
        message = takecommand()
        
        if not message or "cancel" in message:
            speak("Operation cancelled.")
            return
        
        speak("Sending message...")
        result = whatsapp_messenger.send_message_to_contact(name, message)
        speak(result)
    
    # Quick message (for frequent contacts)
    elif "quick message" in query:
        speak("Which contact?")
        name = takecommand()
        
        if not name or "cancel" in name:
            speak("Operation cancelled.")
            return
        
        speak("Quick message options: say 'busy', 'call me', 'on my way', 'thanks', or 'ok'")
        quick_msg = takecommand()
        
        if not quick_msg or "cancel" in quick_msg:
            speak("Operation cancelled.")
            return
        
        # Map quick messages
        quick_messages = {
            "busy": "I'm busy right now, will talk later.",
            "call me": "Please call me when you're free.",
            "on my way": "I'm on my way.",
            "thanks": "Thanks!",
            "ok": "OK"
        }
        
        message = quick_messages.get(quick_msg.lower(), quick_msg)
        
        speak("Sending quick message...")
        result = whatsapp_messenger.send_message_to_contact(name, message)
        speak(result)
    
    # Check if contact exists
    elif "check contact" in query or "find contact" in query:
        speak("What contact name would you like to check?")
        name = takecommand()
        
        if not name or "cancel" in name:
            speak("Operation cancelled.")
            return
        
        exists, best_match, score = whatsapp_messenger.check_contact_exists(name)
        
        if exists:
            phone = whatsapp_messenger.get_contact_phone(name)[0]
            speak(f"Yes, I found {best_match} in your contacts with phone number {phone}")
            speak(f"Match confidence: {score}%")
        else:
            speak(f"No close match found for '{name}'")
    
    # List all contacts
    elif "list contacts" in query or "show contacts" in query:
        contacts = whatsapp_messenger.list_all_contacts()
        if contacts:
            speak("You have the following contacts:")
            for name in contacts[:10]:  # Limit to first 10 to avoid too long speech
                speak(name)
        else:
            speak("You don't have any contacts saved")
    
    # Search and open chat (without sending message)
    elif "open chat" in query:
        speak("Which contact's chat would you like to open?")
        name = takecommand()
        
        if not name or "cancel" in name:
            speak("Operation cancelled.")
            return
        
        speak("Opening WhatsApp...")
        whatsapp_messenger.open_whatsapp()
        time.sleep(3)
        
        # Find best matching contact
        exists, best_match, score = whatsapp_messenger.check_contact_exists(name)
        
        if exists:
            speak(f"Opening chat with {best_match}...")
            result = whatsapp_messenger.search_contact(best_match)
            speak(f"Chat with {best_match} is now open")
            speak(f"Match confidence: {score}%")
        else:
            speak(f"No close match found for '{name}'")
    
    # Find similar contacts
    elif "find similar" in query or "search similar" in query:
        speak("What contact name would you like to find similar contacts for?")
        name = takecommand()
        
        if not name or "cancel" in name:
            speak("Operation cancelled.")
            return
        
        similar_contacts = whatsapp_messenger.get_all_similar_contacts(name)
        
        if similar_contacts:
            speak(f"I found {len(similar_contacts)} similar contacts:")
            for contact_name, score in similar_contacts[:5]:  # Limit to first 5
                speak(f"{contact_name} with {score}% match")
        else:
            speak(f"No similar contacts found for '{name}'")
# ==========================================================
# ---------- CONVERSATION FEATURES ----------
# ==========================================================
def handle_conversation_features(query):
    """Handle conversation memory and context features"""
    
    # Remember previous conversations
    if "remember" in query and "conversation" in query:
        history = memory.get_recent_history(5)
        if history:
            speak("Here are our recent conversations:")
            for i, exchange in enumerate(history, 1):
                speak(f"{i}. You said: {exchange['user']}")
                speak(f"I replied: {exchange['assistant']}")
        else:
            speak("I don't have any record of our previous conversations.")
        return True
    
    # Search conversation history
    elif "search" in query and "history" in query:
        keyword = re.sub(r'search.*history for (.+)', r'\1', query)
        if keyword == query:  # If pattern didn't match
            speak("What would you like me to search for in our conversation history?")
            keyword = takecommand()
        
        if keyword:
            results = memory.search_history(keyword)
            if results:
                speak(f"I found {len(results)} references to {keyword} in our conversation history:")
                for result in results[:3]:  # Limit to top 3 results
                    speak(f"You said: {result['user']}")
            else:
                speak(f"I couldn't find any references to {keyword} in our conversation history.")
        return True
    
    # Context-aware responses
    elif "tell me more" in query or "explain further" in query:
        context = memory.get_context(query)
        if context:
            speak("Based on our previous conversation:")
            for ctx in context:
                speak(f"You mentioned: {ctx}")
        else:
            speak("I don't have enough context from our previous conversation to elaborate further.")
        return True
    
    # User preferences learning
    elif "i prefer" in query or "i like" in query:
        preference_type = None
        value = None
        
        # Extract preference type and value
        if "formal" in query or "casual" in query:
            preference_type = "greeting_style"
            value = "formal" if "formal" in query else "casual"
        
        elif "morning person" in query or "night owl" in query:
            preference_type = "daily_rhythm"
            value = "morning person" if "morning person" in query else "night owl"
        
        elif "short answers" in query or "detailed answers" in query:
            preference_type = "response_style"
            value = "short" if "short answers" in query else "detailed"
        
        if preference_type and value:
            memory.learn_preference(preference_type, value)
            speak(f"I'll remember that you prefer {value} {preference_type.replace('_', ' ')}.")
        else:
            speak("I've noted your preference. I'll try to remember it for our future conversations.")
        return True
    
    # Check user preferences
    elif "what do you know about me" in query or "what do you remember about me" in query:
        if memory.user_preferences:
            speak("Here's what I've learned about your preferences:")
            for pref_type, prefs in memory.user_preferences.items():
                most_common = max(prefs, key=lambda x: x['count'])['value']
                speak(f"You prefer {most_common} {pref_type.replace('_', ' ')}.")
        else:
            speak("I haven't learned much about your preferences yet. As we talk more, I'll remember what you like.")
        return True
    
    # Clear conversation history
    elif "clear" in query and "history" in query:
        memory.conversation_history = []
        memory.save_memory()
        speak("I've cleared our conversation history.")
        return True
    
    return False
# ==========================================================
# ---------- PASSWORD MANAGER ----------
# ==========================================================
password_manager = PasswordManager()
screen_lock = ScreenLock()

def authenticate_master_password():
    """Authenticate the master password for the password manager"""
    master_password = getpass.getpass("Enter master password: ")
    if not password_manager._verify_master_password(master_password):
        speak("Incorrect master password. Access denied.")
        return None
    return master_password

def process_password_command(query):
    """Process password-related commands"""
    if "add password" in query:
        speak("Adding a new password. Please provide the service name.")
        service = takecommand()
        if not service:
            speak("I didn't catch the service name. Please try again.")
            return
        
        speak(f"Adding password for {service}. Please provide the username.")
        username = takecommand()
        if not username:
            speak("I didn't catch the username. Please try again.")
            return
        
        speak(f"Adding password for {service} with username {username}. Would you like to generate a strong password?")
        response = takecommand()
        
        if response and "yes" in response.lower():
            speak("Generating a strong password. What length would you like?")
            length_str = takecommand()
            try:
                length = int(length_str) if length_str else 12
            except ValueError:
                length = 12
                speak("I'll use the default length of 12 characters.")
            
            password = password_manager.generate_password(length=length)
            speak(f"Generated password: {password}. Saving now.")
        else:
            speak("Please provide the password.")
            password = takecommand()
            if not password:
                speak("I didn't catch the password. Please try again.")
                return
        
        master_password = authenticate_master_password()
        if master_password and password_manager.add_password(service, username, password, master_password):
            speak(f"Password for {service} added successfully.")
        else:
            speak("Failed to add password. Please check your master password.")
    
    elif "get password" in query or "retrieve password" in query:
        speak("Which service password would you like to retrieve?")
        service = takecommand()
        if not service:
            speak("I didn't catch the service name. Please try again.")
            return
        
        master_password = authenticate_master_password()
        if master_password:
            password_data = password_manager.get_password(service, master_password)
            if password_data:
                speak(f"Username for {service} is {password_data['username']}.")
                speak(f"Password for {service} is {password_data['password']}.")
                password_manager.copy_to_clipboard(password_data['password'])
                speak("Password has been copied to clipboard.")
            else:
                speak(f"No password found for {service}.")
    
    elif "update password" in query:
        speak("Updating password. Please provide the service name.")
        service = takecommand()
        if not service:
            speak("I didn't catch the service name. Please try again.")
            return
        
        speak(f"Updating password for {service}. Please provide the new username.")
        username = takecommand()
        if not username:
            speak("I didn't catch the username. Please try again.")
            return
        
        speak(f"Updating password for {service} with username {username}. Would you like to generate a new strong password?")
        response = takecommand()
        
        if response and "yes" in response.lower():
            speak("Generating a strong password. What length would you like?")
            length_str = takecommand()
            try:
                length = int(length_str) if length_str else 12
            except ValueError:
                length = 12
                speak("I'll use the default length of 12 characters.")
            
            password = password_manager.generate_password(length=length)
            speak(f"Generated password: {password}. Saving now.")
        else:
            speak("Please provide the new password.")
            password = takecommand()
            if not password:
                speak("I didn't catch the password. Please try again.")
                return
        
        master_password = authenticate_master_password()
        if master_password and password_manager.update_password(service, username, password, master_password):
            speak(f"Password for {service} updated successfully.")
        else:
            speak("Failed to update password. Please check your master password.")
    
    elif "delete password" in query:
        speak("Deleting password. Please provide the service name.")
        service = takecommand()
        if not service:
            speak("I didn't catch the service name. Please try again.")
            return
        
        master_password = authenticate_master_password()
        if master_password and password_manager.delete_password(service, master_password):
            speak(f"Password for {service} deleted successfully.")
        else:
            speak("Failed to delete password. Please check your master password.")
    
    elif "list services" in query or "list passwords" in query:
        master_password = authenticate_master_password()
        if master_password:
            services = password_manager.list_services(master_password)
            if services:
                speak("You have passwords for the following services:")
                for service in services:
                    speak(service)
            else:
                speak("You don't have any saved passwords.")
    
    elif "generate password" in query:
        speak("Generating a strong password. What length would you like?")
        length_str = takecommand()
        try:
            length = int(length_str) if length_str else 12
        except ValueError:
            length = 12
            speak("I'll use the default length of 12 characters.")
        
        password = password_manager.generate_password(length=length)
        speak(f"Generated password: {password}.")
        password_manager.copy_to_clipboard(password)
        speak("Password has been copied to clipboard.")
    
    elif "lock screen" in query:
        screen_lock.lock()
    
    elif "unlock screen" in query:
        speak("Please provide the unlock password.")
        password = takecommand()
        if password and screen_lock.unlock(password):
            speak("Screen unlocked successfully.")
        else:
            speak("Failed to unlock screen. Please try again.")
# ==========================================================
# ---------- COMMAND PROCESSING ----------
# ==========================================================
def process_command(query):
    if query is None:
        return
    
    # Screenshot commands
    if "take screenshot" in query or "screenshot" in query:
        speak("Taking a screenshot now.")
        features.take_screenshot()
    
    elif "gesture screenshot" in query or "hand screenshot" in query:
        speak("Starting gesture screenshot mode. Make a fist in front of the camera to take a screenshot.")
        features.start_gesture_screenshot()
    
    # Screen recording commands
    elif "start recording" in query or "record screen" in query:
        speak("Starting screen recording. Say 'stop recording' when you're done.")
        features.start_screen_recording()
    
    elif "stop recording" in query:
        speak("Stopping screen recording now.")
        features.stop_screen_recording()
    
    # OCR commands
    elif "extract text" in query or "ocr" in query:
        speak("Please provide the path to the image file.")
        image_path = input("Enter image path: ")
        if os.path.exists(image_path):
            text = features.extract_text_from_image(image_path)
            if text:
                speak(f"Extracted text: {text}")
            else:
                speak("Sorry, I couldn't extract any text from the image.")
        else:
            speak("The file path you provided doesn't exist.")
    
    # Translation commands
    elif "translate" in query:
        # Extract text to translate
        text_to_translate = query.replace("translate", "").strip()
        if not text_to_translate:
            speak("What text would you like me to translate?")
            text_to_translate = takecommand()
        
        if text_to_translate:
            # Try to detect target language
            target_lang = "en"  # default
            if "to spanish" in query or "in spanish" in query:
                target_lang = "es"
            elif "to french" in query or "in french" in query:
                target_lang = "fr"
            elif "to german" in query or "in german" in query:
                target_lang = "de"
            elif "to chinese" in query or "in chinese" in query:
                target_lang = "zh"
            
            speak(f"Translating to {target_lang}")
            translated = features.translate_text(text_to_translate, target_lang)
            if translated:
                speak(f"Translation: {translated}")
            else:
                speak("Sorry, I couldn't translate the text.")
    
    # Real-time translation commands
    elif "real time translation" in query or "conversation translation" in query:
        # Try to detect languages
        source_lang = "en"  # default
        target_lang = "es"  # default
        
        if "english to spanish" in query:
            source_lang, target_lang = "en", "es"
        elif "english to french" in query:
            source_lang, target_lang = "en", "fr"
        elif "english to german" in query:
            source_lang, target_lang = "en", "de"
        elif "spanish to english" in query:
            source_lang, target_lang = "es", "en"
        elif "french to english" in query:
            source_lang, target_lang = "fr", "en"
        
        speak(f"Starting real-time translation from {source_lang} to {target_lang}. Press 'q' to stop.")
        features.start_realtime_translation(source_lang, target_lang) 

    
    # Unknown command
    else:
        speak("I'm not sure how to help with that. You can ask me to take screenshots, record your screen, extract text from images, or translate text.")
# ==========================================================
# ---------- HEALTH REMINDER FUNCTIONS ----------
# ==========================================================
def process_medication_command(query):
    """Process medication reminder commands"""
    if "add medication" in query:
        speak("What medication would you like to add?")
        med_name = takecommand()
        if med_name:
            speak(f"When should you take {med_name}? Please tell me the time.")
            med_time = takecommand()
            if med_time:
                speak("What's the dosage? You can skip this if you want.")
                dosage = takecommand()
                if not dosage or dosage == "skip":
                    dosage = ""
                result = health_reminders.add_medication(med_name, med_time, dosage)
                speak(result)
                return True
    return False

def process_water_command(query):
    """Process water intake commands"""
    if "log water" in query or "drank water" in query or "had water" in query:
        # Check if the user specified how many glasses
        glasses = 1  # Default to 1 glass
        match = re.search(r'(\d+) glasses?', query)
        if match:
            glasses = int(match.group(1))
        
        result = health_reminders.log_water_intake(glasses)
        speak(result)
        return True
    elif "water intake" in query or "how much water" in query:
        result = health_reminders.get_water_intake()
        speak(result)
        return True
    return False

def process_exercise_command(query):
    """Process exercise reminder commands"""
    if "i exercised" in query or "did exercise" in query or "worked out" in query:
        result = health_reminders.acknowledge_exercise()
        speak(result)
        return True
    return False

def process_posture_command(query):
    """Process posture alert commands"""
    if "checked my posture" in query or "posture is good" in query:
        result = health_reminders.acknowledge_posture_check()
        speak(result)
        return True
    return False

def check_health_reminders():
    """Check and announce any due health reminders"""
    # Check medication reminders
    due_medications = health_reminders.check_medication_reminders()
    for med in due_medications:
        dosage_info = f" Take {med['dosage']}" if med['dosage'] else ""
        speak(f"Reminder: It's time to take your medication: {med['dosage']}.{dosage_info}")
    
    # Check water reminder
    if hasattr(health_reminders, 'water_reminder_due') and health_reminders.water_reminder_due:
        speak("Reminder: It's time to drink some water to stay hydrated.")
    
    # Check exercise reminder
    if hasattr(health_reminders, 'exercise_reminder_due') and health_reminders.exercise_reminder_due:
        speak("Reminder: It's time for some exercise. Even a short walk would be beneficial.")
    
    # Check posture alert
    if hasattr(health_reminders, 'posture_alert_due') and health_reminders.posture_alert_due:
        speak("Posture check: Please sit up straight and adjust your posture.")

# ==========================================================
# ---------- delay timer in background ----------
# ==========================================================
def send_email(subject, body, recipients, delay_seconds):
    """
    Function to send email after delay_seconds in background
    recipients: list of email addresses
    """
    def task():
        if delay_seconds > 0:
            time.sleep(delay_seconds)
        try:
            sender_email = "awabbhammad8@gmail.com"
            sender_password = "etbg xuql hcxo ohro"  # Gmail App Password

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, sender_password)

            for receiver_email in recipients:
                message = MIMEMultipart()
                message["From"] = sender_email
                message["To"] = receiver_email
                message["Subject"] = subject
                message.attach(MIMEText(body, "plain"))

                server.sendmail(sender_email, receiver_email, message.as_string())

            server.quit()
            speak("Scheduled Email has been sent successfully to all recipients.")
        except Exception as e:
            print("Error:", e)
            speak("Sorry, I could not send the scheduled email.")

    threading.Thread(target=task).start()  # Run in background

# ==========================================================
# ---------- MAIN PROGRAM ----------
# ==========================================================
if __name__ == "__main__":
    try:
        # Initialize Music Player
        music_dir = r"D:\songs"  # Your music folder path
        music_player = MusicPlayer(music_dir)
        print("Music Player initialized successfully")
    except Exception as e:
        print(f"Error initializing Music Player: {e}")
        music_player = None
    
    # Start the assistant with wish_me
    try:
       
        wishme()
    except Exception as e:
        print(f"Error loading wishme: {e}")
        # Fallback simple greeting
        hour = int(datetime.datetime.now().hour)
        if 0 <= hour < 12:
            speak("Good morning! How are you today?")
        elif 12 <= hour < 18:
            speak("Good afternoon! How's your day going?")
        else:
            speak("Good evening! Hope you're doing well.")
        speak("I'm ready to assist you. What would you like to do?")
    
    print("Now main program starts...")
    # Check if it's a new day and reset counters if needed
    now = datetime.datetime.now()
    if now.hour == 0 and now.minute < 5:  # Within first 5 minutes of midnight
        health_reminders.reset_daily_counters()
    
    # Main command loop
    try:
        while True:
            query = takecommand()
            if not query:
                continue
                # Wikipedia
            if "wikipedia" in query:
                speak("Searching on Wikipedia...")
                search_query = query.replace("wikipedia", "").strip()
                try:
                    import wikipedia
                    results = wikipedia.summary(search_query, sentences=2)
                    speak("According to Wikipedia,")
                    print(results)
                    for sent in results.split('. '):
                        if sent.strip():
                            speak(sent.strip() + ".")
                except Exception as e:
                    print(f"Wikipedia error: {e}")
                    speak("Sorry, I couldn't find anything useful on Wikipedia.")
            
            #=================================Music====================================
            elif "play music" in query or "music" in query:
                if not music_player:
                    speak("Music player is not initialized.")
                    continue
                    
                speak("which song would you like to listen...?")
                song_name = takecommand()
                if not song_name:
                    speak("I couldn't find that song. Please try again.")
                    continue
                if "none" in song_name:
                    speak("I couldn't find that song. Please try again.")
                    continue
                speak(f"searching for song: {song_name}")
                song_file, match_score = music_player.find_similar_song(song_name)
                if match_score > 70:
                    speak(f"found {song_file} in your collection. playing now.")
                    music_player.play_local_song(song_file)
                elif match_score > 50:
                    speak(f"i found a similar song: {song_file}. should i play it?")
                    confirmation = takecommand()
                    if confirmation and ("yes" in confirmation or "play" in confirmation):
                        speak(f"playing song {song_name}")
                        music_player.play_local_song(song_file)
                    elif confirmation and ("no" in confirmation or "stop" in confirmation):
                        speak("ok, not playing the song.")
                else:
                    speak("song not found in your collection. would you like me to search it on youtube?")
                    youtube_choice = takecommand()
                    if youtube_choice and ("yes" in youtube_choice or "search" in youtube_choice):
                        speak("searching for song on youtube")
                        music_player.search_youtube(song_name)
                    else:
                        speak("okay, not searching on youtube.")
            
            elif "pause music" in query or "pause song" in query:
                if music_player:
                    music_player.pause_music()
                    speak("Music paused.")
                    
            elif "resume music" in query or "resume song" in query:
                if music_player:
                    music_player.resume_music()
                    speak("Music resumed.")
                    
            elif "next song" in query:
                if music_player:
                    music_player.next_song()
                    speak("Playing next song.")
                    
            elif "previous song" in query:
                if music_player:
                    music_player.previous_song()
                    speak("Playing previous song.")
                    
            elif "show songs" in query or "list song" in query:
                if music_player:
                    songs = music_player.get_local_songs()
                    if songs:
                        speak(f"you have {len(songs)} songs in your collection")
                        print("\nAvailable songs:")
                        for i, song in enumerate(songs[:10], 1):
                            print(f"{i}. {os.path.splitext(song)[0]}")
                        if len(songs) > 10:
                            print(f".... and {len(songs) - 10} more songs")
                    else:
                        speak("No songs found in your collection.") 
                else:
                    speak("Music player not initialized.")
            
            #=================================Applications====================================
            elif "open" in query:
                app_name = parse_application_name(query, "open")
                if app_name:
                    open_application(app_name)
                else:
                    speak("Please tell me which application to open.")
            
            # CLOSE APPLICATION
            elif "close" in query or "stop application" in query:
                app_name = parse_application_name(query, "close")
                if app_name:
                    close_application(app_name)
                else:
                    speak("Please tell me which application to close.")
            elif "add note" in query or "create note" in query or "new note" in query:
                    add_voice_note()
        
            elif "search note" in query or "find note" in query or "look for" in query:
                search_notes()
        
            elif "export note" in query or "save note" in query:
                export_notes()
        
            elif "sync with google" in query or "google sync" in query:
                sync_with_google()
        
            elif "list categories" in query or "show categories" in query:
                list_categories()
            # 1. Add Task
            elif"add task" in query or "create task" in query:
                speak("What is the task?")
                task_query = takecommand()
                if task_query:
                    response = task_manager.add_task(task_query)
                    speak(response)

        # 2. Remove Task
            elif "remove task" in query or "delete task" in query:
                speak("Which task would you like to remove?")
                task_query = takecommand()
                if task_query:
                    response = task_manager.remove_task(task_query)
                    speak(response)

        # 3. Complete Task
            elif "complete task" in query or "finish task" in query or "done with" in query:
                speak("Which task have you completed?")
                task_query = takecommand()
                if task_query:
                    response = task_manager.complete_task(task_query)
                    speak(response)
        
        # 4. List all tasks
            elif "show my tasks" in query or "list all tasks" in query or "what's on my to do list" in query:
                response = task_manager.list_tasks(filter_type='all')
                speak(response)

        # 5. List pending tasks
            elif "show pending tasks" in query or "what's left to do" in query:
                response = task_manager.list_tasks(filter_type='pending')
                speak(response)
        
        # 6. List completed tasks
            elif "show completed tasks" in query:
                response = task_manager.list_tasks(filter_type='completed')
                speak(response)

        # 7. List tasks by category
            elif "show category" in query:
            # Extract category name from query
                category_match = re.search(r'category (\w+)', query, re.IGNORECASE)
                if category_match:
                    category_name = category_match.group(1)
                    response = task_manager.list_tasks(filter_type=f'category {category_name}')
                    speak(response)
                else:
                    speak("Please specify a category, for example, 'show category work'.")

              # WhatsApp commands
            elif any(word in query for word in ["whatsapp", "message", "contact", "chat"]):
                process_whatsapp_command(query)
            elif handle_conversation_features(query):
                continue
            elif "calculate" in query or "math" in query or "solve" in query:
            # Extract the expression to calculate
                expression = re.sub(r'(calculate|math|solve)', '', query).strip()
                result = calculator.calculate(expression)
                speak(f"The result is {result}")
        
            elif "convert currency" in query or "exchange rate" in query:
            # Extract currency conversion details
                pattern = r'convert (\d+\.?\d*) (\w+) to (\w+)'
                match = re.search(pattern, query)
            
                if match:
                    amount = float(match.group(1))
                    from_currency = match.group(2).upper()
                    to_currency = match.group(3).upper()
                
                    result = calculator.convert_currency(amount, from_currency, to_currency)
                    speak(f"{amount} {from_currency} is equal to {result} {to_currency}")
                else:
                    speak("Please specify the amount and currencies to convert.")
        
            elif "convert length" in query or "convert distance" in query:
                # Extract length conversion details
                pattern = r'convert (\d+\.?\d*) (\w+) to (\w+)'
                match = re.search(pattern, query)
            
                if match:
                    value = float(match.group(1))
                    from_unit = match.group(2)
                    to_unit = match.group(3)
                
                    result = calculator.convert_length(value, from_unit, to_unit)
                    speak(f"{value} {from_unit} is equal to {result} {to_unit}")
                else:
                    speak("Please specify the value and units to convert.")
        
            elif "convert weight" in query:
                # Extract weight conversion details
                pattern = r'convert (\d+\.?\d*) (\w+) to (\w+)'
                match = re.search(pattern, query)
            
                if match:
                    value = float(match.group(1))
                    from_unit = match.group(2)
                    to_unit = match.group(3)
                
                    result = calculator.convert_weight(value, from_unit, to_unit)
                    speak(f"{value} {from_unit} is equal to {result} {to_unit}")
                else:
                    speak("Please specify the value and units to convert.")
        
            elif "convert temperature" in query:
            # Extract temperature conversion details
                pattern = r'convert (\d+\.?\d*) (\w+) to (\w+)'
                match = re.search(pattern, query)
            
                if match:
                    value = float(match.group(1))
                    from_unit = match.group(2)
                    to_unit = match.group(3)
                
                    result = calculator.convert_temperature(value, from_unit, to_unit)
                    speak(f"{value} {from_unit} is equal to {result} {to_unit}")
                else:
                    speak("Please specify the value and units to convert.")
        
        # Location & Navigation features
            elif "directions" in query or "get directions" in query:
            # Extract origin and destination
                pattern = r'directions from (.+?) to (.+)'
                match = re.search(pattern, query)
            
                if match:
                    origin = match.group(1)
                    destination = match.group(2)
                
                # Check for travel mode
                    mode = "driving"  # default
                    if "walking" in query:
                        mode = "foot-walking"
                    elif "cycling" in query:
                        mode = "cycling-regular"
                
                    result = navigation.get_directions(origin, destination, mode)
                
                    if isinstance(result, dict):
                        # Fixed syntax error here
                        speak(f"The distance is {result['distance']:.2f} kilometers and it will take approximately {result['duration']:.0f} minutes.")
                        speak("Here are the directions:")
                        for step in result["steps"]:
                            speak(step)
                    else:
                        speak(result)
                else:
                    speak("Please specify the origin and destination.")
        
            elif "find" in query and "near" in query:
            # Extract location and place type
                pattern = r'find (.+?) near (.+)'
                match = re.search(pattern, query)
            
                if match:
                    place_type = match.group(1)
                    location = match.group(2)
                
                    result = navigation.find_nearby_places(location, place_type)
                
                    if isinstance(result, list) and result:
                        speak(f"I found {len(result)} {place_type}s near {location}. Here are the closest ones:")
                        for place in result[:5]:  # Mention top 5
                            speak(f"{place['name']} is {place['distance']:.2f} kilometers away.")
                    else:
                        speak(result)
                else:
                    speak("Please specify what you're looking for and where.")
        
            elif "traffic" in query:
            # Extract origin and destination
                pattern = r'traffic from (.+?) to (.+)'
                match = re.search(pattern, query)
            
                if match:
                    origin = match.group(1)
                    destination = match.group(2)
                
                    result = navigation.get_traffic_info(origin, destination)
                
                    if isinstance(result, dict):
                        speak(f"Traffic status: {result['status']}. {result['description']}")
                        if result['additional_time'] > 0:
                            speak(f"Expect an additional {result['additional_time']} minutes to your travel time.")
                    else:
                        speak(result)
                else:
                    speak("Please specify the origin and destination.")
        
            elif "distance" in query and "between" in query:
            # Extract two locations
                pattern = r'distance between (.+?) and (.+)'
                match = re.search(pattern, query)
            
                if match:
                    location1 = match.group(1)
                    location2 = match.group(2)
                
                # First get coordinates for both locations
                    import requests
                
                    try:
                        url1 = f"https://nominatim.openstreetmap.org/search?format=json&q={location1}"
                        url2 = f"https://nominatim.openstreetmap.org/search?format=json&q={location2}"
                    
                        response1 = requests.get(url1)
                        response2 = requests.get(url2)
                    
                        data1 = response1.json()
                        data2 = response2.json()
                    
                        if data1 and data2:
                            lat1 = float(data1[0]["lat"])
                            lon1 = float(data1[0]["lon"])
                            lat2 = float(data2[0]["lat"])
                            lon2 = float(data2[0]["lon"])
                        
                            distance = navigation.calculate_distance(lat1, lon1, lat2, lon2)
                            speak(f"The distance between {location1} and {location2} is {distance:.2f} kilometers.")
                        else:
                            speak("I couldn't find one or both locations.")
                    except Exception as e:
                        speak(f"Error calculating distance: {str(e)}")
                else:
                    speak("Please specify two locations to calculate the distance between.")
             # Check for health reminder commands first
            elif (process_medication_command(query) or 
                process_water_command(query) or 
                process_exercise_command(query) or 
                process_posture_command(query)):
                continue
            elif "health reminders" in query:
                speak("I can help you with medication reminders, water intake tracking, exercise reminders, and posture alerts. Just tell me what you'd like to do.")
        
            elif "check reminders" in query:
                check_health_reminders()
            elif "password" in query or "lock" in query:
                process_password_command(query)  
            if screen_lock.is_locked():
                speak("Screen is locked. Please provide the unlock password.")
                password = takecommand()
                if password and screen_lock.unlock(password):
                    speak("Screen unlocked successfully.")
                    continue
                else:
                    speak("Failed to unlock screen. Please try again.")
                    continue
        
                    # --- CALENDAR AND REMINDER SYSTEM COMMANDS ---
        
                 # 1. Create Calendar Event
            elif"create event" in query or "make an appointment" in query:
                speak("What is the event about? Please tell me the summary, date, and time.")
                event_query = takecommand()
                if event_query:
                    response = calendar_manager.create_event(event_query)
                    speak(response)
        
              # 2. View Calendar Events
            elif "view calendar" in query or "show my events" in query or "what's on my schedule" in query:
                response = calendar_manager.get_events()
                speak(response)
        
             # 3. Delete Calendar Event
            elif "delete event" in query:
                speak("Which event would you like to delete? Please say its name.")
                delete_query = takecommand()
                if delete_query:
                 # We add "delete event called" to match the function's parsing logic
                    full_delete_query = f"delete event called {delete_query}"
                    response = calendar_manager.delete_event(full_delete_query)
                    speak(response)
        
                 # 4. Set Reminder
            elif "set reminder" in query or "remind me" in query:
                speak("What should I remind you about, and on which day?")
                reminder_query = takecommand()
                if reminder_query:
                # We add "set reminder for" to match the function's parsing logic
                    full_reminder_query = f"set reminder for {reminder_query}"
                    response = calendar_manager.set_reminder(full_reminder_query)
                    speak(response)
        
                 # 5. Daily Schedule Briefing
            elif "daily briefing" in query or "what's my day like" in query or "my schedule for today" in query:
                response = calendar_manager.get_daily_schedule()
                speak(response)
            


            elif "exit" in query or "quit" in query:
                speak("Goodbye!")
                break
            elif "send an email" in query.lower():
                try:
                    # -------------------------------
                    # 1. Ask for Recipients
                    # -------------------------------
                    speak("To whom should I send the email? You can say multiple emails separated by 'and'.")
                    recipients_input = takecommand()

                    # Extract emails from voice input
                    recipient_list = [email.strip() for email in re.split(r"and|,| ", recipients_input) if "@" in email]

                    if not recipient_list:
                        speak("I could not find any valid email address. Cancelling.")
                        continue

                    speak(f"Okay, I will send the email to {', '.join(recipient_list)}")

                    # -------------------------------
                    # 2. Ask for Subject
                    # -------------------------------
                    speak("What should be the subject of the email?")
                    subject = takecommand()
                    speak(f"Email subject set as: {subject}")

                    # -------------------------------
                    # 3. Ask for Body
                    # -------------------------------
                    speak("What should I say in the email?")
                    body = takecommand()
                    speak(f"Email body set as: {body}")

                    # -------------------------------
                    # 4. Confirmation
                    # -------------------------------
                    speak("Do you want to send this email now or later? Say 'now' or 'later', or 'no' to cancel.")
                    confirmation = takecommand().lower()

                    if "now" in confirmation:
                        speak("Sending email now.")
                        send_email(subject, body, recipient_list, delay_seconds=0)

                    elif "later" in confirmation:
                        speak("After how much time should I send the email? You can say seconds or mm:ss format.")
                        delay_input = takecommand().lower().replace(" ", "")

                        # Parse Time
                        if ":" in delay_input:
                            try:
                                minutes, seconds = map(int, delay_input.split(":"))
                                delay_seconds = minutes * 60 + seconds
                            except:
                                delay_seconds = 10
                        else:
                            numbers = re.findall(r'\d+', delay_input)
                            if numbers:
                                delay_seconds = int(numbers[0])
                            else:
                                delay_seconds = 10

                        speak(f"Email scheduled to be sent after {delay_seconds} seconds.")
                        send_email(subject, body, recipient_list, delay_seconds)

                    else:
                        speak("Email sending cancelled.")
                        continue

                    speak("You can continue with your next task. I will send the email in the background.")

                except Exception as e:
                    print("Error:", e)
                    speak("Sorry, I could not send the email.")
    except KeyboardInterrupt:
        speak("Goodbye!")
