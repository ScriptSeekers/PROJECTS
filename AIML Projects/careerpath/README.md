# CareerPath

An AI-powered web application that helps students discover their ideal career paths through comprehensive psychometric assessments.

## Features

- **Psychometric Testing**: 10-question assessment analyzing interests, strengths, and preferences
- **Personalized Recommendations**: Suggests one of 9 career paths based on results
- **Success Roadmaps**: Step-by-step guidance tailored to each recommended career
- **Skill Analysis**: Visual radar charts showing skill profiles
- **Educational Resources**: Curated YouTube videos for career exploration
- **User Tracking**: Maintains assessment history for registered users
- **Dark/Light Theme**: Toggle between themes with persistence

## Dependencies

- Chart.js (for radar chart visualization)
- Google Fonts (Poppins)

## How to Run

Simply open `index.html` in any modern web browser:

- **Option 1**: Double-click `index.html` to open in default browser
- **Option 2**: Right-click → "Open with" → Select your browser
- **Option 3**: Run a local server: `python -m http.server` in the careerpath folder, then visit `http://localhost:8000`

## Career Paths

- Science and Technology
- Business and Commerce
- Arts and Humanities
- Engineering Fields
- Medical and Healthcare
- Business Management
- Legal Professions
- Design and Creative Fields
- Multiple Options

## Technical Details

- **Frontend-only**: No backend server required
- **Client-side Storage**: Uses browser localStorage for data persistence
- **Responsive Design**: Works on desktop and mobile devices
- **Authentication**: Login/signup system with session management
- **Assessment History**: Tracks all previous assessments per user