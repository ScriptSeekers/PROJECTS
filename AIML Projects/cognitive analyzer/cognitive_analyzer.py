
import os
import sqlite3
import datetime
import threading
import webbrowser
from contextlib import contextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
import google.generativeai as genai

# ==================== CONFIGURATION ====================
# Configure Google AI
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', "__YOUR_GOOGLE_API_KEY_HERE__")
genai.configure(api_key=GOOGLE_API_KEY)

# ==================== MASTER PROMPT ====================
MASTER_PROMPT = """
You are a cognitive behavior analyst AI.

Your task is NOT to answer questions, but to analyze how the user thinks.

You are given:
1. A list of detected behavioral patterns
2. The user's latest input

Your job:

Step 1: Identify thinking patterns
- Are they shallow, inconsistent, avoidant, or unclear?

Step 2: Detect behavioral issues
- Repetition of weak behavior
- Lack of depth
- Avoidance of complexity

Step 3: Highlight contradictions
- Compare stated intent vs actual behavior

Step 4: Provide direct feedback
- Be specific and evidence-based
- Avoid generic advice

Step 5: Suggest improvement
- Clear, actionable, and realistic

Rules:
- Do not be polite or motivational
- Do not give generic answers
- Focus on analysis, not explanation
- Use the provided patterns as primary evidence

Output Format:

1. Observed Pattern
2. What It Means
3. Why It's a Problem
4. What To Do Next
"""

# ==================== DATABASE SETUP ====================
DB_PATH = "cognitive_patterns.db"

def init_database():
    """Initialize SQLite database with required tables"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_inputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_type TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

@contextmanager
def get_db():
    """Database connection context manager"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# ==================== PATTERN EXTRACTION ====================
def extract_patterns(inputs):
    """Extract behavioral patterns from user inputs"""
    patterns = []
    
    if not inputs:
        return patterns
    
    short_inputs = 0
    code_inputs = 0
    text_inputs = 0
    total_length = 0
    
    for inp in inputs:
        content = inp['content'] if isinstance(inp, dict) else inp.content
        input_type = inp['input_type'] if isinstance(inp, dict) else inp.input_type
        
        word_count = len(content.split())
        if word_count < 5:
            short_inputs += 1
        total_length += word_count
        
        if input_type != 'text':
            code_inputs += 1
        else:
            text_inputs += 1
    
    # Pattern detection rules
    if short_inputs > len(inputs) * 0.5:
        patterns.append("You tend to provide low-detail inputs (less than 5 words)")
    
    if code_inputs > text_inputs:
        patterns.append("You frequently submit code snippets")
    elif text_inputs > code_inputs and text_inputs > 0:
        patterns.append("You frequently submit text queries")
    
    avg_length = total_length / len(inputs)
    if avg_length < 10:
        patterns.append("Your responses are consistently brief and lacking depth")
    elif avg_length > 100:
        patterns.append("You provide detailed, thorough inputs")
    
    # Check for repetitive patterns in recent inputs
    recent_contents = [inp['content'] if isinstance(inp, dict) else inp.content for inp in inputs[:5]]
    if len(set(recent_contents)) < len(recent_contents) * 0.7:
        patterns.append("You are repeating similar content, showing potential stagnation")
    
    return patterns

# ==================== AI ANALYZER ====================
def analyze_behavior(patterns, latest_input):
    """Use Gemini AI to analyze user behavior"""
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_GOOGLE_API_KEY_HERE":
        return "Error: Google API key not configured. Please set your GOOGLE_API_KEY."
    
    try:
        prompt = f"{MASTER_PROMPT}\n\nPatterns:\n" + "\n".join(patterns) + f"\n\nLatest Input: {latest_input}"
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        return response.text.strip()
    except Exception as e:
        return f"AI Analysis Error: {str(e)}"

# ==================== FASTAPI BACKEND ====================
app = FastAPI(title="Cognitive Pattern Tracking AI")

class InputRequest(BaseModel):
    input_type: str  # 'text' or 'code'
    content: str

@app.post("/submit_input")
def submit_input(request: InputRequest):
    """Submit a new user input"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO user_inputs (input_type, content) VALUES (?, ?)",
                (request.input_type, request.content)
            )
            conn.commit()
            input_id = cursor.lastrowid
        return {"message": "Input submitted successfully", "id": input_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_feedback")
def get_feedback():
    """Get cognitive feedback based on recent inputs"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT input_type, content, timestamp FROM user_inputs ORDER BY timestamp DESC LIMIT 10"
            )
            inputs = [dict(row) for row in cursor.fetchall()]
        
        if not inputs:
            return {"feedback": "No inputs available for analysis. Please submit some text or code first."}
        
        patterns = extract_patterns(inputs)
        latest_input = inputs[0]['content']
        
        feedback = analyze_behavior(patterns, latest_input)
        return {"feedback": feedback}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_history")
def get_history(limit: int = 20):
    """Get user input history"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, input_type, content, timestamp FROM user_inputs ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            inputs = [dict(row) for row in cursor.fetchall()]
        return {"history": inputs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clear_history")
def clear_history():
    """Clear all user input history"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_inputs")
            conn.commit()
        return {"message": "History cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_stats")
def get_stats():
    """Get dashboard statistics"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Total inputs
            cursor.execute("SELECT COUNT(*) as total FROM user_inputs")
            total_inputs = cursor.fetchone()['total']
            
            # Inputs by type
            cursor.execute("SELECT input_type, COUNT(*) as count FROM user_inputs GROUP BY input_type")
            type_counts = {row['input_type']: row['count'] for row in cursor.fetchall()}
            clean_counts = {'code': 0, 'text': 0}
            for k, v in type_counts.items():
                if k == 'text':
                    clean_counts['text'] += v
                else:
                    clean_counts['code'] += v
            
            # Recent activity (last 7 days)
            cursor.execute("""
                SELECT COUNT(*) as recent FROM user_inputs 
                WHERE timestamp >= datetime('now', '-7 days')
            """)
            recent_activity = cursor.fetchone()['recent']
            
            # Average input length
            cursor.execute("SELECT AVG(LENGTH(content)) as avg_length FROM user_inputs")
            avg_length = cursor.fetchone()['avg_length'] or 0
            
            return {
                "total_inputs": total_inputs,
                "recent_activity": recent_activity,
                "avg_input_length": round(avg_length, 1),
                "languages": clean_counts
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze_content")
def analyze_content(request: dict):
    """Analyze content to determine if it's text or code, and detect programming language"""
    content = request.get('content', '').strip()
    
    if not content:
        return {"detected_type": "text", "language": None, "confidence": 0.0}
    
    # Language-specific detection patterns
    languages = {
        'python': {
            'keywords': ['def ', 'class ', 'import ', 'from ', 'if ', 'for ', 'while ', 'try:', 'except:', 'return ', 'elif ', 'with ', 'as ', 'lambda ', '__init__', 'self.', 'print('],
            'patterns': ['.py', '#!/usr/bin/env python', 'python', 'pip ', 'venv', '__name__ == "__main__"', 'sys.', 'os.', 'json.', 'requests.', 'print(', 'input(', 'len(', 'range(', 'str(', 'int(', 'float('],
            'imports': ['import ', 'from '],
            'score': 0
        },
        'javascript': {
            'keywords': ['function ', 'const ', 'let ', 'var ', 'if ', 'for ', 'while ', 'try ', 'catch ', 'return ', 'console.log', '=> ', 'async ', 'await ', 'class ', 'extends '],
            'patterns': ['.js', '.jsx', '.ts', '.tsx', 'npm ', 'node ', 'react', 'vue', 'angular', 'document.', 'window.', 'addEventListener', 'console.log(', 'alert(', 'setTimeout('],
            'imports': ['import ', 'require(', 'from '],
            'score': 0
        },
        'java': {
            'keywords': ['public class ', 'private ', 'protected ', 'static ', 'void ', 'int ', 'String ', 'System.out.println', 'import java.', 'extends ', 'implements ', 'new ', 'this.', 'super.'],
            'patterns': ['.java', 'public static void main', 'package ', 'import java.', 'javac ', 'gradle', 'maven', 'System.out.print'],
            'imports': ['import '],
            'score': 0
        },
        'cpp': {
            'keywords': ['#include ', 'int main(', 'cout <<', 'cin >>', 'std::', 'class ', 'public:', 'private:', 'void ', 'int ', 'char ', 'std::cout', 'std::endl'],
            'patterns': ['.cpp', '.cc', '.cxx', '.h', '.hpp', '#include <iostream>', '#include <string>', 'using namespace std', 'printf(', 'scanf('],
            'imports': ['#include '],
            'score': 0
        },
        'csharp': {
            'keywords': ['using ', 'namespace ', 'class ', 'public ', 'private ', 'static ', 'void ', 'int ', 'string ', 'Console.WriteLine', 'var ', 'new ', 'this.', 'base.'],
            'patterns': ['.cs', 'using System', 'dotnet ', 'nuget', 'Console.', 'System.', 'Console.Write('],
            'imports': ['using '],
            'score': 0
        },
        'php': {
            'keywords': ['<?php', 'function ', 'echo ', 'print ', '$', 'if ', 'for ', 'while ', 'class ', 'public ', 'private ', 'static ', 'require', 'include'],
            'patterns': ['.php', '<?php', '$_GET', '$_POST', 'mysql_', 'pdo', 'composer', 'echo ', 'print '],
            'imports': ['require', 'include', 'require_once', 'include_once'],
            'score': 0
        },
        'html': {
            'keywords': ['<html>', '<head>', '<body>', '<div>', '<p>', '<a ', '<img ', '<script>', '<style>', '<link ', '<meta ', 'href=', 'src=', 'class=', 'id='],
            'patterns': ['.html', '.htm', '<!DOCTYPE html>', '<html', '</html>', 'http-equiv', 'viewport'],
            'imports': [],
            'score': 0
        },
        'css': {
            'keywords': ['{', '}', ': ', ';', 'color:', 'background:', 'margin:', 'padding:', 'font-size:', 'display:', 'position:', 'width:', 'height:', '.class', '#id'],
            'patterns': ['.css', '@media ', '@import ', 'px', 'em', 'rem', '%', 'rgba(', 'linear-gradient'],
            'imports': ['@import '],
            'score': 0
        },
        'sql': {
            'keywords': ['SELECT ', 'FROM ', 'WHERE ', 'INSERT ', 'UPDATE ', 'DELETE ', 'CREATE ', 'ALTER ', 'DROP ', 'JOIN ', 'GROUP BY ', 'ORDER BY ', 'LIMIT '],
            'patterns': ['.sql', 'mysql', 'postgresql', 'sqlite', 'database', 'table', 'column'],
            'imports': [],
            'score': 0
        },
        'ruby': {
            'keywords': ['def ', 'class ', 'end', 'if ', 'elsif ', 'else ', 'puts ', 'print ', 'require ', 'gem ', 'attr_accessor', 'initialize'],
            'patterns': ['.rb', 'ruby', 'rails', 'gem ', 'bundler', 'rake', 'puts ', 'print '],
            'imports': ['require '],
            'score': 0
        },
        'go': {
            'keywords': ['package ', 'import ', 'func ', 'var ', 'const ', 'if ', 'for ', 'switch ', 'case ', 'fmt.Println', 'main()', 'go ', 'defer ', 'goroutine'],
            'patterns': ['.go', 'golang', 'go mod', 'go run', 'fmt.', 'os.', 'net/http', 'fmt.Print'],
            'imports': ['import '],
            'score': 0
        },
        'rust': {
            'keywords': ['fn ', 'let ', 'mut ', 'struct ', 'impl ', 'pub ', 'use ', 'mod ', 'println!', 'match ', 'if let ', 'enum ', 'trait '],
            'patterns': ['.rs', 'cargo', 'rustc', 'println!', 'std::', 'crate ', 'macro_rules!', 'print!'],
            'imports': ['use ', 'extern crate '],
            'score': 0
        }
    }
    
    # Analyze content for each language
    for lang, patterns in languages.items():
        score = 0
        
        # Check keywords (higher weight for unique identifiers)
        for keyword in patterns['keywords']:
            if keyword in content:
                # Give higher score for more specific keywords
                if len(keyword.strip()) > 5:  # Longer, more specific keywords
                    score += 3
                else:
                    score += 2
        
        # Check patterns (file extensions, specific syntax)
        for pattern in patterns['patterns']:
            if pattern in content:
                score += 2  # Reduced from 3 to be more balanced
        
        # Check import statements (very specific)
        for imp in patterns['imports']:
            if imp in content:
                score += 4
        
        languages[lang]['score'] = score
    
    # Find the language with highest score
    best_lang = max(languages.items(), key=lambda x: x[1]['score'])
    best_score = best_lang[1]['score']
    
    # Improved confidence calculation
    # Base confidence on content length and score
    content_length = len(content)
    
    # For short content, be more lenient
    if content_length < 50:
        min_score_needed = 2  # Just need 1-2 matches for short content
    elif content_length < 200:
        min_score_needed = 4  # Need a few matches for medium content
    else:
        min_score_needed = 6  # Need more matches for long content
    
    # Calculate confidence based on score vs minimum needed
    if best_score >= min_score_needed:
        confidence = min(best_score / (min_score_needed * 2), 1.0)
    else:
        confidence = best_score / (min_score_needed * 2)
    
    # Special handling for very short but clear code snippets
    if content_length < 30 and best_score >= 2:
        confidence = max(confidence, 0.6)  # Boost confidence for short clear matches
    
    # Determine final classification
    if confidence < 0.3:
        detected_type = "text"
        language = None
    elif confidence < 0.5:
        detected_type = "code"
        language = "unknown"
    else:
        detected_type = "code"
        language = best_lang[0]
    
    return {
        "detected_type": detected_type,
        "language": language,
        "confidence": round(confidence, 2),
        "scores": {lang: data['score'] for lang, data in languages.items()},
        "analysis": {
            "best_score": best_score,
            "content_length": content_length,
            "min_score_needed": min_score_needed,
            "language_detected": language,
            "top_matches": sorted(languages.items(), key=lambda x: x[1]['score'], reverse=True)[:3]
        }
    }

# ==================== FRONTEND HTML ====================
FRONTEND_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cognitive Pattern Tracking AI</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            animation: fadeIn 0.8s ease-in;
            display: grid;
            grid-template-columns: 1fr;
            grid-template-rows: auto auto auto auto;
            gap: 30px;
            padding: 20px;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            grid-template-rows: auto auto auto;
            gap: 25px;
            margin-top: 30px;
        }
        
        .main-input-section {
            grid-column: 1 / 9;
            grid-row: 1;
        }
        
        .stats-section {
            grid-column: 9 / 13;
            grid-row: 1;
        }
        
        .analysis-section {
            grid-column: 1 / 13;
            grid-row: 2;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
            position: relative;
        }
        
        .header h1 {
            font-size: 3rem;
            margin-bottom: 15px;
            font-weight: 700;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            animation: slideDown 1s ease-out;
        }
        
        @keyframes slideDown {
            from { transform: translateY(-50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.95;
            font-weight: 400;
            max-width: 600px;
            margin: 0 auto;
        }
        
        .header .subtitle {
            font-size: 1rem;
            opacity: 0.8;
            margin-top: 10px;
            font-style: italic;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 30px 80px rgba(0,0,0,0.2);
        }
        
        .card h2 {
            color: #2c3e50;
            margin-bottom: 25px;
            font-size: 1.8rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .card h2 i {
            color: #667eea;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 10px;
            font-weight: 600;
            color: #34495e;
            font-size: 1rem;
        }
        
        select, textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #e3e6ea;
            border-radius: 12px;
            font-size: 16px;
            transition: all 0.3s ease;
            background: white;
            font-family: inherit;
        }
        
        select:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            transform: translateY(-2px);
        }
        
        textarea {
            resize: vertical;
            min-height: 120px;
            line-height: 1.6;
        }
        
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            position: relative;
            overflow: hidden;
        }
        
        button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        button:hover::before {
            left: 100%;
        }
        
        button:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        
        button:active {
            transform: translateY(-1px);
        }
        
        .button-group {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-top: 20px;
        }
        
        .btn-secondary {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        
        .btn-secondary:hover {
            box-shadow: 0 10px 30px rgba(79, 172, 254, 0.4);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
            color: #333;
        }
        
        .btn-danger:hover {
            box-shadow: 0 10px 30px rgba(255, 154, 158, 0.4);
        }
        
        .feedback-area {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 15px;
            padding: 25px;
            margin-top: 25px;
            white-space: pre-wrap;
            font-family: 'Inter', monospace;
            font-size: 15px;
            line-height: 1.7;
            border-left: 5px solid #667eea;
            position: relative;
            min-height: 100px;
        }
        
        .feedback-area::before {
            content: '💡';
            position: absolute;
            top: 15px;
            right: 15px;
            font-size: 1.5rem;
            opacity: 0.6;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #667eea;
            font-size: 1.1rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 15px;
        }
        
        .loading i {
            font-size: 2rem;
            animation: spin 2s linear infinite;
        }
        
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        .history-item {
            background: linear-gradient(135deg, #f8f9ff 0%, #e8f2ff 100%);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
            transition: transform 0.2s ease;
            position: relative;
        }
        
        .history-item:hover {
            transform: translateX(5px);
        }
        
        .history-type {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin-right: 15px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .type-text {
            background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
            color: white;
        }
        
        .type-code {
            background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
            color: white;
        }
        
        .history-time {
            font-size: 13px;
            color: #7f8c8d;
            margin-top: 10px;
            font-weight: 500;
        }
        
        .history-content {
            margin-top: 12px;
            font-family: 'Inter', monospace;
            font-size: 14px;
            color: #2c3e50;
            line-height: 1.6;
            background: rgba(255,255,255,0.7);
            padding: 10px;
            border-radius: 8px;
            border: 1px solid rgba(0,0,0,0.05);
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: scale(1.05);
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 1rem;
            opacity: 0.9;
            font-weight: 500;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(255,255,255,0.2);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 15px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4facfe, #00f2fe);
            border-radius: 4px;
            transition: width 0.3s ease;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2.2rem;
            }
            .card {
                padding: 20px;
            }
            .button-group {
                flex-direction: column;
            }
            button {
                width: 100%;
                justify-content: center;
            }
            .dashboard-grid {
                grid-template-columns: 1fr;
                gap: 20px;
            }
            .main-input-section,
            .stats-section,
            .analysis-section {
                grid-column: 1;
            }
            .stats-section {
                order: -1; /* Show stats first on mobile */
            }
        }
        
        @media (max-width: 480px) {
            .header h1 {
                font-size: 1.8rem;
            }
            .header p {
                font-size: 1rem;
            }
            .card h2 {
                font-size: 1.5rem;
            }
            .container {
                padding: 15px;
                gap: 20px;
            }
        }
        
        .notification {
            font-family: 'Inter', sans-serif;
        }
        
        @keyframes slideInRight {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slideOutRight {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
        
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none !important;
        }
        
        .detection-result {
            margin-top: 10px;
            padding: 8px 12px;
            background: rgba(255,255,255,0.9);
            border-radius: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            color: #2c3e50;
            border: 1px solid rgba(102, 126, 234, 0.2);
        }
        
        .confidence-badge {
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .confidence-high {
            background: linear-gradient(135deg, #4caf50, #45a049);
            color: white;
        }
        
        .confidence-medium {
            background: linear-gradient(135deg, #ff9800, #f57c00);
            color: white;
        }
        
        .confidence-low {
            background: linear-gradient(135deg, #f44336, #d32f2f);
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-brain"></i> Cognitive Pattern Tracking AI</h1>
            <p>Analyze your thinking patterns and get actionable feedback</p>
            <p class="subtitle">Enhance your learning journey with AI-powered insights</p>
        </div>
        
        <div class="dashboard-grid">
            <div class="card main-input-section">
                <h2><i class="fas fa-edit"></i> Submit Your Input</h2>
                <div class="form-group">
                    <label for="inputType"><i class="fas fa-tag"></i> Input Type:</label>
                    <select id="inputType">
                        <option value="auto">🤖 Auto-Detect</option>
                        <option value="text">💬 Text / Question</option>
                        <option value="code">💻 Code</option>
                    </select>
                    <div id="detectionResult" class="detection-result" style="display: none;">
                        <i class="fas fa-robot"></i>
                        <span id="detectionText">Analyzing...</span>
                        <span id="confidenceBadge" class="confidence-badge"></span>
                    </div>
                </div>
                <div class="form-group">
                    <label for="content"><i class="fas fa-keyboard"></i> Your Input:</label>
                    <textarea id="content" rows="6" placeholder="Enter your text, question, or code here... Share your thoughts and get cognitive insights!"></textarea>
                </div>
                <div class="button-group">
                    <button id="submitBtn"><i class="fas fa-paper-plane"></i> Submit Input</button>
                    <button id="getFeedbackBtn" class="btn-secondary"><i class="fas fa-chart-line"></i> Get Cognitive Feedback</button>
                </div>
            </div>
            
            <div class="card stats-section">
                <h2><i class="fas fa-chart-pie"></i> Learning Statistics</h2>
                <div id="statsContainer">
                    <div class="stat-card">
                        <div class="stat-number" id="totalInputs">0</div>
                        <div class="stat-label">Total Inputs</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="recentActivity">0</div>
                        <div class="stat-label">This Week</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="textInputs">0</div>
                        <div class="stat-label">Text Inputs</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="codeInputs">0</div>
                        <div class="stat-label">Code Inputs</div>
                    </div>
                </div>
            </div>
            
            <div class="card analysis-section">
                <h2><i class="fas fa-chart-bar"></i> Analysis & Feedback</h2>
                <div class="button-group" style="margin-bottom: 20px;">
                    <button id="getHistoryBtn"><i class="fas fa-history"></i> View History</button>
                    <button id="clearHistoryBtn" class="btn-danger"><i class="fas fa-trash-alt"></i> Clear History</button>
                </div>
                <div id="feedback" class="feedback-area">
                    <i class="fas fa-lightbulb"></i> Click "Get Cognitive Feedback" to analyze your thinking patterns and receive personalized insights for improvement...
                </div>
            </div>
            
            <div class="card" id="historyCard" style="display: none; grid-column: 1 / 13; grid-row: 3;">
                <h2><i class="fas fa-list"></i> Input History</h2>
                <div id="historyList"></div>
            </div>
        </div>
    </div>
    
    <script>
        const API_BASE = '';
        
        async function loadStats() {
            try {
                const response = await fetch('/get_stats');
                const data = await response.json();
                
                document.getElementById('totalInputs').textContent = data.total_inputs;
                document.getElementById('recentActivity').textContent = data.recent_activity;
                
                const statCards = document.querySelectorAll('.stat-card');
                if (statCards.length >= 4) {
                    statCards[0].querySelector('.stat-number').textContent = data.total_inputs;
                    statCards[0].querySelector('.stat-label').textContent = 'Total Inputs';
                    
                    statCards[1].querySelector('.stat-number').textContent = data.recent_activity;
                    statCards[1].querySelector('.stat-label').textContent = 'This Week';
                    
                    statCards[2].querySelector('.stat-number').textContent = data.languages['text'] || 0;
                    statCards[2].querySelector('.stat-label').textContent = '💬 Text Inputs';
                    
                    statCards[3].querySelector('.stat-number').textContent = data.languages['code'] || 0;
                    statCards[3].querySelector('.stat-label').textContent = '💻 Code Inputs';
                }
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }
        
        async function analyzeContent(content) {
            if (!content.trim()) {
                document.getElementById('detectionResult').style.display = 'none';
                return;
            }
            
            const detectionResult = document.getElementById('detectionResult');
            const detectionText = document.getElementById('detectionText');
            const confidenceBadge = document.getElementById('confidenceBadge');
            
            detectionResult.style.display = 'flex';
            detectionText.textContent = 'Analyzing...';
            confidenceBadge.textContent = '';
            confidenceBadge.className = 'confidence-badge';
            
            try {
                const response = await fetch('/analyze_content', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ content: content }),
                });
                
                const data = await response.json();
                
                let displayText = '';
                let iconClass = '';
                
                if (data.detected_type === 'text') {
                    displayText = 'Detected: Text';
                    iconClass = 'fas fa-comment';
                } else {
                    displayText = 'Detected: Code';
                    iconClass = 'fas fa-code';
                }
                
                detectionText.innerHTML = `<i class="${iconClass}"></i> ${displayText}`;
                
                // Set confidence badge with better thresholds
                let confidenceClass = 'confidence-low';
                let confidenceLabel = '';
                
                if (data.confidence >= 0.8) {
                    confidenceClass = 'confidence-high';
                    confidenceLabel = 'Very High';
                } else if (data.confidence >= 0.6) {
                    confidenceClass = 'confidence-high';
                    confidenceLabel = 'High';
                } else if (data.confidence >= 0.4) {
                    confidenceClass = 'confidence-medium';
                    confidenceLabel = 'Medium';
                } else if (data.confidence >= 0.2) {
                    confidenceClass = 'confidence-low';
                    confidenceLabel = 'Low';
                } else {
                    confidenceClass = 'confidence-low';
                    confidenceLabel = 'Very Low';
                }
                
                confidenceBadge.textContent = `${confidenceLabel} (${Math.round(data.confidence * 100)}%)`;
                confidenceBadge.className = `confidence-badge ${confidenceClass}`;
                
                // Auto-select if confidence is high enough
                if (data.confidence > 0.5) {
                    document.getElementById('inputType').value = data.detected_type === 'text' ? 'text' : 'code';
                } else {
                    document.getElementById('inputType').value = 'auto';
                }
                
            } catch (error) {
                detectionText.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Analysis failed';
                confidenceBadge.textContent = '';
            }
        }
        
        async function submitInput() {
            const inputTypeSelect = document.getElementById('inputType');
            let inputType = inputTypeSelect.value;
            const content = document.getElementById('content').value;
            
            if (!content.trim()) {
                showNotification('Please enter some content to analyze!', 'warning');
                return;
            }
            
            // If auto-detect is selected, analyze the content first
            if (inputType === 'auto') {
                try {
                    const response = await fetch('/analyze_content', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ content: content }),
                    });
                    const data = await response.json();
                    
                    // Map detected language to input type
                    if (data.detected_type === 'text') {
                        inputType = 'text';
                    } else {
                        inputType = 'code';
                    }
                    
                    const detectedName = data.detected_type === 'text' ? 'Text' : 'Code';
                    showNotification(`Auto-detected as ${detectedName} (${Math.round(data.confidence * 100)}% confidence)`, 'info');
                } catch (error) {
                    inputType = 'text'; // fallback
                    showNotification('Could not auto-detect type, defaulting to text', 'warning');
                }
            }
            
            const submitBtn = document.getElementById('submitBtn');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
            submitBtn.disabled = true;
            
            try {
                const response = await fetch('/submit_input', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ input_type: inputType, content: content }),
                });
                
                if (response.ok) {
                    showNotification('Input submitted successfully! Ready for analysis.', 'success');
                    document.getElementById('content').value = '';
                    document.getElementById('detectionResult').style.display = 'none';
                    loadStats(); // Refresh stats after submission
                } else {
                    showNotification('Error submitting input. Please try again.', 'error');
                }
            } catch (error) {
                showNotification('Network error: ' + error.message, 'error');
            } finally {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        }
        
        function showNotification(message, type) {
            // Create notification element
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.innerHTML = `
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-triangle' : type === 'error' ? 'times-circle' : 'info-circle'}"></i>
                ${message}
            `;
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: ${type === 'success' ? '#4caf50' : type === 'warning' ? '#ff9800' : type === 'error' ? '#f44336' : '#2196f3'};
                color: white;
                padding: 15px 20px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                z-index: 1000;
                font-weight: 500;
                animation: slideInRight 0.3s ease;
                display: flex;
                align-items: center;
                gap: 10px;
            `;
            
            document.body.appendChild(notification);
            
            // Remove after 3 seconds
            setTimeout(() => {
                notification.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        }
        
        async function getFeedback() {
            const feedbackDiv = document.getElementById('feedback');
            feedbackDiv.innerHTML = `
                <div class="loading">
                    <i class="fas fa-cog"></i>
                    Analyzing your cognitive patterns...
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 0%"></div>
                    </div>
                </div>
            `;
            
            // Animate progress bar
            const progressFill = feedbackDiv.querySelector('.progress-fill');
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress > 90) progress = 90;
                progressFill.style.width = progress + '%';
            }, 200);
            
            try {
                const response = await fetch('/get_feedback');
                const data = await response.json();
                clearInterval(interval);
                progressFill.style.width = '100%';
                setTimeout(() => {
                    feedbackDiv.innerHTML = `<i class="fas fa-lightbulb"></i> ${data.feedback || 'No feedback available'}`;
                }, 500);
            } catch (error) {
                clearInterval(interval);
                feedbackDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> Error getting feedback: ${error.message}`;
            }
        }
        
        async function getHistory() {
            const historyCard = document.getElementById('historyCard');
            const historyList = document.getElementById('historyList');
            
            historyList.innerHTML = `
                <div class="loading">
                    <i class="fas fa-spinner"></i>
                    Loading your learning history...
                </div>
            `;
            historyCard.style.display = 'block';
            
            try {
                const response = await fetch('/get_history');
                const data = await response.json();
                
                if (data.history && data.history.length > 0) {
                    historyList.innerHTML = data.history.map(item => {
                        const isText = item.input_type === 'text';
                        const emoji = isText ? '💬' : '💻';
                        const typeName = isText ? 'Text' : 'Code';
                        
                        return `
                        <div class="history-item">
                            <span class="history-type type-${isText ? 'text' : 'code'}">
                                <i class="fas fa-${isText ? 'comment' : 'code'}"></i>
                                ${emoji} ${typeName}
                            </span>
                            <span class="history-time"><i class="fas fa-clock"></i> ${new Date(item.timestamp).toLocaleString()}</span>
                            <div class="history-content">${escapeHtml(item.content.substring(0, 200))}${item.content.length > 200 ? '...' : ''}</div>
                        </div>
                    `}).join('');
                } else {
                    historyList.innerHTML = '<div style="text-align: center; padding: 40px; color: #7f8c8d;"><i class="fas fa-inbox" style="font-size: 3rem; margin-bottom: 15px;"></i><p>No history yet. Submit some inputs first to start your learning journey!</p></div>';
                }
            } catch (error) {
                historyList.innerHTML = `<div style="text-align: center; padding: 40px; color: #e74c3c;"><i class="fas fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 15px;"></i><p>Error loading history: ${error.message}</p></div>`;
            }
        }
        
        async function clearHistory() {
            if (confirm('⚠️ Are you sure you want to clear all history? This action cannot be undone and will permanently delete all your learning data.')) {
                const clearBtn = document.getElementById('clearHistoryBtn');
                const originalText = clearBtn.innerHTML;
                clearBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Clearing...';
                clearBtn.disabled = true;
                
                try {
                    const response = await fetch('/clear_history', { method: 'DELETE' });
                    if (response.ok) {
                        showNotification('History cleared successfully!', 'success');
                        document.getElementById('historyCard').style.display = 'none';
                        loadStats(); // Refresh stats after clearing
                    } else {
                        showNotification('Error clearing history. Please try again.', 'error');
                    }
                } catch (error) {
                    showNotification('Network error: ' + error.message, 'error');
                } finally {
                    clearBtn.innerHTML = originalText;
                    clearBtn.disabled = false;
                }
            }
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        document.getElementById('submitBtn').addEventListener('click', submitInput);
        document.getElementById('getFeedbackBtn').addEventListener('click', getFeedback);
        document.getElementById('getHistoryBtn').addEventListener('click', getHistory);
        document.getElementById('clearHistoryBtn').addEventListener('click', clearHistory);
        
        // Load stats on page load
        loadStats();
        
        // Content analysis with debouncing
        let analysisTimeout;
        document.getElementById('content').addEventListener('input', (e) => {
            clearTimeout(analysisTimeout);
            const content = e.target.value;
            
            if (content.length > 10) { // Only analyze after 10 characters
                analysisTimeout = setTimeout(() => {
                    analyzeContent(content);
                }, 500); // 500ms debounce
            } else {
                document.getElementById('detectionResult').style.display = 'none';
            }
        });
        
        // Submit on Ctrl+Enter
        document.getElementById('content').addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                submitInput();
            }
        });
    </script>
</body>
</html>
"""

@app.get("/")
async def serve_frontend():
    """Serve the frontend HTML"""
    return HTMLResponse(content=FRONTEND_HTML)

# ==================== MAIN ENTRY POINT ====================
def main():
    """Start the Cognitive Pattern Tracking AI System"""
    print("=" * 60)
    print("Cognitive Pattern Tracking AI System")
    print("=" * 60)
    
    # Initialize database
    init_database()
    print("[+] Database initialized")
    
    # Check API key
    if GOOGLE_API_KEY == "YOUR_GOOGLE_API_KEY_HERE":
        print("\n[!] WARNING: Google API key not configured!")
        print("   Set your API key by either:")
        print("   1. Setting environment variable: GOOGLE_API_KEY")
        print("   2. Editing the GOOGLE_API_KEY variable in the script")
        print("\n   The AI analysis will not work until you configure this.")
    else:
        print("[+] Google API key configured")
    
    print("\n" + "=" * 60)
    print("Starting servers...")
    print("=" * 60)
    print("\nOpen your browser and go to: http://localhost:8000")
    print("Press Ctrl+C to stop the server\n")
    
    # Open browser automatically
    webbrowser.open("http://localhost:8000")
    
    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
