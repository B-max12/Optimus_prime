"""
Note Tracking System - Main Module
Features: Voice-to-text, Categories, Search, Export, Google Drive Integration
"""

import json
import os
import datetime
from pathlib import Path
import csv
from typing import List, Dict, Optional

class NotesManager:
    def __init__(self, data_file="notes_data.json"):
        self.data_file = data_file
        self.notes = []
        self.categories = ["General", "Work", "Personal", "Ideas", "Todo", "Important"]
        self.load_notes()
    
    def load_notes(self):
        """Load notes from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.notes = json.load(f)
            else:
                self.notes = []
        except Exception as e:
            print(f"Error loading notes: {e}")
            self.notes = []
    
    def save_notes(self):
        """Save notes to JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.notes, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving notes: {e}")
            return False
    
    def add_note(self, content: str, category: str = "General") -> bool:
        """Add a new note"""
        try:
            if category not in self.categories:
                category = "General"
            
            note = {
                "id": len(self.notes) + 1,
                "content": content,
                "category": category,
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "modified_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.notes.append(note)
            self.save_notes()
            return True
        except Exception as e:
            print(f"Error adding note: {e}")
            return False
    
    def delete_note(self, note_id: int) -> bool:
        """Delete a note by ID"""
        try:
            self.notes = [note for note in self.notes if note["id"] != note_id]
            self.save_notes()
            return True
        except Exception as e:
            print(f"Error deleting note: {e}")
            return False
    
    def update_note(self, note_id: int, new_content: str) -> bool:
        """Update an existing note"""
        try:
            for note in self.notes:
                if note["id"] == note_id:
                    note["content"] = new_content
                    note["modified_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.save_notes()
                    return True
            return False
        except Exception as e:
            print(f"Error updating note: {e}")
            return False
    
    def search_notes(self, keyword: str) -> List[Dict]:
        """Search notes by keyword"""
        try:
            keyword = keyword.lower()
            results = []
            for note in self.notes:
                if keyword in note["content"].lower() or keyword in note["category"].lower():
                    results.append(note)
            return results
        except Exception as e:
            print(f"Error searching notes: {e}")
            return []
    
    def get_notes_by_category(self, category: str) -> List[Dict]:
        """Get all notes in a specific category"""
        try:
            return [note for note in self.notes if note["category"].lower() == category.lower()]
        except Exception as e:
            print(f"Error getting notes by category: {e}")
            return []
    
    def get_all_notes(self) -> List[Dict]:
        """Get all notes"""
        return self.notes
    
    def change_category(self, note_id: int, new_category: str) -> bool:
        """Change the category of a note"""
        try:
            if new_category not in self.categories:
                return False
            
            for note in self.notes:
                if note["id"] == note_id:
                    note["category"] = new_category
                    note["modified_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.save_notes()
                    return True
            return False
        except Exception as e:
            print(f"Error changing category: {e}")
            return False
    
    def export_to_txt(self, filename: str = None) -> bool:
        """Export all notes to a text file"""
        try:
            if filename is None:
                filename = f"notes_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("NOTES EXPORT\n")
                f.write(f"Exported on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                
                for note in self.notes:
                    f.write(f"Note ID: {note['id']}\n")
                    f.write(f"Category: {note['category']}\n")
                    f.write(f"Created: {note['created_at']}\n")
                    f.write(f"Content: {note['content']}\n")
                    f.write("-" * 60 + "\n\n")
            
            return True
        except Exception as e:
            print(f"Error exporting to TXT: {e}")
            return False
    
    def export_to_csv(self, filename: str = None) -> bool:
        """Export all notes to a CSV file"""
        try:
            if filename is None:
                filename = f"notes_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Category', 'Content', 'Created At', 'Modified At'])
                
                for note in self.notes:
                    writer.writerow([
                        note['id'],
                        note['category'],
                        note['content'],
                        note['created_at'],
                        note['modified_at']
                    ])
            
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def export_to_json(self, filename: str = None) -> bool:
        """Export all notes to a JSON file"""
        try:
            if filename is None:
                filename = f"notes_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.notes, f, indent=4, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Get statistics about notes"""
        try:
            stats = {
                "total_notes": len(self.notes),
                "categories": {}
            }
            
            for category in self.categories:
                count = len([n for n in self.notes if n["category"] == category])
                stats["categories"][category] = count
            
            return stats
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
