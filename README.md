Diabetic Retinopathy Detection System

This is a full stack web application designed to detect diabetic retinopathy using a deep learning model based on the Xception CNN architecture.
Demo video https://drive.google.com/file/d/1t1KvHLfxdayL1GEk1MFNDCrVzlGT6B80/view?usp=drive_link
Features

User Authentication
Secure registration and login functionality integrated with a SQLite database.

AI Powered Detection
Utilizes an advanced Xception CNN model to identify diabetic retinopathy from retinal images.

Real time Analysis
Users can upload retinal images and receive immediate prediction results.

Prediction History
Allows users to view and track all previous diagnoses.

Modern User Interface
Responsive and visually appealing design built with Tailwind CSS.

Security
Implements password hashing and proper session management for secure access.

Tech Stack

Frontend
HTML5
Tailwind CSS
Vanilla JavaScript

Backend
Flask Python web framework
SQLite database
TensorFlow and Keras for deep learning
Download trained model https://drive.google.com/file/d/182wYIX10HAUaNOb74iazLF3IwHyjWiuP/view?usp=drive_link

Installation

Prerequisites
Python 3.8 or above
pip

Steps

1 Install Dependencies

pip install -r requirements.txt

2 Ensure Model File Exists
Confirm that final_xception_diabetic_retinopathy.h5 is available in the root directory of the project.

3 Run the Application

python app.py

4 Access the Application
Open your browser and go to

http://localhost:5000

Project Structure

diabities_clg

app.py Flask backend
cnn.py Model training script
requirements.txt Python dependencies
users.db SQLite database created automatically
final_xception_diabetic_retinopathy.h5 Trained model

templates
index.html Main frontend page

static
app.js Frontend JavaScript

Usage

1 Register or Login
Create a new account or sign in using existing credentials.
All passwords are securely hashed before storage.

2 Upload Image
Select the upload section.
Choose a retinal fundus image in PNG or JPG format.
A preview of the image will be displayed.

3 Analyze
Click on the Analyze Image button.
The AI model will process the image and generate results.
The output will include the diagnosis along with confidence levels.

4 View History
Access all your previous predictions.
Review prediction dates and confidence scores.

Diabetic Retinopathy Levels

The system classifies diabetic retinopathy into five stages.

No DR 0
No signs of diabetic retinopathy.

Mild 1
Mild non proliferative diabetic retinopathy.

Moderate 2
Moderate non proliferative diabetic retinopathy.

Severe 3
Severe non proliferative diabetic retinopathy.

Proliferative DR 4
Proliferative diabetic retinopathy.

Model Information

Architecture
Xception CNN

Input Size
229 by 229 pixels

Training Dataset
Diabetic Retinopathy Level Detection dataset from Kaggle

Classes
Five classes including No DR, Mild, Moderate, Severe, and Proliferative

Security Features

Passwords are hashed using SHA 256.
Authentication is managed through user sessions.
Login is required before accessing prediction features.
CORS is enabled to enhance API security.

API Endpoints

GET / Main page
POST /register User registration
POST /login User login
POST /logout User logout
GET /check-auth Check authentication status
POST /predict Image prediction requires authentication
GET /history Retrieve prediction history requires authentication

Note

Important
This application is an AI based diagnostic support tool and is not a substitute for professional medical advice. Always consult a qualified healthcare professional for accurate diagnosis and treatment.

License

This project is created for educational purposes.

Author

Developed as a college project.