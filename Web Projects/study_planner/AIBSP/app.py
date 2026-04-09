from flask import Flask, render_template, request, redirect, url_for, session, flash
import google.genai as genai
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from config import DB_CONFIG, SMTP_CONFIG, GEMINI_API_KEY, GEMINI_MODEL

app = Flask(__name__)
app.secret_key = os.urandom(24)

db_config = DB_CONFIG
smtp_config = SMTP_CONFIG

otp_storage = {}
SAVE_DATA = False # Set to True to enable database saving

# Initialize Gemini AI
genai.configure(api_key=GEMINI_API_KEY)  
model = genai.GenerativeModel(GEMINI_MODEL)

def get_db_connection():
    conn = sqlite3.connect('student.db')
    conn.row_factory = sqlite3.Row
    return conn

def send_otp_email(email, otp):
    try:
        # Render the HTML template
        email_html = render_template('otp_email.html', otp=otp)
        msg = MIMEMultipart()
        msg['From'] = smtp_config['username']
        msg['To'] = email
        msg['Subject'] = 'ScriptSeekers Academy - Registration OTP'
        # Attach HTML content
        msg.attach(MIMEText(email_html, 'html'))
        server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
        server.starttls()
        server.login(smtp_config['username'], smtp_config['password'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Create study_plans table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            subjects TEXT NOT NULL,
            hours_per_day INTEGER NOT NULL,
            study_style TEXT NOT NULL,
            time_slots TEXT NOT NULL,
            short_term_goal TEXT NOT NULL,
            long_term_goal TEXT NOT NULL,
            study_plan TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Check if it's an OTP verification request
        if 'verify_otp' in request.form:
            email = request.form['email']
            otp_attempt = request.form['otp']
            # Check if OTP exists and is valid
            if email in otp_storage:
                stored_otp, expiry_time = otp_storage[email]
                if time.time() > expiry_time:
                    flash('OTP has expired. Please request a new one.', 'error')
                    return render_template('register.html', email=email, show_otp_field=True)
                if otp_attempt == stored_otp:
                    # OTP is correct, proceed with registration
                    username = request.form['username']
                    password = request.form['password']
                    confirm_password = request.form['confirm_password']
                    if password != confirm_password:
                        flash('Passwords do not match!', 'error')
                        return render_template('register.html', email=email, show_otp_field=True)
                    try:
                        if SAVE_DATA:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            # Check if username or email already exists
                            cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
                            if cursor.fetchone():
                                flash('Username or email already exists!', 'error')
                                return render_template('register.html', email=email, show_otp_field=True)
                            # Insert new user
                            password_hash = generate_password_hash(password)
                            cursor.execute(
                                "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                                (username, password_hash, email)
                            )
                            conn.commit()
                            cursor.close()
                            conn.close()
                            flash('Registration successful! Please log in.', 'success')
                        else:
                            flash('Registration successful! (Database saving is currently disabled)', 'info')
                        
                        # Remove OTP from storage after successful registration
                        if email in otp_storage:
                            del otp_storage[email]
                        return redirect(url_for('login'))
                    except sqlite3.Error as err:
                        flash(f'Database error: {err}', 'error')
                        return render_template('register.html', email=email, show_otp_field=True)
                    finally:
                        pass
                else:
                    flash('Invalid OTP. Please try again.', 'error')
                    return render_template('register.html', email=email, show_otp_field=True)
            else:
                flash('No OTP found for this email. Please request a new one.', 'error')
                return render_template('register.html')
        # Handle OTP request
        elif 'request_otp' in request.form:
            email = request.form['email']
            username = request.form['username']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            # Basic validation
            if not all([username, email, password, confirm_password]):
                flash('All fields are required!', 'error')
                return render_template('register.html')
            if password != confirm_password:
                flash('Passwords do not match!', 'error')
                return render_template('register.html')
            # Check if user already exists
            try:
                if SAVE_DATA:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
                    if cursor.fetchone():
                        flash('Username or email already exists!', 'error')
                        return render_template('register.html')
                    cursor.close()
                    conn.close()
            except sqlite3.Error as err:
                flash(f'Database error: {err}', 'error')
                return render_template('register.html')
            # Generate and send OTP
            otp = str(random.randint(100000, 999999))
            expiry_time = time.time() + 600  # 10 minutes from now
            # Store OTP with expiry time
            otp_storage[email] = (otp, expiry_time)
            # Send OTP via email
            if send_otp_email(email, otp):
                flash('OTP sent to your email. Please check your inbox.', 'success')
                return render_template('register.html', 
                                     email=email, 
                                     username=username,
                                     password=password,
                                     confirm_password=confirm_password,
                                     show_otp_field=True)
            else:
                flash('Failed to send OTP. Please try again.', 'error')
                return render_template('register.html')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            if SAVE_DATA:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
                user = cursor.fetchone()
                if user and check_password_hash(user['password_hash'], password):
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    flash('Login successful!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid username or password!', 'error')
            else:
                # Bypass login if saving is disabled
                session['user_id'] = 1  # Dummy ID
                session['username'] = username
                flash('Login successful! (Guest Mode Enabled)', 'success')
                return redirect(url_for('dashboard'))
            
        except sqlite3.Error as err:
            flash(f'Database error: {err}', 'error')
        finally:
            pass
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        user_input = request.form.to_dict(flat=True)
        # Validate study hours
        try:
            hours = int(user_input['hours_per_day'])
            if hours < 1 or hours > 24:
                flash('Please enter valid study hours (1-24)', 'error')
                return render_template('dashboard.html')
        except ValueError:
            flash('Please enter a valid number for study hours', 'error')
            return render_template('dashboard.html')
        prompt = f"""
        Generate a weekly personalized study plan for a student with:
        Name: {user_input['name']},
        Age: {user_input['age']},
        Subjects: {user_input['subjects']},
        Study Hours per Day: {user_input['hours_per_day']},
        Study Style: {user_input['study_style']},
        Time Slots: {user_input['time_slots']},
        Short Term Goal: {user_input['short_term_goal']},
        Long Term Goal: {user_input['long_term_goal']}.
        Make the schedule visually structured and motivating. Note* Don't make any table format, just a simple text output. 
        IMPORTANT: Start each day with the day name followed by a colon (e.g., "Monday:").
        Provide a detailed plan for each day of the week, including specific tasks and study techniques.
        """
        try:
            response = model.generate_content(prompt)
            plan = response.text
            
            if SAVE_DATA:
                # Save to database
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO study_plans 
                    (user_id, name, age, subjects, hours_per_day, study_style, time_slots, short_term_goal, long_term_goal, study_plan)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session['user_id'], 
                    user_input['name'], 
                    user_input['age'], 
                    user_input['subjects'], 
                    user_input['hours_per_day'], 
                    user_input['study_style'], 
                    user_input['time_slots'], 
                    user_input['short_term_goal'], 
                    user_input['long_term_goal'], 
                    plan
                ))
                conn.commit()
                cursor.close()
                conn.close()
            
            return render_template('result.html', plan=plan)
        except Exception as e:
            flash(f'Error generating study plan: {str(e)}', 'error')
            return render_template('dashboard.html')
    return render_template('dashboard.html')

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    try:
        if SAVE_DATA:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, subjects, created_at 
                FROM study_plans 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            ''', (session['user_id'],))
            plans = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template('history.html', plans=plans)
        else:
            flash('History feature is currently disabled.', 'info')
            return redirect(url_for('dashboard'))
    except sqlite3.Error as err:
        flash(f'Database error: {err}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/plan/<int:plan_id>')
def view_plan(plan_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM study_plans 
            WHERE id = ? AND user_id = ?
        ''', (plan_id, session['user_id']))
        plan = cursor.fetchone()
        cursor.close()
        conn.close()
        if plan:
            return render_template('result.html', plan=plan['study_plan'])
        else:
            flash('Study plan not found!', 'error')
            return redirect(url_for('history'))        
    except sqlite3.Error as err:
        flash(f'Database error: {err}', 'error')
        return redirect(url_for('history'))
    
@app.route('/delete_plan/<int:plan_id>')
def delete_plan(plan_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if the plan belongs to the current user
        cursor.execute('''
            DELETE FROM study_plans 
            WHERE id = ? AND user_id = ?
        ''', (plan_id, session['user_id']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Study plan deleted successfully!', 'success')
        return redirect(url_for('history'))
            
    except sqlite3.Error as err:
        flash(f'Database error: {err}', 'error')
        return redirect(url_for('history'))

if __name__ == '__main__':
    if SAVE_DATA:
        init_db()
    app.run(debug=True)