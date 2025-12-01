# file_operations.py
import pyautogui
import time
import subprocess

def open_application(app_name):
    """
    Open applications using Windows Start Menu
    """
    try:
        # Press Windows key to open Start Menu
        pyautogui.press("super")
        time.sleep(1)
        
        # Type application name
        pyautogui.typewrite(app_name)
        time.sleep(2)
        
        # Press Enter to open
        pyautogui.press("enter")
        time.sleep(2)
        
        return True, f"{app_name} should be opening now."
        
    except Exception as e:
        return False, f"Sorry, I couldn't open {app_name}. Error: {str(e)}"

def close_application(app_name):
    """
    Close applications using taskkill
    """
    try:
        # Application process mapping
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
        
        # Get process name
        process_name = app_processes.get(app_name.lower(), f"{app_name}.exe")
        
        # Close using taskkill
        result = subprocess.run(
            f"taskkill /f /im {process_name}", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        
        # Check if application was closed successfully
        if result.returncode == 0:
            return True, f"{app_name} has been closed successfully"
        else:
            if "not found" in result.stderr.lower() or "no tasks" in result.stdout.lower():
                return False, f"{app_name} is not running or already closed"
            else:
                return False, f"Could not close {app_name}"
                
    except Exception as e:
        return False, f"Sorry, I couldn't close {app_name}. Error: {str(e)}"

def parse_application_name(query, command_type="open"):
    """
    Extract application name from query
    """
    # Remove common words
    remove_words = ["optimus", "please", "can you", "could you", "would you"]
    
    for word in remove_words:
        query = query.replace(word, "")
    
    # Extract application name based on command type
    if command_type == "open":
        query = query.replace("open", "").strip()
    elif command_type == "close":
        query = query.replace("close", "").replace("stop", "").replace("exit", "").strip()
    
    return query