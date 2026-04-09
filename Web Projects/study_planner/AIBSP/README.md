# AIBSP - AI-Based Study Planner

## Overview

AIBSP (AI-Based Study Planner) is a web application built with Flask that helps students create personalized study plans using Google's Gemini AI. The app allows users to register, input their study preferences, and receive AI-generated weekly study schedules tailored to their goals and learning styles.

## Features

- **User Registration & Authentication**: Secure signup with OTP verification via email
- **AI-Powered Study Plans**: Generate customized weekly study schedules using Gemini AI
- **Dashboard**: Input form for study preferences (age, subjects, hours, style, goals, etc.)
- **Plan History**: View and manage previously generated study plans
- **Responsive Design**: Modern UI with glassmorphism effects
- **Database Integration**: SQLite for storing user data and study plans

## Technology Stack

- **Backend**: Python Flask
- **AI Integration**: Google Gemini AI (gemini-1.5-flash)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Email Service**: SMTP (Gmail) for OTP delivery

## Installation

1. **Clone or navigate to the project directory**:
   ```
   cd Web\ Projects\study_planner\AIBSP
   ```

2. **Install dependencies**:
   ```
   pip install -r doc/requirements.txt
   ```

3. **Configure the application**:
   - Edit `config.py` to set your database, SMTP, and Gemini API credentials
   - Ensure you have a valid Gemini API key from Google AI Studio
   - Set up Gmail app password for SMTP if using Gmail

4. **Initialize the database**:
   The app will automatically create the necessary tables on first run.

## Configuration

Update the following in `config.py`:

- **Database**: Currently configured for SQLite (`student.db`)
- **SMTP**: Configure your email server settings for OTP delivery
- **Gemini API**: Add your API key and model name

Note: The app uses SQLite by default, but config shows MySQL settings (not currently used).

## Usage

1. **Run the application**:
   ```
   python app.py
   ```

2. **Access the app**:
   Open your browser and go to `http://localhost:5000`

3. **Register**: Create an account with email verification
4. **Login**: Access your dashboard
5. **Create Study Plan**: Fill out the form with your details and generate a plan
6. **View History**: Check previous plans and delete if needed

## Database Schema

- **users**: Stores user information (username, email, password hash)
- **study_plans**: Stores generated study plans with user inputs and AI responses

## Security Notes

- Passwords are hashed using Werkzeug
- OTP verification for registration
- Session-based authentication
- Database saving can be toggled with `SAVE_DATA` flag in `app.py`

## File Structure

```
AIBSP/
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── student.db          # SQLite database (created automatically)
├── doc/
│   ├── requirements.txt # Python dependencies
│   └── Detail.docx      # Additional documentation
├── static/             # CSS, JS, images
├── templates/          # HTML templates
```

## Contributing

This is a personal project for ScriptSeekers Academy. For improvements or bug reports, please contact the developer.

## License

© 2025 Arpit Vishwakarma AKA ScriptSeekers.</content>
<parameter name="filePath">d:\PROJECTS\Web Projects\study_planner\AIBSP\README.md