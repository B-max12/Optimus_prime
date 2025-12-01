"""
Web Automation Tool - Automatically fill forms using personal info
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import json
import time
import os

class WebAutomation:
    def __init__(self, personal_info_file="personal_info.json"):
        """Initialize with personal information"""
        self.driver = None
        self.personal_info = self.load_personal_info(personal_info_file)
        
    def load_personal_info(self, filename):
        """Load personal information from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading personal info: {e}")
            return {}
    
    def setup_driver(self, headless=False):
        """Setup Chrome driver"""
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-notifications")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            return True
        except Exception as e:
            print(f"Error setting up driver: {e}")
            return False
    
    def open_url(self, url):
        """Open URL in browser"""
        try:
            self.driver.get(url)
            time.sleep(2)
            return True
        except Exception as e:
            print(f"Error opening URL: {e}")
            return False
    
    def fill_field(self, field_identifier, value, by=By.NAME):
        """Fill a single field"""
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((by, field_identifier))
            )
            element.clear()
            element.send_keys(value)
            return True
        except Exception as e:
            print(f"Could not fill field {field_identifier}: {e}")
            return False
    
    def upload_file(self, field_identifier, file_path, by=By.NAME):
        """Upload file to input field"""
        try:
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return False
            
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((by, field_identifier))
            )
            element.send_keys(file_path)
            time.sleep(1)
            return True
        except Exception as e:
            print(f"Could not upload file to {field_identifier}: {e}")
            return False
    
    def select_dropdown(self, field_identifier, value, by=By.NAME):
        """Select option from dropdown"""
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((by, field_identifier))
            )
            select = Select(element)
            select.select_by_visible_text(value)
            return True
        except Exception as e:
            print(f"Could not select dropdown {field_identifier}: {e}")
            return False
    
    def click_button(self, button_identifier, by=By.XPATH):
        """Click button"""
        try:
            button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((by, button_identifier))
            )
            button.click()
            time.sleep(1)
            return True
        except Exception as e:
            print(f"Could not click button: {e}")
            return False
    
    def auto_fill_common_form(self):
        """Auto-fill common form fields based on field names"""
        try:
            info = self.personal_info
            
            # Common field mappings
            field_mappings = {
                # Name fields
                'name': info['personal_info']['full_name'],
                'fullname': info['personal_info']['full_name'],
                'full_name': info['personal_info']['full_name'],
                'firstname': info['personal_info']['first_name'],
                'first_name': info['personal_info']['first_name'],
                'lastname': info['personal_info']['last_name'],
                'last_name': info['personal_info']['last_name'],
                
                # Contact fields
                'email': info['contact_info']['email'],
                'phone': info['contact_info']['phone'],
                'mobile': info['contact_info']['phone'],
                'contact': info['contact_info']['phone'],
                
                # Address fields
                'address': info['address']['current_address'],
                'city': info['address']['city'],
                'country': info['address']['country'],
                'postal_code': info['address']['postal_code'],
                'zip': info['address']['postal_code'],
                
                # CNIC / ID
                'cnic': info['personal_info']['cnic'],
                'id': info['personal_info']['cnic'],
                
                # Date of birth
                'dob': info['personal_info']['date_of_birth'],
                'date_of_birth': info['personal_info']['date_of_birth'],
                'birthdate': info['personal_info']['date_of_birth'],
            }
            
            # Try to fill each field
            for field_name, value in field_mappings.items():
                try:
                    # Try by name
                    self.fill_field(field_name, value, By.NAME)
                except:
                    try:
                        # Try by id
                        self.fill_field(field_name, value, By.ID)
                    except:
                        pass
            
            print("Auto-fill completed!")
            return True
            
        except Exception as e:
            print(f"Error in auto-fill: {e}")
            return False
    
    def fill_job_application(self):
        """Fill job application form"""
        try:
            info = self.personal_info
            
            # Fill personal info
            self.fill_field('name', info['personal_info']['full_name'])
            self.fill_field('email', info['contact_info']['email'])
            self.fill_field('phone', info['contact_info']['phone'])
            
            # Upload CV
            if 'cv_path' in info['documents']:
                self.upload_file('cv', info['documents']['cv_path'])
            
            # Upload photo if required
            if 'profile_photo' in info['photos']:
                self.upload_file('photo', info['photos']['profile_photo'])
            
            # Fill education
            self.fill_field('education', info['education']['highest_degree'])
            self.fill_field('university', info['education']['university'])
            
            # Fill experience
            self.fill_field('experience', info['work_experience']['years_of_experience'])
            self.fill_field('current_position', info['work_experience']['current_job'])
            
            print("Job application filled successfully!")
            return True
            
        except Exception as e:
            print(f"Error filling job application: {e}")
            return False
    
    def close_browser(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()

# Usage Example
if __name__ == "__main__":
    # Initialize automation
    auto = WebAutomation("personal_info.json")
    
    # Setup browser
    if auto.setup_driver(headless=False):
        
        # Open website
        auto.open_url("https://example.com/application-form")
        
        # Auto-fill form
        auto.auto_fill_common_form()
        
        # Or fill specific job application
        # auto.fill_job_application()
        
        # Wait before closing
        time.sleep(5)
        
        # Close browser
        auto.close_browser()
