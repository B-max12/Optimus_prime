import os
import pygame
import time
import threading
import re
from fuzzywuzzy import fuzz
import webbrowser

class MusicPlayer:
    def __init__(self, music_directory=r"D:\songs"):
        self.music_directory = music_directory
        self.current_song = None
        self.is_playing = False
        self.paused = False
        self.queue = [] # Initialize queue
        
        if not os.path.exists(music_directory):
            os.makedirs(music_directory)
            print(f"Created music directory: {music_directory}")
        
        pygame.mixer.init()
    
    def get_local_songs(self):
        music_files = []
        supported_formats = ('.mp3', '.wav', '.ogg', '.m4a')
        
        if os.path.exists(self.music_directory):
            for file in os.listdir(self.music_directory):
                if file.lower().endswith(supported_formats):
                    music_files.append(file)
        return music_files
    
    def find_similar_song(self, song_name, threshold=60):
        local_songs = self.get_local_songs()
        best_match = None
        best_score = 0
        
        for song in local_songs:
            song_name_clean = os.path.splitext(song)[0]
            score = fuzz.partial_ratio(song_name.lower(), song_name_clean.lower())
            
            if score > best_score and score >= threshold:
                best_score = score
                best_match = song
        
        return best_match, best_score
    
    def play_local_song(self, song_file):
        def play_thread():
            try:
                song_path = os.path.join(self.music_directory, song_file)
                
                if not os.path.exists(song_path):
                    print(f"Song not found: {song_file}")
                    return False
                
                if self.is_playing:
                    pygame.mixer.music.stop()
                
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play()
                self.current_song = song_file
                self.is_playing = True
                
                self.monitor_playback()
                
            except Exception as e:
                print(f"Error playing song: {e}")
                self.is_playing = False
        
        thread = threading.Thread(target=play_thread, daemon=True)
        thread.start()
        return True

    def monitor_playback(self):
        while pygame.mixer.music.get_busy() or self.paused:
            time.sleep(1)
        self.is_playing = False
        print("Playback finished. Ready for next command.")
        # Auto-play next song in queue
        if self.queue:
            print("Playing next song from queue...")
            self.play_next()

    def pause_music(self):
        if self.is_playing and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
            print("Music paused")
    
    def resume_music(self):
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            print("Music resumed")
    
    def stop_music(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.paused = False
        print("Music stopped")

    # Volume Control
    def set_volume(self, volume):
        """Set volume (0.0 to 1.0)"""
        try:
            vol = float(volume)
            if 0.0 <= vol <= 1.0:
                pygame.mixer.music.set_volume(vol)
                print(f"Volume set to {int(vol*100)}%")
                return True
            return False
        except:
            return False

    def volume_up(self):
        current_vol = pygame.mixer.music.get_volume()
        new_vol = min(1.0, current_vol + 0.1)
        self.set_volume(new_vol)

    def volume_down(self):
        current_vol = pygame.mixer.music.get_volume()
        new_vol = max(0.0, current_vol - 0.1)
        self.set_volume(new_vol)

    def add_to_queue(self, song_file):
        self.queue.append(song_file)
        print(f"Added to queue: {song_file}")

    def play_next(self):
        if self.queue:
            next_song = self.queue.pop(0)
            self.play_local_song(next_song)
            return True
        else:
            print("Queue is empty.")
            return False
    
    def search_youtube(self, song_name):
        def youtube_thread():
            try:
                search_query = song_name.replace(' ', '+') + '+official+audio'
                youtube_url = f"https://www.youtube.com/results?search_query={search_query}"
                
                print(f"Searching YouTube for: {song_name}")
                
                # Register Chrome
                chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
                webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
                webbrowser.get('chrome').open(youtube_url)
                
                print("YouTube search opened in your browser!")
                print("Ready for next command.")
                return True
                
            except Exception as e:
                print(f"Error searching YouTube: {e}")
                return False
        
        thread = threading.Thread(target=youtube_thread, daemon=True)
        thread.start()
        return True
    
    def show_available_songs(self):
        songs = self.get_local_songs()
        if songs:
            print("\nAvailable local songs:")
            for i, song in enumerate(songs, 1):
                print(f"  {i}. {os.path.splitext(song)[0]}")
        else:
            print("\nNo local songs found in music directory.")
        print()

def clean_song_name(song_name):
    clean_name = re.sub(r'\(official.*?\)|\(official\)|official audio|official video', '', song_name, flags=re.IGNORECASE)
    clean_name = re.sub(r'\s+', ' ', clean_name).strip()
    return clean_name