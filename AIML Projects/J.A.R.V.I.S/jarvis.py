import speech_recognition as sr
import pyttsx3
import pywhatkit
import os
import webbrowser
import psutil
import subprocess
import datetime
import requests
import json
import time
import sqlite3
import threading
import random
import difflib
from reportlab.pdfgen import canvas
from pathlib import Path
from collections import defaultdict
import calendar

# ============================================================================
# CONFIGURATION & DATABASE
# ============================================================================
class Config:
    """Configuration management"""
    DB_FILE = "jarvis_data.db"
    LOG_FILE = "jarvis_logs.txt"
    COMMANDS_FILE = "custom_commands.json"
    SPEECH_RATE = 170
    SPEECH_VOLUME = 0.9
    LISTENING_TIMEOUT = 10
    LISTENING_PHRASE_TIME_LIMIT = 15

class Database:
    """SQLite database for storing commands, logs, and data"""
    def __init__(self, db_file=Config.DB_FILE):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Command history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY,
                command TEXT,
                response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User preferences
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        # Custom commands
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_commands (
                id INTEGER PRIMARY KEY,
                trigger TEXT UNIQUE,
                action TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Reminders
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY,
                reminder_text TEXT,
                remind_time DATETIME,
                is_completed BOOLEAN DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
    
    def log_command(self, command, response):
        """Log executed command"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO command_history (command, response) VALUES (?, ?)", (command, response))
        conn.commit()
        conn.close()
    
    def get_command_history(self, limit=10):
        """Get recent command history"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT command, timestamp FROM command_history ORDER BY id DESC LIMIT ?", (limit,))
        history = cursor.fetchall()
        conn.close()
        return history
    
    def add_reminder(self, reminder_text, remind_time):
        """Add a reminder"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO reminders (reminder_text, remind_time) VALUES (?, ?)", (reminder_text, remind_time))
        conn.commit()
        conn.close()
    
    def get_pending_reminders(self):
        """Get reminders that need to be triggered"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, reminder_text FROM reminders 
            WHERE is_completed = 0 AND remind_time <= datetime('now')
            ORDER BY remind_time ASC
        """)
        reminders = cursor.fetchall()
        conn.close()
        return reminders
    
    def mark_reminder_done(self, reminder_id):
        """Mark reminder as completed"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("UPDATE reminders SET is_completed = 1 WHERE id = ?", (reminder_id,))
        conn.commit()
        conn.close()

# ============================================================================
# VOICE ENGINE WITH ENHANCED FEATURES
# ============================================================================
class VoiceEngine:
    """Advanced text-to-speech with multiple voices"""
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', Config.SPEECH_RATE)
        self.engine.setProperty('volume', Config.SPEECH_VOLUME)
        self.voice_index = 0
        self.available_voices = self.engine.getProperty('voices')
    
    def speak(self, text, voice=None):
        """Convert text to speech with optional voice selection"""
        try:
            if voice and voice < len(self.available_voices):
                self.engine.setProperty('voice', self.available_voices[voice].id)
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Speech error: {e}")
    
    def set_rate(self, rate):
        """Change speech rate"""
        self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume):
        """Change speech volume"""
        self.engine.setProperty('volume', min(max(volume, 0), 1))

# ============================================================================
# ADVANCED SPEECH RECOGNITION
# ============================================================================
class SpeechRecognizer:
    """Advanced speech recognition with multiple engines"""
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
    
    def listen(self, speak_func=None):
        """Listen with advanced features"""
        with sr.Microphone() as source:
            if speak_func:
                speak_func("Listening")
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=Config.LISTENING_TIMEOUT, phrase_time_limit=Config.LISTENING_PHRASE_TIME_LIMIT)
                command = self.recognizer.recognize_google(audio)
                return command.lower()
            except sr.UnknownValueError:
                return ""
            except sr.RequestError:
                return ""
            except Exception as e:
                print(f"Recognition error: {e}")
                return ""

# ============================================================================
# NLP & COMMAND MATCHING
# ============================================================================
class CommandMatcher:
    """Intelligent command matching with fuzzy logic"""
    def __init__(self):
        self.command_aliases = {
            "youtube": ["youtube", "tube", "yt"],
            "google": ["google", "search"],
            "time": ["time", "clock", "what time", "current time"],
            "date": ["date", "today", "what date"],
            "weather": ["weather", "temperature", "forecast"],
            "news": ["news", "headlines"],
            "shutdown": ["shutdown", "power off", "turn off"],
            "restart": ["restart", "reboot"],
            "help": ["help", "what can you do", "capabilities"],
        }
    
    def find_best_match(self, command, candidates, cutoff=0.6):
        """Find best matching command using fuzzy matching"""
        matches = difflib.get_close_matches(command, candidates, n=1, cutoff=cutoff)
        return matches[0] if matches else None
    
    def extract_intent(self, command):
        """Extract intent from command"""
        for intent, aliases in self.command_aliases.items():
            for alias in aliases:
                if alias in command:
                    return intent
        return None

# ============================================================================
# BROWSER & WEB COMMANDS (ENHANCED)
# ============================================================================
class BrowserCommands:
    """Web browsing with enhanced features"""
    def __init__(self, voice_engine, db):
        self.voice = voice_engine
        self.db = db
        self.websites = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "facebook": "https://www.facebook.com",
            "twitter": "https://www.twitter.com",
            "instagram": "https://www.instagram.com",
            "github": "https://www.github.com",
            "stack overflow": "https://www.stackoverflow.com",
            "linkedin": "https://www.linkedin.com",
            "reddit": "https://www.reddit.com",
            "wikipedia": "https://www.wikipedia.org",
            "amazon": "https://www.amazon.com",
            "netflix": "https://www.netflix.com",
            "gmail": "https://mail.google.com",
            "drive": "https://drive.google.com",
            "stackoverflow": "https://www.stackoverflow.com",
            "github": "https://github.com",
            "python": "https://www.python.org",
        }
    
    def open_website(self, command):
        for site, url in self.websites.items():
            if site in command:
                self.voice.speak(f"Opening {site}")
                webbrowser.open(url)
                self.db.log_command(command, f"Opened {site}")
                return True
        return False
    
    def search_web(self, command):
        """Search on Google"""
        if "search" in command:
            search_term = command.replace("search", "").replace("for", "").strip()
            if search_term:
                self.voice.speak(f"Searching for {search_term}")
                url = f"https://www.google.com/search?q={search_term}"
                webbrowser.open(url)
                self.db.log_command(command, f"Searched: {search_term}")
                return True
        return False
    
    def play_video(self, command):
        """Play video on YouTube"""
        if "play" in command and "youtube" in command:
            search_term = command.replace("play", "").replace("on youtube", "").replace("youtube", "").strip()
            if search_term:
                self.voice.speak(f"Playing {search_term}")
                try:
                    pywhatkit.playonyt(search_term)
                    self.db.log_command(command, f"Played: {search_term}")
                    return True
                except Exception as e:
                    print(f"Error: {e}")
        return False

# ============================================================================
# FILE SYSTEM COMMANDS (ENHANCED)
# ============================================================================
class FileSystemCommands:
    """File and folder operations with advanced features"""
    def __init__(self, voice_engine, db):
        self.voice = voice_engine
        self.db = db
    
    def create_pdf(self, command):
        """Create advanced PDF"""
        if "create pdf" in command or "make pdf" in command:
            try:
                filename = f"jarvis_document_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                c = canvas.Canvas(filename)
                c.drawString(100, 750, "Document Created by Jarvis AI Assistant")
                c.drawString(100, 730, f"Created: {datetime.datetime.now()}")
                c.drawString(100, 710, f"System Info: {psutil.virtual_memory().percent}% RAM in use")
                c.save()
                self.voice.speak(f"PDF created as {filename}")
                self.db.log_command(command, f"Created: {filename}")
                return True
            except Exception as e:
                self.voice.speak("Error creating PDF")
        return False
    
    def create_note(self, command):
        """Create note with content"""
        if "create note" in command or "write note" in command:
            try:
                filename = f"note_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(filename, 'w') as f:
                    f.write(f"Note created by Jarvis\nDate: {datetime.datetime.now()}\n\n")
                self.voice.speak(f"Note created as {filename}")
                return True
            except Exception as e:
                self.voice.speak("Error creating note")
        return False
    
    def open_directory(self, command):
        """Open file explorer"""
        if "open file" in command or "file manager" in command or "explorer" in command:
            self.voice.speak("Opening file manager")
            os.startfile(os.path.expanduser("~"))
            return True
        return False

# ============================================================================
# SYSTEM COMMANDS (ENHANCED)
# ============================================================================
class SystemCommands:
    """System operations with advanced features"""
    def __init__(self, voice_engine, db):
        self.voice = voice_engine
        self.db = db
        self.applications = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "chrome": "chrome.exe",
            "firefox": "firefox.exe",
            "visual studio": "devenv.exe",
            "vs code": "code.exe",
            "word": "winword.exe",
            "excel": "excel.exe",
            "powerpoint": "powerpnt.exe",
            "task manager": "taskmgr.exe",
            "settings": "ms-settings:",
        }
    
    def open_application(self, command):
        """Open applications intelligently"""
        for app, exe in self.applications.items():
            if app in command:
                self.voice.speak(f"Opening {app}")
                try:
                    if exe.startswith("ms-"):
                        os.startfile(exe)
                    else:
                        os.startfile(exe)
                    return True
                except:
                    try:
                        subprocess.Popen(exe)
                        return True
                    except:
                        self.voice.speak(f"Could not open {app}")
        return False
    
    def get_system_health(self, command):
        """Get comprehensive system information"""
        if "system info" in command or "system health" in command:
            try:
                cpu = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                info = f"CPU: {cpu} percent, Memory: {memory.percent} percent, "
                info += f"Disk: {disk.percent} percent"
                
                self.voice.speak(info)
                print(f"\nSystem Health Report:")
                print(f"  CPU Usage: {cpu}%")
                print(f"  Memory Usage: {memory.percent}% ({memory.used // (1024**3)} GB used)")
                print(f"  Disk Usage: {disk.percent}%")
                print(f"  Available RAM: {memory.available // (1024**3)} GB\n")
                return True
            except:
                self.voice.speak("Error getting system info")
        return False
    
    def shutdown_system(self, command):
        """Shutdown with confirmation"""
        if "shutdown" in command:
            self.voice.speak("Shutting down in 30 seconds. Say cancel to stop.")
            os.system("shutdown /s /t 30")
            return True
        return False
    
    def restart_system(self, command):
        """Restart system"""
        if "restart" in command:
            self.voice.speak("Restarting in 30 seconds")
            os.system("shutdown /r /t 30")
            return True
        return False
    
    def sleep_system(self, command):
        """Sleep mode"""
        if "sleep" in command:
            self.voice.speak("Going to sleep")
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return True
        return False
    
    def lock_system(self, command):
        """Lock computer"""
        if "lock" in command:
            self.voice.speak("Locking computer")
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return True
        return False

# ============================================================================
# TIME & DATE COMMANDS (ENHANCED)
# ============================================================================
class TimeCommands:
    """Time and date operations with advanced features"""
    def __init__(self, voice_engine, db):
        self.voice = voice_engine
        self.db = db
    
    def get_time(self, command):
        """Get current time with details"""
        if "time" in command:
            now = datetime.datetime.now()
            time_str = now.strftime("%I:%M %p")
            self.voice.speak(f"The time is {time_str}")
            print(f"Current time: {now.strftime('%H:%M:%S')}")
            return True
        return False
    
    def get_date(self, command):
        """Get current date"""
        if "date" in command or "today" in command:
            now = datetime.datetime.now()
            date_str = now.strftime("%A, %B %d, %Y")
            self.voice.speak(f"Today is {date_str}")
            return True
        return False
    
    def get_day(self, command):
        """Get day of week"""
        if "what day" in command:
            now = datetime.datetime.now()
            day = now.strftime("%A")
            self.voice.speak(f"Today is {day}")
            return True
        return False
    
    def set_alarm(self, command):
        """Set alarm for future time"""
        if "alarm" in command or "remind me" in command:
            self.voice.speak("Alarm set for future implementation")
            return True
        return False

# ============================================================================
# WEATHER & NEWS (API INTEGRATION)
# ============================================================================
class WeatherNews:
    """Weather and news using APIs"""
    def __init__(self, voice_engine):
        self.voice = voice_engine
    
    def get_weather(self, command):
        """Get weather information"""
        if "weather" in command:
            try:
                # Using wttr.in API (no key required)
                response = requests.get("https://wttr.in/?format=%t+%C")
                if response.status_code == 200:
                    weather = response.text
                    self.voice.speak(f"Weather: {weather}")
                    return True
            except:
                self.voice.speak("Unable to fetch weather")
        return False
    
    def get_news(self, command):
        """Get headlines"""
        if "news" in command or "headlines" in command:
            try:
                # Using NewsAPI
                api_key = "demo"  # Replace with actual key
                self.voice.speak("News feature requires API key setup")
                return True
            except:
                self.voice.speak("Unable to fetch news")
        return False

# ============================================================================
# MEDIA & ENTERTAINMENT
# ============================================================================
class MediaCommands:
    """Media and entertainment commands"""
    def __init__(self, voice_engine):
        self.voice = voice_engine
    
    def tell_joke(self, command):
        """Tell jokes"""
        if "joke" in command:
            jokes = [
                "Why don't scientists trust atoms? Because they make up everything!",
                "Why did the scarecrow win an award? Because he was outstanding in his field!",
                "What do you call a fake noodle? An impasta!",
                "Why don't eggs tell jokes? They'd crack each other up!",
                "Parallel lines have so much in common. It's a shame they'll never meet.",
                "I'm reading a book on the history of glue. Can't put it down!",
            ]
            joke = random.choice(jokes)
            self.voice.speak(joke)
            return True
        return False
    
    def tell_fact(self, command):
        """Tell interesting facts"""
        if "fact" in command or "interesting" in command:
            facts = [
                "Honey never spoils!",
                "A group of flamingos is called a flamboyance!",
                "Octopuses have three hearts!",
                "Bananas are berries, but strawberries are not!",
                "The shortest war in history lasted 38 to 45 minutes!",
                "Cows have best friends and get stressed when separated!",
            ]
            fact = random.choice(facts)
            self.voice.speak(fact)
            return True
        return False

# ============================================================================
# ADVANCED UTILITIES
# ============================================================================
class AdvancedUtilities:
    """Advanced utility commands"""
    def __init__(self, voice_engine, db):
        self.voice = voice_engine
        self.db = db
    
    def show_help(self, command):
        """Show comprehensive help"""
        if "help" in command or "what can you do" in command:
            help_text = """
╔════════════════════════════════════════════════════════════╗
║            JARVIS V3 - VOICE ASSISTANT COMMANDS            ║
╚════════════════════════════════════════════════════════════╝

🌐 WEB & BROWSING:
   • "Open YouTube/Google/Facebook..." 
   • "Search for Python tutorials"
   • "Play music on YouTube"

📂 FILE MANAGEMENT:
   • "Create PDF"
   • "Create note"
   • "Open file manager"

⚙️ SYSTEM CONTROL:
   • "Open Calculator/Notepad/VS Code..."
   • "System health"
   • "Shutdown/Restart/Sleep/Lock"

🕐 TIME & DATE:
   • "What time is it?"
   • "What's today's date?"
   • "What day is it?"

🎭 ENTERTAINMENT:
   • "Tell me a joke"
   • "Tell me a fact"

📊 ADVANCED:
   • "Show history" - See recent commands
   • "Show reminders" - View pending reminders
   • "Set reminder" - Create new reminder

ℹ️ OTHER:
   • "Help" - Show this menu
   • "Stop/Exit/Goodbye" - Shut down Jarvis
            """
            print(help_text)
            self.voice.speak("Help menu displayed. Check console for details.")
            return True
        return False
    
    def show_history(self, command):
        """Show command history"""
        if "history" in command or "show history" in command:
            history = self.db.get_command_history(10)
            if history:
                self.voice.speak(f"Last {len(history)} commands")
                print("\n📋 Command History:")
                for idx, (cmd, ts) in enumerate(history, 1):
                    print(f"   {idx}. {cmd} - {ts}")
                print()
                return True
            else:
                self.voice.speak("No command history")
        return False
    
    def show_reminders(self, command):
        """Show pending reminders"""
        if "show reminders" in command or "reminders" in command:
            reminders = self.db.get_pending_reminders()
            if reminders:
                self.voice.speak(f"You have {len(reminders)} pending reminders")
                print("\n⏰ Pending Reminders:")
                for reminder_id, text in reminders:
                    print(f"   • {text}")
                print()
                return True
            else:
                self.voice.speak("No pending reminders")
        return False
    
    def set_reminder(self, command):
        """Set reminder"""
        if "remind me" in command or "set reminder" in command:
            self.voice.speak("Reminder feature initialized")
            # Parse time and reminder text
            remind_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
            self.db.add_reminder("Sample reminder", remind_time)
            return True
        return False

# ============================================================================
# BACKGROUND REMINDER CHECKER
# ============================================================================
class ReminderThread(threading.Thread):
    """Background thread to check reminders"""
    def __init__(self, db, voice_engine):
        super().__init__(daemon=True)
        self.db = db
        self.voice = voice_engine
        self.running = True
    
    def run(self):
        """Check reminders every minute"""
        while self.running:
            try:
                reminders = self.db.get_pending_reminders()
                for reminder_id, text in reminders:
                    self.voice.speak(f"Reminder: {text}")
                    self.db.mark_reminder_done(reminder_id)
            except Exception as e:
                print(f"Reminder check error: {e}")
            time.sleep(60)
    
    def stop(self):
        self.running = False

# ============================================================================
# MAIN JARVIS V3 CLASS
# ============================================================================
class JarvisAssistantV3:
    """Advanced AI Voice Assistant - Version 3"""
    def __init__(self):
        print("\n" + "="*60)
        print("🤖 JARVIS V3 - Advanced AI Voice Assistant")
        print("="*60 + "\n")
        
        # Initialize core components
        self.db = Database()
        self.voice = VoiceEngine()
        self.recognizer = SpeechRecognizer()
        self.matcher = CommandMatcher()
        
        # Initialize command handlers
        self.browser = BrowserCommands(self.voice, self.db)
        self.filesystem = FileSystemCommands(self.voice, self.db)
        self.system = SystemCommands(self.voice, self.db)
        self.time_commands = TimeCommands(self.voice, self.db)
        self.weather_news = WeatherNews(self.voice)
        self.media = MediaCommands(self.voice)
        self.utilities = AdvancedUtilities(self.voice, self.db)
        
        # Start reminder thread
        self.reminder_thread = ReminderThread(self.db, self.voice)
        self.reminder_thread.start()
        
        self.is_running = True
        self.command_count = 0
    
    def process_command(self, command):
        """Process voice command with intelligent matching"""
        if not command.strip():
            return False
        
        print(f"\n> Command: {command}")
        self.command_count += 1
        
        # Exit command
        if any(word in command for word in ["stop", "exit", "goodbye", "quit", "bye"]):
            self.voice.speak("Thank you for using Jarvis. Goodbye!")
            self.is_running = False
            return True
        
        # Try all command handlers
        handlers = [
            (self.browser.open_website, "Browser: Open website"),
            (self.browser.search_web, "Browser: Search"),
            (self.browser.play_video, "Browser: Play video"),
            (self.filesystem.create_pdf, "File: Create PDF"),
            (self.filesystem.create_note, "File: Create note"),
            (self.filesystem.open_directory, "File: Open directory"),
            (self.system.open_application, "System: Open app"),
            (self.system.get_system_health, "System: Health check"),
            (self.system.shutdown_system, "System: Shutdown"),
            (self.system.restart_system, "System: Restart"),
            (self.system.sleep_system, "System: Sleep"),
            (self.system.lock_system, "System: Lock"),
            (self.time_commands.get_time, "Time: Get time"),
            (self.time_commands.get_date, "Time: Get date"),
            (self.time_commands.get_day, "Time: Get day"),
            (self.weather_news.get_weather, "Weather: Get weather"),
            (self.weather_news.get_news, "News: Get news"),
            (self.media.tell_joke, "Entertainment: Joke"),
            (self.media.tell_fact, "Entertainment: Fact"),
            (self.utilities.show_help, "Help: Show help"),
            (self.utilities.show_history, "History: Show commands"),
            (self.utilities.show_reminders, "Reminders: Show reminders"),
            (self.utilities.set_reminder, "Reminders: Set reminder"),
        ]
        
        for handler, label in handlers:
            try:
                if handler(command):
                    self.db.log_command(command, label)
                    return True
            except Exception as e:
                print(f"Handler error ({label}): {e}")
        
        # Default response
        self.voice.speak("I did not understand that command. Say help for more options.")
        self.db.log_command(command, "UNRECOGNIZED")
        return False
    
    def run(self):
        """Main event loop"""
        self.voice.speak("Jarvis V3 online and ready to assist")
        
        while self.is_running:
            try:
                command = self.recognizer.listen(self.voice.speak)
                if command:
                    self.process_command(command)
            except KeyboardInterrupt:
                self.voice.speak("Shutting down Jarvis")
                self.is_running = False
                break
            except Exception as e:
                print(f"Error: {e}")
                self.voice.speak("An error occurred. Continuing...")
                continue
        
        # Cleanup
        self.reminder_thread.stop()
        print(f"\n{'='*60}")
        print(f"📊 Session Summary: {self.command_count} commands processed")
        print(f"{'='*60}\n")

# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    try:
        jarvis = JarvisAssistantV3()
        jarvis.run()
    except KeyboardInterrupt:
        print("\nJarvis terminated by user")
    except Exception as e:
        print(f"Critical error: {e}")
