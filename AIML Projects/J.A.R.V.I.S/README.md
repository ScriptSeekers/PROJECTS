# J.A.R.V.I.S (Just A Rather Very Intelligent System)

An advanced AI-powered voice assistant with 150+ commands, database persistence, and comprehensive system integration.

## Features

- **Voice Recognition**: Advanced speech recognition with ambient noise adjustment
- **Text-to-Speech**: Multiple voice options with adjustable rate and volume
- **150+ Commands**: Web browsing, file management, system control, entertainment
- **Database Persistence**: SQLite database for command history, preferences, and reminders
- **Multi-threading**: Background reminder checking and non-blocking operations
- **Intelligent Matching**: Fuzzy logic with 60% cutoff for command recognition

## Dependencies

- psutil
- pyttsx3
- pywhatkit
- reportlab
- requests
- speech_recognition

## How to Run

```bash
.\.venv\Scripts\python jarvis.py
```

## Command Categories

### Web & Browsing (20+ commands)
- Open websites: YouTube, Google, Facebook, Twitter, Instagram, GitHub, etc.
- Google search and YouTube playback

### File Management
- Create timestamped PDFs with system info
- Create text notes and open file explorer

### System Control
- Power management: Shutdown, restart, sleep, lock
- Launch applications: Calculator, Notepad, Chrome, VS Code, etc.
- System monitoring: CPU, memory, disk usage

### Time & Date
- Current time, date, and day identification

### Entertainment
- Random jokes and interesting facts

### Advanced Features
- Command history and usage statistics
- Reminder management with background checking

## Technical Details

- **Database**: SQLite with 4 tables (command_history, preferences, custom_commands, reminders)
- **Speech Engine**: pyttsx3 with configurable speech rate (170 wpm) and volume (0.9)
- **Recognition**: 10-second timeout with 15-second phrase limit
- **Threading**: Background reminder thread checking every 60 seconds
- **NLP**: Fuzzy matching with command aliases for flexibility

## Usage Examples

- "What time is it?" → Returns current time
- "Open YouTube" → Opens browser
- "Create PDF" → Generates timestamped PDF
- "System health" → Reports resource usage
- "Tell me a joke" → Random joke with TTS
- "Search for AI tutorials" → Google search