import os
import ast
import sys

def check_syntax(directory):
    print(f"Checking syntax in {directory}...")
    issues = []
    for root, dirs, files in os.walk(directory):
        if 'venv' in dirs:
            dirs.remove('venv') # Skip venv
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
            
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        source = f.read()
                    ast.parse(source)
                except SyntaxError as e:
                    issues.append(f"SyntaxError in {file}: {e}")
                except Exception as e:
                    issues.append(f"Error reading {file}: {e}")
    
    if issues:
        print("Found the following issues:")
        for issue in issues:
            print(issue)
    else:
        print("No syntax errors found.")

if __name__ == "__main__":
    check_syntax(os.getcwd())
