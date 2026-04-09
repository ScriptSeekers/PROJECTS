# Cognitive Analyzer

An AI-powered cognitive behavior analysis tool that tracks your thinking patterns, analyzes behavioral issues, and provides personalized feedback to enhance your learning journey.

## Features

- **Cognitive Pattern Tracking**: Analyzes your thinking patterns and identifies behavioral issues
- **AI-Powered Feedback**: Uses Google Gemini AI to provide direct, evidence-based feedback
- **Input Classification**: Automatically detects whether input is text or code, supporting 12+ programming languages
- **Learning Statistics**: Tracks total inputs, recent activity, and content type distribution
- **Behavioral Analysis**: Identifies patterns like shallow responses, repetition, avoidance of complexity
- **Web Interface**: Beautiful, responsive web application with real-time analysis
- **Database Persistence**: SQLite database stores all inputs and analysis history
- **Progress Tracking**: Monitors improvement over time with detailed statistics

## Dependencies

- fastapi - Web framework for the API backend
- uvicorn - ASGI server for running the FastAPI app
- google-generativeai - Google Gemini AI integration
- sqlite3 - Database for storing user inputs and patterns

## How to Run

1. **Install dependencies:**
   ```bash
   pip install fastapi uvicorn google-generativeai
   ```

2. **Set up Google API Key:**
   - Get your Google Generative AI API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Set the environment variable: `GOOGLE_API_KEY=your_api_key_here`
   - Or edit the script and replace `GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', "__YOUR_GOOGLE_API_KEY_HERE__")`

3. **Run the application:**
   ```bash
   python cognitive_analyzer.py
   ```

4. **Access the web interface:**
   - Open your browser and go to: `http://localhost:8000`
   - The application will automatically open in your default browser

## Usage

1. **Submit Input**: Enter text or code in the input area
2. **Auto-Detection**: The system automatically detects if your input is text or code
3. **Get Feedback**: Click "Get Cognitive Feedback" to receive AI analysis of your thinking patterns
4. **View Statistics**: Monitor your learning progress with detailed statistics
5. **Browse History**: Review your past inputs and analysis

## AI Analysis Features

The system analyzes:
- **Thinking Patterns**: Shallow, inconsistent, avoidant, or unclear thinking
- **Behavioral Issues**: Repetition of weak behaviors, lack of depth, avoidance of complexity
- **Contradictions**: Compares stated intent vs. actual behavior
- **Improvement Suggestions**: Clear, actionable, and realistic recommendations

## Supported Programming Languages

The system can detect and classify code in:
- Python, JavaScript, Java, C++, C#, PHP, HTML, CSS, SQL, Ruby, Go, Rust

## Database Schema

- **user_inputs**: Stores input_type (text/code), content, and timestamp
- Automatic database initialization on first run
- Persistent storage of all user interactions

## Technical Details

- **Backend**: FastAPI with RESTful API endpoints
- **Frontend**: Vanilla HTML/CSS/JavaScript with modern UI
- **AI Model**: Google Gemini 2.5-flash for cognitive analysis
- **Database**: SQLite for local data persistence
- **Real-time Analysis**: Content type detection with confidence scoring
- **Responsive Design**: Works on desktop and mobile devices

## API Endpoints

- `GET /` - Serve the web interface
- `POST /submit_input` - Submit user input for analysis
- `GET /get_feedback` - Get AI-powered cognitive feedback
- `GET /get_history` - Retrieve input history
- `DELETE /clear_history` - Clear all stored data
- `GET /get_stats` - Get learning statistics
- `POST /analyze_content` - Analyze content type and programming language

## Important Notes

- **API Key Required**: The AI analysis requires a valid Google Generative AI API key
- **Local Processing**: All data is processed locally; nothing is sent to external servers except API calls to Google
- **Educational Purpose**: Designed to help users improve their cognitive patterns and learning habits
- **Data Privacy**: All inputs are stored locally in SQLite database