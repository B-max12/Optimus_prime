import sys
import os
import importlib.util

def check_import(module_name, file_path=None):
    try:
        if file_path:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        else:
            importlib.import_module(module_name)
        print(f"✅ Successfully imported {module_name}")
        return True
    except Exception as e:
        print(f"❌ Failed to import {module_name}: {e}")
        return False

print("Starting verification...")

# Check standard imports
modules = ['speech_recognition', 'wikipedia', 'webbrowser', 'edge_tts', 'pygame', 'selenium']
for mod in modules:
    check_import(mod)

# Check custom modules
current_dir = os.getcwd()
print(f"Current directory: {current_dir}")

custom_modules = [
    ('music_player', 'music_player.py'),
    ('google_system', 'google_system.py'),
    ('file_operations', 'file_operations.py'),
    ('email_system', 'email_system.py'),
    ('youtube_search_auto', 'youtube_search_auto.py'),
    ('wahtsapp_Ai.main', os.path.join('wahtsapp_Ai', 'main.py'))
]

all_passed = True
for name, path in custom_modules:
    full_path = os.path.join(current_dir, path)
    if os.path.exists(full_path):
        if not check_import(name, full_path):
            all_passed = False
    else:
        print(f"❌ File not found: {path}")
        all_passed = False

if all_passed:
    print("\n🎉 All checks passed! The system should be ready to run.")
else:
    print("\n⚠️ Some checks failed. Please review the errors.")
