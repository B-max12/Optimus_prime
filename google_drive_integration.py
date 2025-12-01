"""
Google Drive Integration Module
Upload and sync notes with Google Drive
"""

import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle

SCOPES = ['https://www.googleapis.com/auth/drive.file']

class GoogleDriveManager:
    def __init__(self, credentials_file='credentials.json'):
        self.credentials_file = credentials_file
        self.token_file = 'token.pickle'
        self.service = None
        self.folder_id = None
    
    def authenticate(self):
        """Authenticate with Google Drive"""
        creds = None
        
        # Load existing credentials
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    return False
            else:
                if not os.path.exists(self.credentials_file):
                    print("Error: credentials.json not found!")
                    print("Please download it from Google Cloud Console")
                    return False
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Error during authentication: {e}")
                    return False
            
            # Save credentials
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        try:
            self.service = build('drive', 'v3', credentials=creds)
            return True
        except Exception as e:
            print(f"Error building service: {e}")
            return False
    
    def create_notes_folder(self):
        """Create a folder for notes in Google Drive"""
        try:
            if not self.service:
                return False
            
            # Check if folder already exists
            results = self.service.files().list(
                q="name='NotesBackup' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            items = results.get('files', [])
            
            if items:
                self.folder_id = items[0]['id']
                return True
            
            # Create new folder
            file_metadata = {
                'name': 'NotesBackup',
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            self.folder_id = folder.get('id')
            return True
            
        except Exception as e:
            print(f"Error creating folder: {e}")
            return False
    
    def upload_file(self, filepath: str, filename: str = None) -> bool:
        """Upload a file to Google Drive"""
        try:
            if not self.service:
                if not self.authenticate():
                    return False
            
            if not self.folder_id:
                if not self.create_notes_folder():
                    return False
            
            if filename is None:
                filename = os.path.basename(filepath)
            
            file_metadata = {
                'name': filename,
                'parents': [self.folder_id]
            }
            
            media = MediaFileUpload(filepath, resumable=True)
            
            # Check if file already exists
            results = self.service.files().list(
                q=f"name='{filename}' and '{self.folder_id}' in parents and trashed=false",
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            items = results.get('files', [])
            
            if items:
                # Update existing file
                file_id = items[0]['id']
                self.service.files().update(
                    fileId=file_id,
                    media_body=media
                ).execute()
            else:
                # Create new file
                self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
            
            return True
            
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False
    
    def list_files(self):
        """List all files in the notes folder"""
        try:
            if not self.service:
                if not self.authenticate():
                    return []
            
            if not self.folder_id:
                if not self.create_notes_folder():
                    return []
            
            results = self.service.files().list(
                q=f"'{self.folder_id}' in parents and trashed=false",
                spaces='drive',
                fields='files(id, name, modifiedTime, size)',
                orderBy='modifiedTime desc'
            ).execute()
            
            return results.get('files', [])
            
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a file from Google Drive"""
        try:
            if not self.service:
                if not self.authenticate():
                    return False
            
            self.service.files().delete(fileId=file_id).execute()
            return True
            
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
