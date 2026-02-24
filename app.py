from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import sqlite3
import hashlib
import os
import numpy as np
from keras.models import load_model
from keras.preprocessing import image as keras_image
from PIL import Image
import io
import base64
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
CORS(app)

# Database setup
DATABASE = 'users.db'
MODEL_PATH = 'final_xception_diabetic_retinopathy.h5'
IMG_SIZE = 229

# Class labels for diabetic retinopathy
CLASS_LABELS = {
    0: 'No DR',
    1: 'Mild',
    2: 'Moderate',
    3: 'Severe',
    4: 'Proliferative DR'
}

# Load model
try:
    model = load_model(MODEL_PATH)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

def init_db():
    """Initialize the database"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            prediction TEXT,
            confidence REAL,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'error': 'All fields are required'}), 400
        
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Check if user already exists
        c.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
        if c.fetchone():
            conn.close()
            return jsonify({'error': 'Username or email already exists'}), 400
        
        # Insert new user
        hashed_pw = hash_password(password)
        c.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                  (username, email, hashed_pw))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        
        # Auto login after registration
        session['user_id'] = user_id
        session['username'] = username
        
        return jsonify({'message': 'Registration successful', 'username': username}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({'error': 'All fields are required'}), 400
        
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        hashed_pw = hash_password(password)
        c.execute('SELECT id, username FROM users WHERE username = ? AND password = ?',
                  (username, hashed_pw))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return jsonify({'message': 'Login successful', 'username': user[1]}), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/check-auth')
def check_auth():
    """Check if user is authenticated"""
    if 'user_id' in session:
        return jsonify({'authenticated': True, 'username': session.get('username')}), 200
    return jsonify({'authenticated': False}), 200

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    """Make prediction on uploaded image"""
    try:
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        # Read and preprocess image
        img = Image.open(file.stream).convert('RGB')
        img = img.resize((IMG_SIZE, IMG_SIZE))
        img_array = keras_image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0  # Normalize
        
        # Make prediction
        predictions = model.predict(img_array)
        predicted_class = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class])
        
        # Get all class probabilities
        all_predictions = {
            CLASS_LABELS[i]: float(predictions[0][i]) * 100
            for i in range(len(CLASS_LABELS))
        }
        
        # Save prediction to database
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO predictions (user_id, prediction, confidence)
            VALUES (?, ?, ?)
        ''', (session['user_id'], CLASS_LABELS[predicted_class], confidence))
        conn.commit()
        conn.close()
        
        return jsonify({
            'prediction': CLASS_LABELS[predicted_class.item() if hasattr(predicted_class, 'item') else predicted_class],
            'confidence': float(confidence) * 100,
            'all_predictions': all_predictions,
            'severity_level': int(predicted_class.item() if hasattr(predicted_class, 'item') else predicted_class)
        }), 200
    
    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/history')
@login_required
def history():
    """Get user's prediction history"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            SELECT prediction, confidence, created_at
            FROM predictions
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 10
        ''', (session['user_id'],))
        
        predictions = c.fetchall()
        conn.close()
        
        history_data = [
            {
                'prediction': p[0],
                'confidence': p[1] * 100,
                'date': p[2]
            }
            for p in predictions
        ]
        
        return jsonify({'history': history_data}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Create templates folder if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create static folder if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    
    app.run(debug=True, host='0.0.0.0', port=5000)
