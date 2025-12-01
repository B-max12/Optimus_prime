"""
Voice Commands Handler for Notes System
Processes voice commands and executes appropriate actions
"""

from notes_manager import NotesManager
from google_drive_integration import GoogleDriveManager
import re

class NotesCommandHandler:
    def __init__(self, speak_func, listen_func):
        self.notes_manager = NotesManager()
        self.drive_manager = GoogleDriveManager()
        self.speak = speak_func
        self.listen = listen_func
    
    def handle_command(self, command: str) -> bool:
        """Main command router"""
        if not command:
            return False
        
        command = command.lower().strip()
        
        # Add note commands
        if "create note" in command or "add note" in command or "make note" in command or "new note" in command:
            self.create_note_command()
            return True
        
        # View notes commands
        elif "show notes" in command or "view notes" in command or "list notes" in command or "display notes" in command:
            self.show_notes_command(command)
            return True
        
        # Search commands
        elif "search note" in command or "find note" in command or "search for" in command:
            self.search_notes_command(command)
            return True
        
        # Delete commands
        elif "delete note" in command or "remove note" in command:
            self.delete_note_command()
            return True
        
        # Update commands
        elif "update note" in command or "edit note" in command or "modify note" in command:
            self.update_note_command()
            return True
        
        # Category commands
        elif "change category" in command or "move note" in command:
            self.change_category_command()
            return True
        
        # Export commands
        elif "export note" in command or "save note" in command or "backup note" in command:
            self.export_notes_command()
            return True
        
        # Google Drive commands
        elif "upload to drive" in command or "sync to drive" in command or "backup to drive" in command:
            self.upload_to_drive_command()
            return True
        
        elif "show drive files" in command or "list drive files" in command:
            self.list_drive_files_command()
            return True
        
        # Statistics commands
        elif "notes statistics" in command or "notes stats" in command or "how many notes" in command:
            self.show_statistics_command()
            return True
        
        else:
            return False
    
    def create_note_command(self):
        """Create a new note"""
        self.speak("What would you like to note?")
        content = self.listen()
        
        if not content:
            self.speak("I didn't hear anything. Note cancelled.")
            return
        
        self.speak("Which category? Say General, Work, Personal, Ideas, Todo, or Important")
        category_input = self.listen()
        
        category = "General"
        if category_input:
            category_input = category_input.lower()
            if "work" in category_input:
                category = "Work"
            elif "personal" in category_input:
                category = "Personal"
            elif "idea" in category_input:
                category = "Ideas"
            elif "todo" in category_input or "to do" in category_input:
                category = "Todo"
            elif "important" in category_input:
                category = "Important"
        
        if self.notes_manager.add_note(content, category):
            self.speak(f"Note added to {category} category successfully!")
        else:
            self.speak("Sorry, I couldn't add the note. Please try again.")
    
    def show_notes_command(self, command: str):
        """Show notes (all or by category)"""
        notes = []
        
        # Check if user wants specific category
        if "work" in command:
            notes = self.notes_manager.get_notes_by_category("Work")
            category_name = "Work"
        elif "personal" in command:
            notes = self.notes_manager.get_notes_by_category("Personal")
            category_name = "Personal"
        elif "idea" in command:
            notes = self.notes_manager.get_notes_by_category("Ideas")
            category_name = "Ideas"
        elif "todo" in command or "to do" in command:
            notes = self.notes_manager.get_notes_by_category("Todo")
            category_name = "Todo"
        elif "important" in command:
            notes = self.notes_manager.get_notes_by_category("Important")
            category_name = "Important"
        else:
            notes = self.notes_manager.get_all_notes()
            category_name = "All"
        
        if not notes:
            self.speak(f"No notes found in {category_name} category.")
            return
        
        self.speak(f"You have {len(notes)} notes in {category_name} category.")
        
        for i, note in enumerate(notes[:5], 1):  # Show first 5 notes
            self.speak(f"Note {note['id']}: {note['content'][:100]}")
        
        if len(notes) > 5:
            self.speak(f"And {len(notes) - 5} more notes. Check the console for full list.")
            print("\n" + "="*60)
            print(f"{category_name} NOTES:")
            print("="*60)
            for note in notes:
                print(f"\nID: {note['id']}")
                print(f"Category: {note['category']}")
                print(f"Created: {note['created_at']}")
                print(f"Content: {note['content']}")
                print("-"*60)
    
    def search_notes_command(self, command: str):
        """Search for notes"""
        # Extract search keyword
        keyword = None
        if "for" in command:
            keyword = command.split("for", 1)[1].strip()
        
        if not keyword:
            self.speak("What would you like to search for?")
            keyword = self.listen()
        
        if not keyword:
            self.speak("I didn't hear a search term.")
            return
        
        results = self.notes_manager.search_notes(keyword)
        
        if not results:
            self.speak(f"No notes found containing '{keyword}'.")
            return
        
        self.speak(f"Found {len(results)} notes matching '{keyword}'.")
        
        for note in results[:3]:  # Read first 3 results
            self.speak(f"Note {note['id']} in {note['category']}: {note['content'][:100]}")
        
        if len(results) > 3:
            self.speak(f"And {len(results) - 3} more results. Check the console.")
            print("\n" + "="*60)
            print(f"SEARCH RESULTS FOR: {keyword}")
            print("="*60)
            for note in results:
                print(f"\nID: {note['id']}")
                print(f"Category: {note['category']}")
                print(f"Content: {note['content']}")
                print("-"*60)
    
    def delete_note_command(self):
        """Delete a note"""
        self.speak("What is the note ID you want to delete?")
        note_id_input = self.listen()
        
        if not note_id_input:
            self.speak("I didn't hear a note ID.")
            return
        
        # Extract number from input
        numbers = re.findall(r'\d+', note_id_input)
        if not numbers:
            self.speak("I couldn't find a valid note ID.")
            return
        
        note_id = int(numbers[0])
        
        self.speak(f"Are you sure you want to delete note {note_id}? Say yes or no.")
        confirmation = self.listen()
        
        if confirmation and "yes" in confirmation.lower():
            if self.notes_manager.delete_note(note_id):
                self.speak(f"Note {note_id} deleted successfully.")
            else:
                self.speak("Failed to delete the note. Please check the note ID.")
        else:
            self.speak("Deletion cancelled.")
    
    def update_note_command(self):
        """Update an existing note"""
        self.speak("What is the note ID you want to update?")
        note_id_input = self.listen()
        
        if not note_id_input:
            self.speak("I didn't hear a note ID.")
            return
        
        numbers = re.findall(r'\d+', note_id_input)
        if not numbers:
            self.speak("I couldn't find a valid note ID.")
            return
        
        note_id = int(numbers[0])
        
        self.speak("What is the new content?")
        new_content = self.listen()
        
        if not new_content:
            self.speak("I didn't hear any new content.")
            return
        
        if self.notes_manager.update_note(note_id, new_content):
            self.speak(f"Note {note_id} updated successfully.")
        else:
            self.speak("Failed to update the note. Please check the note ID.")
    
    def change_category_command(self):
        """Change the category of a note"""
        self.speak("What is the note ID?")
        note_id_input = self.listen()
        
        if not note_id_input:
            self.speak("I didn't hear a note ID.")
            return
        
        numbers = re.findall(r'\d+', note_id_input)
        if not numbers:
            self.speak("I couldn't find a valid note ID.")
            return
        
        note_id = int(numbers[0])
        
        self.speak("What is the new category? Say General, Work, Personal, Ideas, Todo, or Important")
        category_input = self.listen()
        
        if not category_input:
            self.speak("I didn't hear a category.")
            return
        
        category = "General"
        category_input = category_input.lower()
        if "work" in category_input:
            category = "Work"
        elif "personal" in category_input:
            category = "Personal"
        elif "idea" in category_input:
            category = "Ideas"
        elif "todo" in category_input or "to do" in category_input:
            category = "Todo"
        elif "important" in category_input:
            category = "Important"
        
        if self.notes_manager.change_category(note_id, category):
            self.speak(f"Note {note_id} moved to {category} category.")
        else:
            self.speak("Failed to change category. Please check the note ID.")
    
    def export_notes_command(self):
        """Export notes to different formats"""
        self.speak("What format would you like? Say text, CSV, or JSON")
        format_input = self.listen()
        
        if not format_input:
            self.speak("I didn't hear a format. Using text format.")
            format_input = "text"
        
        format_input = format_input.lower()
        success = False
        
        if "csv" in format_input:
            success = self.notes_manager.export_to_csv()
            format_name = "CSV"
        elif "json" in format_input:
            success = self.notes_manager.export_to_json()
            format_name = "JSON"
        else:
            success = self.notes_manager.export_to_txt()
            format_name = "text"
        
        if success:
            self.speak(f"Notes exported to {format_name} format successfully. Check your current directory.")
        else:
            self.speak("Failed to export notes.")
    
    def upload_to_drive_command(self):
        """Upload notes to Google Drive"""
        self.speak("Authenticating with Google Drive. Please wait.")
        
        if not self.drive_manager.authenticate():
            self.speak("Failed to authenticate with Google Drive. Make sure credentials.json is in the directory.")
            return
        
        # Export to JSON first
        export_file = "drive_backup.json"
        if not self.notes_manager.export_to_json(export_file):
            self.speak("Failed to prepare notes for upload.")
            return
        
        self.speak("Uploading to Google Drive...")
        
        if self.drive_manager.upload_file(export_file):
            self.speak("Notes uploaded to Google Drive successfully!")
        else:
            self.speak("Failed to upload notes to Google Drive.")
        
        # Clean up
        import os
        if os.path.exists(export_file):
            os.remove(export_file)
    
    def list_drive_files_command(self):
        """List files in Google Drive"""
        self.speak("Fetching files from Google Drive...")
        
        if not self.drive_manager.authenticate():
            self.speak("Failed to authenticate with Google Drive.")
            return
        
        files = self.drive_manager.list_files()
        
        if not files:
            self.speak("No backup files found in Google Drive.")
            return
        
        self.speak(f"Found {len(files)} backup files.")
        
        print("\n" + "="*60)
        print("GOOGLE DRIVE BACKUP FILES:")
        print("="*60)
        for file in files:
            print(f"\nName: {file['name']}")
            print(f"Modified: {file.get('modifiedTime', 'N/A')}")
            print(f"Size: {file.get('size', 'N/A')} bytes")
            print("-"*60)
    
    def show_statistics_command(self):
        """Show notes statistics"""
        stats = self.notes_manager.get_statistics()
        
        self.speak(f"You have {stats['total_notes']} notes in total.")
        
        for category, count in stats['categories'].items():
            if count > 0:
                self.speak(f"{category}: {count} notes")
        
        print("\n" + "="*60)
        print("NOTES STATISTICS:")
        print("="*60)
        print(f"Total Notes: {stats['total_notes']}")
        print("\nBy Category:")
        for category, count in stats['categories'].items():
            print(f"  {category}: {count}")
        print("="*60)
