import os
import platform
import difflib
import datetime
import speech_recognition as sr
import wikipedia
import webbrowser
import time
import pyautogui
import tempfile
import asyncio
import edge_tts
import smtplib
import re
import threading
import psutil
import subprocess
import json
from dotenv import load_dotenv
from pathlib import Path
from playsound3 import playsound
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- Custom Module Imports ---
try:
    from code_generator import CodeGenerator
    from hand_mouse import start_hand_mouse
    import google_system
    from music_player import MusicPlayer
    import email_system
    from notes_commands import NotesCommandHandler
    import system_control
    from task_manager_module import TaskManager, handle_task_commands
    from web_automation import WebAutomation
    from youtube_search_auto import youtube_search
    from agent_evaluator import AgentEvaluator
    from a2a_protocol import A2AManager, MessageType
    from mcp_integration import MCPManager
    from openapi_tools import OpenAPIToolGenerator, OPENAPI_SERVICES

except ImportError as e:
    print(f"Error importing modules: {e}")

load_dotenv()
# ==========================================================
# ---------- VOICE SYSTEM ----------
# ==========================================================
async def speak_async(text):
    try:
        print(f"Optimus: {text}")
        output = os.path.join(tempfile.gettempdir(), "voice.mp3")
        communicate = edge_tts.Communicate(text, voice="en-US-GuyNeural", rate="+0%")
        await communicate.save(output)
        playsound(output)
        os.remove(output)
    except Exception as e:
        print(f"[Error in speak_async]: {e}")

def speak(text):
    asyncio.run(speak_async(text))

def wishme():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good morning! How are you today?")
    elif 12 <= hour < 18:
        speak("Good afternoon! How's your day going?")
    else:
        speak("Good evening! Hope you're doing well.")
    speak("I'm ready to assist you. What would you like to do?")

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
# ---------- MAIN PROGRAM ----------
# ==========================================================
if __name__ == "__main__":
    # Initialize Modules
    try:
        code_gen = CodeGenerator()
        music_player = MusicPlayer()
        notes_handler = NotesCommandHandler(speak, takecommand)
        task_manager = TaskManager()
        web_auto = WebAutomation()
    except Exception as e:
        print(f"Error initializing modules: {e}")
      # Initialize new systems
    evaluator = AgentEvaluator()
    a2a_manager = A2AManager()
    mcp_manager = MCPManager()
    openapi_generator = OpenAPIToolGenerator()
    
    # Register A2A agents
    main_agent = a2a_manager.register_agent("optimus_main", "main_agent")
    email_agent = a2a_manager.register_agent("email_agent", "email_manager", port=8001)
    calendar_agent = a2a_manager.register_agent("calendar_agent", "calendar_manager", port=8002)
    
    # Start A2A agents
    a2a_manager.start_all_agents()
    
    # Connect to MCP
    mcp_manager.use_local_server()  # or mcp_manager.connect_to_server("http://mcp-server:3000")
    
    # Load OpenAPI services
    for service_name, service_info in OPENAPI_SERVICES.items():
        if openapi_generator.register_service(service_info['name'], service_info['spec_url']):
            print(f"Loaded OpenAPI service: {service_name}")
    wishme()

    while True:
        query = takecommand()
        if not query:
            continue


         # Track command execution for evaluation
        start_time = time.time()
        
        # ... existing command processing ...
        
        # After command execution
        end_time = time.time()
        response_time = end_time - start_time
        
        # Log for evaluation
        evaluator.log_command(query, success=True, response_time=response_time)
        
        # Use MCP for complex queries
        if "complex" in query or "analyze" in query:
            context = mcp_manager.get_context_for_query(query)
            if context:
                speak(f"Based on context, {context.get('summary', 'here is what I found')}")
        
        # Check for A2A commands
        if "ask email agent" in query:
            response = a2a_manager.send_command("optimus_main", "email_agent", "check_unread", {})
            if response:
                speak("Email agent is checking for new messages")

        # --- WIKIPEDIA ---
        if "wikipedia" in query:
            speak("Searching on Wikipedia...")
            search_query = query.replace("wikipedia", "").strip()
            try:
                results = wikipedia.summary(search_query, sentences=2)
                speak("According to Wikipedia,")
                print(results)
                speak(results)
            except Exception as e:
                print(f"Wikipedia error: {e}")
                speak("Sorry, I couldn't find anything useful on Wikipedia.")

        # --- OPEN/CLOSE APPLICATIONS ---
        elif "open" in query and "youtube" not in query: # Exclude youtube as it has its own handler
            app_name = parse_application_name(query, "open")
            open_application(app_name)

        elif "close" in query or "stop application" in query:
            app_name = parse_application_name(query, "close")
            if app_name:
                close_application(app_name)
            else:
                speak("Please tell me which application to close")

        # --- CODE GENERATION ---
        elif "generate code" in query or "write code" in query:
            speak("What should the code do?")
            description = takecommand()
            if description:
                speak("Which language?")
                language = takecommand()
                speak("Generating code, please wait...")
                result = code_gen.generate_code(description, language or "python")
                speak("Code generated successfully.")
                print(result)

        elif "create website" in query:
            speak("Describe the website you want to create.")
            description = takecommand()
            if description:
                speak("Generating website...")
                code_gen.generate_website(description)
                speak("Website generated.")

        # --- HAND MOUSE ---
        elif "start hand mouse" in query or "virtual mouse" in query:
            speak("Starting hand mouse. Press 'q' in the camera window to exit.")
            start_hand_mouse()

        # --- GOOGLE SYSTEM ---
        elif "google search" in query:
            search_query = query.replace("google search", "").strip()
            if not search_query:
                speak("What should I search for?")
                search_query = takecommand()
            if search_query:
                result = google_system.perform_google_search(search_query)
                speak(result)

        elif "news" in query:
            headlines = google_system.get_top_news()
            speak("Here are the top headlines:")
            for headline in headlines:
                speak(headline)

        elif "weather" in query:
            speak("Which city?")
            city = takecommand()
            if city:
                result = google_system.get_weather(city)
                speak(result)

        # --- MUSIC PLAYER ---
        elif "play music" in query or "play song" in query:
            speak("What song would you like to play?")
            song_name = takecommand()
            if song_name:
                # Try local first
                song_file, score = music_player.find_similar_song(song_name)
                if score > 80:
                    speak(f"Playing {song_file}")
                    music_player.play_local_song(song_file)
                else:
                    speak("Song not found locally. Searching on YouTube...")
                    music_player.search_youtube(song_name)

        elif "pause music" in query or "pause song" in query:
            music_player.pause_music()

        elif "resume music" in query:
            music_player.resume_music()

        elif "stop music" in query:
            music_player.stop_music()

        elif "next song" in query:
            music_player.play_next()

        elif "volume up" in query:
            music_player.volume_up()

        elif "volume down" in query:
            music_player.volume_down()

        # --- EMAIL SYSTEM ---
        elif "send email" in query:
            # Using the advanced email system
            speak("Who is the recipient?")
            recipient_text = takecommand()
            recipients = email_system.parse_recipients(recipient_text)
            
            if not recipients:
                speak("I couldn't understand the recipient. Please try again.")
                continue

            speak("What is the subject?")
            subject = takecommand()
            
            speak("What is the message?")
            body = takecommand()

            speak(f"Sending email to {', '.join(recipients)} with subject {subject}. Confirm?")
            confirm = takecommand()
            if "yes" in confirm or "ok" in confirm:
                email_system.send_email(subject, body, recipients)
                speak("Email sending initiated in background.")
            else:
                speak("Email cancelled.")

        # --- NOTES SYSTEM ---
        elif "note" in query: # "create note", "show notes", etc.
            notes_handler.handle_command(query)

        # --- SYSTEM CONTROL ---
        elif "battery" in query:
            status = system_control.get_battery_status()
            speak(status)

        elif "system stats" in query or "cpu usage" in query:
            stats = system_control.get_system_stats()
            speak(stats)

        elif "shutdown system" in query:
            speak("Are you sure you want to shutdown?")
            confirm = takecommand()
            if "yes" in confirm:
                system_control.shutdown_system()
            else:
                speak("Shutdown cancelled.")

        elif "restart system" in query:
            speak("Are you sure you want to restart?")
            confirm = takecommand()
            if "yes" in confirm:
                system_control.restart_system()
            else:
                speak("Restart cancelled.")

        # --- TASK MANAGER ---
        elif "task" in query: # "add task", "list tasks", etc.
            handle_task_commands(query, task_manager, speak)

        # --- YOUTUBE SEARCH ---
        elif "open youtube" in query or "search youtube" in query:
            youtube_search()

        # --- WEB AUTOMATION ---
        elif "fill form" in query:
            speak("Starting web automation for form filling.")
            if web_auto.setup_driver(headless=False):
                web_auto.auto_fill_common_form()
                speak("Form filling attempted.")
            else:
                speak("Could not setup web driver.")

        elif "job application" in query:
            speak("Starting job application automation.")
            if web_auto.setup_driver(headless=False):
                web_auto.fill_job_application()
                speak("Job application form filling attempted.")
       # Agent Evaluation Commands
        elif "agent performance" in query or "how am i doing" in query:
            report = evaluator.get_performance_report()
            speak(f"Your performance report: Success rate {report['success_rate']:.1f}%, "
                  f"average response time {report['average_response_time']:.2f} seconds, "
                  f"total commands {report['total_commands']}")

        elif "give feedback" in query or "rate performance" in query:
            speak("Please rate my performance from 1 to 10")
            rating = takecommand()
            if rating and any(str(i) in rating for i in range(1, 11)):
                speak("Thank you for your feedback!")
                evaluator.add_feedback(rating, int(rating))

# A2A Protocol Commands
        elif "agent status" in query or "list agents" in query:
            statuses = a2a_manager.get_agent_statuses()
            speak(f"I have {len(statuses)} agents running")
            for agent_id, info in statuses.items():
                speak(f"{agent_id} is {info['type']}")

# MCP Tools Commands
        elif "list tools" in query or "available tools" in query:
            tools = mcp_manager.get_tools()
            speak(f"I have {len(tools)} MCP tools available")
            for tool in tools[:3]:  # List first 3
                speak(f"{tool['name']}: {tool['description']}")

        elif "analyze with mcp" in query:
    # Extract text to analyze
            text = query.replace("analyze with mcp", "").strip()
            if text:
                result = mcp_manager.execute_mcp_tool("analyze_text", {"text": text, "analysis_type": "sentiment"})
                if result and 'analysis' in result:
                    sentiment = result['analysis'].get('sentiment', 'neutral')
                    speak(f"The text appears to be {sentiment}")

# OpenAPI Commands
        elif "weather api" in query or "check weather api" in query:
            tools = openapi_generator.generate_all_tools("weather_api")
            speak(f"Weather API has {len(tools)} operations available")

        elif "call openapi" in query:
    # Example: Get weather
            result = openapi_generator._execute_operation("weather_api", "getCurrentWeather", {"city": "London"})
            if result:
                speak("Weather data retrieved from OpenAPI")        

        # --- EXIT ---
        elif "exit" in query or "quit" in query or "shutdown optimus" in query:
            speak("Shutting down. Have a great day!")
            break