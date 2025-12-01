import speech_recognition as sr
import asyncio
import edge_tts
import tempfile
import os
from playsound3 import playsound
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import threading

# Threading lock for voice
voice_lock = threading.Lock()

async def speak_async(text):
    with voice_lock:
        try:
            print(f"Optimus: {text}")
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                output = f.name
            communicate = edge_tts.Communicate(text, voice="en-US-GuyNeural", rate="+0%")
            await communicate.save(output)
            playsound(output)
            os.remove(output)
        except Exception as e:
            print(f"[Error in speak_async]: {e}")

def speak(text):
    """Speak the given text"""
    asyncio.run(speak_async(text))

def take_command():
    """Listen to user voice and return as text"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.pause_threshold = 1
        try:
            audio = recognizer.listen(source, timeout=5)
            print("Recognizing...")
            query = recognizer.recognize_google(audio, language='en-in')
            print(f"User said: {query}")
            return query.lower()
        except Exception as e:
            print(f"Error: {e}")
            speak("Sorry, I didn't catch that. Please say again.")
            return "none"

def youtube_search():
    """Main function to search YouTube"""
    
    # Step 1: Setup Chrome with your profile
    speak("Opening YouTube")
    
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Run in background - DISABLED for visibility
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Set Chrome binary location
    chrome_options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    # Keep browser open after script finishes
    chrome_options.add_experimental_option("detach", True)
    
    try:
        # Initialize driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        
        # Step 2: Open YouTube
        driver.get("https://www.youtube.com/")
        time.sleep(3)
        
        # Step 3: Ask for search query
        speak("What do you want to search on YouTube?")
        
        # Step 4: Take voice command
        search_query = take_command()
        
        if search_query == "none":
            speak("No query received. Closing.")
            driver.quit()
            return
        
        # Step 5: Find search box and type query
        try:
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "search_query"))
            )
            search_box.clear()
            search_box.send_keys(search_query)
            search_box.send_keys(Keys.RETURN)
            
            speak(f"Searching for {search_query}")
            time.sleep(3)
            
            # Step 6: Ask to choose video
            speak("Please say the video number or title you want to play")
            
            # Interactive loop for selection
            max_attempts = 3
            video_found = False
            
            for attempt in range(max_attempts):
                video_choice = take_command()
                
                if video_choice == "none":
                    if attempt < max_attempts - 1:
                        speak("I didn't hear a selection. Please try again.")
                        continue
                    else:
                        speak("No selection made. Leaving search results open.")
                        return

                # Step 8: Find and click the video
                # Get all video titles - refresh list in case of page updates
                videos = driver.find_elements(By.ID, "video-title")
                
                # Try to match video by number or title
                
                # Check if user said a number (e.g., "first", "second", "1", "2")
                number_words = {"first": 0, "second": 1, "third": 2, "fourth": 3, "fifth": 4}
                
                for word, index in number_words.items():
                    if word in video_choice and index < len(videos):
                        videos[index].click()
                        speak(f"Playing {word} video")
                        video_found = True
                        break
                
                if video_found: break
                
                # Try to match by number
                for i in range(1, 6):
                    if str(i) in video_choice and (i-1) < len(videos):
                        videos[i-1].click()
                        speak(f"Playing video number {i}")
                        video_found = True
                        break
                
                if video_found: break
                
                # Try to match by title keywords
                for i, video in enumerate(videos[:5]):  # Check first 5 videos
                    title = video.get_attribute("title").lower()
                    if any(word in title for word in video_choice.split()):
                        video.click()
                        speak(f"Playing video: {video.get_attribute('title')[:50]}")
                        video_found = True
                        break
                
                if video_found: break
                
                speak("I couldn't find that video. Please say the number or title again.")
            
            if not video_found:
                speak("Could not find matching video. Leaving search results open.")
            
        except Exception as e:
            print(f"Error during search: {e}")
            speak("An error occurred while searching. Please try again.")
            # driver.quit() # Keep open for debugging/manual use

    except Exception as e:
        print(f"Error: {e}")
        speak("Could not open YouTube. Please check your Chrome setup.")
    # finally:
        # driver.quit() # Removed to keep browser open

if __name__ == "__main__":
    youtube_search()
