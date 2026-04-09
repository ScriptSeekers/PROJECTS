# Chat-Bot

A desktop-based conversational AI application that integrates with Google's Gemini API to provide intelligent chat responses through a graphical user interface.

## Features

- **GUI Interface**: 600x500 pixel tkinter window with scrollable text display
- **Color-Coded Messages**: User messages in blue, bot responses in green
- **Non-Blocking Threading**: Background processing prevents UI freezing
- **Special Commands**: Type "quit", "exit", or "bye" to close the application
- **Error Handling**: Graceful error messages for API failures

## Dependencies

- google-generativeai

## How to Run

```bash
.\.venv\Scripts\python CBAPI.py
```

## Setup Requirements

- Python 3.x with tkinter (usually included with Python)
- A valid Google Gemini API key (replace `___YOUR_KEY___` in CBAPI.py)
- A valid Gemini model name (replace `__YOUR_MODEL___` in CBAPI.py)

## Technical Details

- **API Integration**: Uses Google's Generative AI library
- **Threading**: Python's threading module for non-blocking responses
- **UI Framework**: tkinter for cross-platform desktop interface
- **Message Display**: Scrollable text area with color differentiation