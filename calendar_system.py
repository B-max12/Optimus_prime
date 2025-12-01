import os
import datetime
import pickle
import asyncio
import threading
import time
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import edge_tts
from playsound3 import playsound
import tempfile

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarSystem:
    def __init__(self, speak_func):
        self.speak = speak_func
        self.service = None
        self.reminders = []
        self.reminder_thread = None
        self.stop_reminders = False
        self.data_dir = Path.home() / '.optimus_calendar'
        self.data_dir.mkdir(exist_ok=True)
        self.reminders_file = self.data_dir / 'reminders.pkl'
        self.load_reminders()
        
    def authenticate_google(self):
        """Authenticate with Google Calendar API"""
        creds = None
        token_path = self.data_dir / 'token.pickle'
        
        if token_path.exists():
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing credentials: {e}")
                    creds = None
            
            if not creds:
                creds_file = self.data_dir / 'credentials.json'
                if not creds_file.exists():
                    self.speak("Google Calendar credentials not found. Please place credentials.json in the .optimus_calendar folder in your home directory.")
                    print(f"Please download credentials.json from Google Cloud Console and place it at: {creds_file}")
                    return False
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    self.speak("Failed to authenticate with Google Calendar.")
                    print(f"Authentication error: {e}")
                    return False
            
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        try:
            self.service = build('calendar', 'v3', credentials=creds)
            return True
        except Exception as e:
            self.speak("Failed to connect to Google Calendar.")
            print(f"Service build error: {e}")
            return False
    
    def create_event(self, title, start_time, end_time=None, description=""):
        """Create a calendar event"""
        if not self.service:
            if not self.authenticate_google():
                return False
        
        try:
            if end_time is None:
                end_time = start_time + datetime.timedelta(hours=1)
            
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Asia/Karachi',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Asia/Karachi',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }
            
            event = self.service.events().insert(calendarId='primary', body=event).execute()
            self.speak(f"Event created successfully: {title}")
            return True
        except HttpError as error:
            self.speak("Failed to create event. Please check your internet connection.")
            print(f"Error creating event: {error}")
            return False
        except Exception as e:
            self.speak("An error occurred while creating the event.")
            print(f"Error: {e}")
            return False
    
    def view_events(self, days_ahead=7):
        """View upcoming events"""
        if not self.service:
            if not self.authenticate_google():
                return []
        
        try:
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            end_date = (datetime.datetime.utcnow() + datetime.timedelta(days=days_ahead)).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                timeMax=end_date,
                maxResults=10,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                self.speak("No upcoming events found.")
                return []
            
            self.speak(f"You have {len(events)} upcoming events.")
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                try:
                    start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                    formatted_time = start_dt.strftime('%B %d at %I:%M %p')
                except:
                    formatted_time = start
                
                print(f"- {event['summary']} on {formatted_time}")
            
            return events
        except HttpError as error:
            self.speak("Failed to retrieve events.")
            print(f"Error retrieving events: {error}")
            return []
        except Exception as e:
            self.speak("An error occurred while retrieving events.")
            print(f"Error: {e}")
            return []
    
    def delete_event(self, event_title):
        """Delete a calendar event by title"""
        if not self.service:
            if not self.authenticate_google():
                return False
        
        try:
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=50,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            found = False
            for event in events:
                if event_title.lower() in event['summary'].lower():
                    self.service.events().delete(calendarId='primary', eventId=event['id']).execute()
                    self.speak(f"Event deleted: {event['summary']}")
                    found = True
                    break
            
            if not found:
                self.speak(f"No event found with title: {event_title}")
                return False
            
            return True
        except HttpError as error:
            self.speak("Failed to delete event.")
            print(f"Error deleting event: {error}")
            return False
        except Exception as e:
            self.speak("An error occurred while deleting the event.")
            print(f"Error: {e}")
            return False
    
    def set_reminder(self, title, reminder_time):
        """Set a local reminder with voice notification"""
        reminder = {
            'title': title,
            'time': reminder_time,
            'notified': False
        }
        self.reminders.append(reminder)
        self.save_reminders()
        
        time_str = reminder_time.strftime('%I:%M %p on %B %d')
        self.speak(f"Reminder set for {title} at {time_str}")
        
        if self.reminder_thread is None or not self.reminder_thread.is_alive():
            self.start_reminder_checker()
        
        return True
    
    def start_reminder_checker(self):
        """Start background thread to check reminders"""
        self.stop_reminders = False
        self.reminder_thread = threading.Thread(target=self.check_reminders, daemon=True)
        self.reminder_thread.start()
    
    def check_reminders(self):
        """Background task to check and trigger reminders"""
        while not self.stop_reminders:
            now = datetime.datetime.now()
            
            for reminder in self.reminders:
                if not reminder['notified'] and now >= reminder['time']:
                    reminder['notified'] = True
                    self.trigger_reminder(reminder['title'])
            
            self.reminders = [r for r in self.reminders if not r['notified']]
            self.save_reminders()
            
            time.sleep(30)
    
    def trigger_reminder(self, title):
        """Trigger voice notification for reminder"""
        try:
            asyncio.run(self.speak_reminder(title))
        except Exception as e:
            print(f"Error triggering reminder: {e}")
    
    async def speak_reminder(self, title):
        """Async function to speak reminder"""
        try:
            text = f"Reminder: {title}"
            print(f"\n{'='*50}")
            print(f"REMINDER: {title}")
            print(f"{'='*50}\n")
            
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                output = f.name
            
            communicate = edge_tts.Communicate(text, voice="en-US-GuyNeural", rate="+5%")
            await communicate.save(output)
            playsound(output)
            os.remove(output)
        except Exception as e:
            print(f"Error in speak_reminder: {e}")
    
    def daily_briefing(self):
        """Provide daily schedule briefing"""
        now = datetime.datetime.now()
        greeting_hour = now.hour
        
        if 0 <= greeting_hour < 12:
            greeting = "Good morning"
        elif 12 <= greeting_hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        
        date_str = now.strftime('%A, %B %d, %Y')
        self.speak(f"{greeting}. Today is {date_str}. Let me check your schedule.")
        
        if not self.service:
            if not self.authenticate_google():
                self.speak("Unable to retrieve your schedule.")
                return
        
        try:
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
            today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=today_start,
                timeMax=today_end,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                self.speak("You have no events scheduled for today. You have a free day!")
            else:
                self.speak(f"You have {len(events)} events scheduled for today.")
                
                for i, event in enumerate(events, 1):
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    try:
                        start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                        time_str = start_dt.strftime('%I:%M %p')
                    except:
                        time_str = "all day"
                    
                    print(f"{i}. {event['summary']} at {time_str}")
            
            pending_reminders = [r for r in self.reminders if not r['notified']]
            if pending_reminders:
                self.speak(f"You also have {len(pending_reminders)} pending reminders.")
        
        except Exception as e:
            self.speak("Unable to retrieve your schedule at this time.")
            print(f"Error in daily briefing: {e}")
    
    def save_reminders(self):
        """Save reminders to file"""
        try:
            with open(self.reminders_file, 'wb') as f:
                pickle.dump(self.reminders, f)
        except Exception as e:
            print(f"Error saving reminders: {e}")
    
    def load_reminders(self):
        """Load reminders from file"""
        try:
            if self.reminders_file.exists():
                with open(self.reminders_file, 'rb') as f:
                    self.reminders = pickle.load(f)
                
                self.reminders = [r for r in self.reminders if not r['notified']]
                
                if self.reminders:
                    self.start_reminder_checker()
        except Exception as e:
            print(f"Error loading reminders: {e}")
            self.reminders = []
    
    def parse_datetime(self, date_str, time_str=None):
        """Parse natural language date and time"""
        now = datetime.datetime.now()
        
        date_str = date_str.lower().strip()
        
        if date_str == "today":
            target_date = now.date()
        elif date_str == "tomorrow":
            target_date = (now + datetime.timedelta(days=1)).date()
        elif "next" in date_str:
            weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            for i, day in enumerate(weekdays):
                if day in date_str:
                    days_ahead = (i - now.weekday() + 7) % 7
                    if days_ahead == 0:
                        days_ahead = 7
                    target_date = (now + datetime.timedelta(days=days_ahead)).date()
                    break
            else:
                return None
        else:
            try:
                target_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            except:
                return None
        
        if time_str:
            try:
                time_obj = datetime.datetime.strptime(time_str.strip(), "%H:%M").time()
            except:
                try:
                    time_obj = datetime.datetime.strptime(time_str.strip(), "%I:%M %p").time()
                except:
                    time_obj = datetime.time(9, 0)
        else:
            time_obj = datetime.time(9, 0)
        
        return datetime.datetime.combine(target_date, time_obj)
