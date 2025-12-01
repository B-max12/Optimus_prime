import os
import google.generativeai as genai
from datetime import datetime
import json
import re

class CodeGenerator:
    def __init__(self):
        """Initialize the Code Generator with Gemini AI"""
        self.output_dir = "generated_code"
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Initialize Gemini AI
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.ai_enabled = True
                print("[Code Generator] Gemini AI initialized successfully")
            else:
                self.ai_enabled = False
                print("[Code Generator] Warning: GEMINI_API_KEY not found in .env file")
        except Exception as e:
            self.ai_enabled = False
            print(f"[Code Generator] Error initializing Gemini: {e}")
    def _validate_input(self, description, language=None):
        """Validate input parameters"""
    if not description or not description.strip():
        raise ValueError("Description cannot be empty")
    
    if len(description.strip()) < 10:
        raise ValueError("Description should be more detailed")
    
    if language and language not in self._get_extension.__code__.co_consts[1]:
        raise ValueError(f"Unsupported language: {language}")

    def _sanitize_filename(self, filename):
        """Sanitize filename to prevent path traversal"""
    filename = os.path.basename(filename)
    # Remove any dangerous characters
    filename = re.sub(r'[^\w\.\-]', '_', filename)
    return filename
    
    def generate_code(self, description, language="python"):
        """Generate code snippet based on description"""
        if not self.ai_enabled:
            return {
                'success': False,
                'message': "Code generation is not available. Please add GEMINI_API_KEY to your .env file."
            }
        
        try:
            prompt = f"""
            Generate a complete, working {language} code based on this description:
            {description}
            
            Requirements:
            - Write clean, well-commented code
            - Follow best practices for {language}
            - Include error handling where appropriate
            - Add docstrings/comments explaining the code
            
            Provide only the code, no additional explanations.
            """
            
            response = self.model.generate_content(prompt)
            code = response.text
            
            # Clean up code block markers if present
            code = self._clean_code_blocks(code)
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{language}_code_{timestamp}.{self._get_extension(language)}"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code)
            
            return {
                'success': True,
                'message': f"Code generated successfully and saved to {filename}",
                'filepath': filepath,
                'code': code
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f"Error generating code: {str(e)}"
            }
    
    def generate_website(self, description, framework="html/css/js"):
        """Generate a complete website"""
        if not self.ai_enabled:
            return {
                'success': False,
                'message': "Website generation is not available. Please add GEMINI_API_KEY to your .env file."
            }
        
        try:
            framework_lower = framework.lower()
            
            # Determine what to generate based on framework choice
            if "react" in framework_lower:
                return self._generate_react_website(description)
            elif "vue" in framework_lower:
                return self._generate_vue_website(description)
            else:
                return self._generate_basic_website(description)
        
        except Exception as e:
            return {
                'success': False,
                'message': f"Error generating website: {str(e)}"
            }
    
    def _generate_basic_website(self, description):
        """Generate basic HTML/CSS/JS website"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        website_dir = os.path.join(self.output_dir, f"website_{timestamp}")
        os.makedirs(website_dir, exist_ok=True)
        
        # Generate HTML
        html_prompt = f"""
        Create a complete, modern HTML file for a website with this description:
        {description}
        
        Requirements:
        - Use semantic HTML5
        - Include proper meta tags
        - Link to external CSS file (styles.css) and JS file (script.js)
        - Make it responsive
        - Include all necessary sections based on the description
        
        Provide only the HTML code.
        """
        
        html_response = self.model.generate_content(html_prompt)
        html_code = self._clean_code_blocks(html_response.text)
        
        # Generate CSS
        css_prompt = f"""
        Create modern CSS for a website with this description:
        {description}
        
        Requirements:
        - Use modern CSS techniques (flexbox, grid)
        - Make it fully responsive
        - Include smooth animations
        - Use a professional color scheme
        - Add hover effects and transitions
        
        Provide only the CSS code.
        """
        
        css_response = self.model.generate_content(css_prompt)
        css_code = self._clean_code_blocks(css_response.text)
        
        # Generate JavaScript
        js_prompt = f"""
        Create JavaScript for a website with this description:
        {description}
        
        Requirements:
        - Add interactive features
        - Include smooth scrolling
        - Add form validation if forms are present
        - Include any dynamic functionality needed
        
        Provide only the JavaScript code.
        """
        
        js_response = self.model.generate_content(js_prompt)
        js_code = self._clean_code_blocks(js_response.text)
        
        # Save files
        with open(os.path.join(website_dir, "index.html"), 'w', encoding='utf-8') as f:
            f.write(html_code)
        
        with open(os.path.join(website_dir, "styles.css"), 'w', encoding='utf-8') as f:
            f.write(css_code)
        
        with open(os.path.join(website_dir, "script.js"), 'w', encoding='utf-8') as f:
            f.write(js_code)
        
        return {
            'success': True,
            'message': f"Website generated successfully in folder website_{timestamp}. Open index.html to view.",
            'directory': website_dir
        }
    
    def _generate_react_website(self, description):
        """Generate React-based website"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        website_dir = os.path.join(self.output_dir, f"react_app_{timestamp}")
        os.makedirs(website_dir, exist_ok=True)
        
        prompt = f"""
        Create a React application with this description:
        {description}
        
        Provide:
        1. A complete App.js component
        2. Any additional components needed
        3. CSS styles
        
        Use functional components with hooks.
        Format your response as:
        
        === App.js ===
        [code here]
        
        === [ComponentName].js ===
        [code here]
        
        === styles.css ===
        [code here]
        """
        
        response = self.model.generate_content(prompt)
        content = response.text
        
        # Parse the response and save individual files
        self._parse_and_save_files(content, website_dir)
        
        # Create a README
        readme_content = f"""# React Application

Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Description
{description}

## Setup
1. Make sure you have Node.js installed
2. Run `npx create-react-app .` in this directory
3. Replace the src files with the generated files
4. Run `npm start`
"""
        
        with open(os.path.join(website_dir, "README.md"), 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        return {
            'success': True,
            'message': f"React app generated in folder react_app_{timestamp}. Check README.md for setup instructions.",
            'directory': website_dir
        }
    def _generate_vue_website(self, description):
        """Generate Vue-based website"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    website_dir = os.path.join(self.output_dir, f"vue_app_{timestamp}")
    os.makedirs(website_dir, exist_ok=True)
    
    prompt = f"""
    Create a Vue.js application with this description:
    {description}
    
    Provide:
    1. A complete Vue component structure
    2. Main App.vue component
    3. Any additional components needed
    4. CSS styles
    
    Format your response as:
    
    === App.vue ===
    [code here]
    
    === [ComponentName].vue ===
    [code here]
    
    === main.js ===
    [code here]
    
    === styles.css ===
    [code here]
    """
    
    response = self.model.generate_content(prompt)
    content = response.text
    
    self._parse_and_save_files(content, website_dir)
    
    # Create README for Vue app
    readme_content = f"""# Vue.js Application

Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Description
{description}

## Setup
1. Make sure you have Node.js installed
2. Run `vue create .` or use the generated files in an existing Vue project
3. Run `npm run serve`
"""
    
    with open(os.path.join(website_dir, "README.md"), 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    return {
        'success': True,
        'message': f"Vue app generated in folder vue_app_{timestamp}. Check README.md for setup instructions.",
        'directory': website_dir
    }
   
    def generate_fullstack_app(self, description):
        """Generate a full-stack application with frontend and backend"""
        if not self.ai_enabled:
            return {
                'success': False,
                'message': "App generation is not available. Please add GEMINI_API_KEY to your .env file."
            }
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            app_dir = os.path.join(self.output_dir, f"fullstack_app_{timestamp}")
            os.makedirs(app_dir, exist_ok=True)
            
            # Create frontend and backend directories
            frontend_dir = os.path.join(app_dir, "frontend")
            backend_dir = os.path.join(app_dir, "backend")
            os.makedirs(frontend_dir, exist_ok=True)
            os.makedirs(backend_dir, exist_ok=True)
            
            # Generate backend (Python Flask/FastAPI)
            backend_prompt = f"""
            Create a Python backend API for this application:
            {description}
            
            Use Flask or FastAPI.
            Include:
            - Main application file
            - API routes
            - Database models (use SQLite)
            - CORS configuration
            
            Format as:
            === app.py ===
            [code]
            
            === models.py ===
            [code]
            
            === requirements.txt ===
            [dependencies]
            """
            
            backend_response = self.model.generate_content(backend_prompt)
            self._parse_and_save_files(backend_response.text, backend_dir)
            
            # Generate frontend (React)
            frontend_prompt = f"""
            Create a React frontend for this application:
            {description}
            
            Include:
            - Main App component
            - API integration
            - State management
            - Responsive design
            
            Provide complete React components.
            """
            
            frontend_response = self.model.generate_content(frontend_prompt)
            self._parse_and_save_files(frontend_response.text, frontend_dir)
            
            # Create main README
            readme = f"""# Full-Stack Application

Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Description
{description}

## Structure
- `backend/` - Python backend (Flask/FastAPI)
- `frontend/` - React frontend

## Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm start
```
"""
            
            with open(os.path.join(app_dir, "README.md"), 'w', encoding='utf-8') as f:
                f.write(readme)
            
            return {
                'success': True,
                'message': f"Full-stack app generated in folder fullstack_app_{timestamp}. Check README.md for setup.",
                'directory': app_dir
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f"Error generating full-stack app: {str(e)}"
            }
    
    def explain_code(self, code):
        """Explain what a code snippet does"""
        if not self.ai_enabled:
            return "Code explanation is not available. Please add GEMINI_API_KEY to your .env file."
        
        try:
            prompt = f"""
            Explain this code in simple terms:
            
            ```
            {code}
            ```
            
            Provide:
            1. What the code does
            2. How it works
            3. Key concepts used
            """
            
            response = self.model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            return f"Error explaining code: {str(e)}"
    
    def debug_code(self, code, error):
        """Help debug code based on error message"""
        if not self.ai_enabled:
            return "Code debugging is not available. Please add GEMINI_API_KEY to your .env file."
        
        try:
            prompt = f"""
            Debug this code that's producing an error:
            
            Code:
            ```
            {code}
            ```
            
            Error:
            {error}
            
            Provide:
            1. What's causing the error
            2. How to fix it
            3. Corrected code
            """
            
            response = self.model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            return f"Error debugging code: {str(e)}"
    
    def _clean_code_blocks(self, text):
        """Remove markdown code block markers"""
        # Remove ```language and ``` markers
        text = re.sub(r'```[\w]*\n', '', text)
        text = re.sub(r'```', '', text)
        return text.strip()
    
    def _get_extension(self, language):
        """Get file extension for programming language"""
        extensions = {
            'python': 'py',
            'javascript': 'js',
            'java': 'java',
            'c++': 'cpp',
            'c': 'c',
            'ruby': 'rb',
            'go': 'go',
            'rust': 'rs',
            'php': 'php',
            'html': 'html',
            'css': 'css',
            'typescript': 'ts',
        }
        return extensions.get(language.lower(), 'txt')
    
def _parse_and_save_files(self, content, directory):

    """Parse multi-file response and save individual files"""
    # Look for file markers like === filename === or ```filename
    file_pattern = r'(?:===|```)\s*(.+?)\s*(?:===|```)\s*\n(.*?)(?=(?:===|```)|$)'
    matches = re.findall(file_pattern, content, re.DOTALL)
    
    files_saved = 0
    if matches:
        for filename, code in matches:
            filename = filename.strip()
            # Remove any path traversal attempts for security
            filename = os.path.basename(filename)
            code = self._clean_code_blocks(code.strip())
            
            if filename:
                filepath = os.path.join(directory, filename)
                # Create subdirectories if needed
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(code)
                files_saved += 1
    
    if files_saved == 0:
        # If no file markers, save as single file
        code = self._clean_code_blocks(content)
        with open(os.path.join(directory, "generated_code.txt"), 'w', encoding='utf-8') as f:
            f.write(code)