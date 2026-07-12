# AI Powered Hospital Management System

## Project Description

AI Powered Hospital Management System is a web-based application developed using Python Flask and MySQL. It helps hospitals manage patients, doctors, staff, appointments, billing, pharmacy, bed management, and AI-powered reports.

The project also integrates Google Gemini AI for intelligent disease prediction and hospital analytics.

---

## Folder structure

AI_Hospital_Management_System/
│
├── backend/
│   ├──── dataset/
│   │      └── health_dataset.csv
|   |
│   |── ml_models/
|   |     |
|   |     ├── health_prediction_model.pkl
|   |     ├── model.py
|   |     ├── patient_model.pkl
│   |     ├── patient_prediction_model.pkl
│   |     ├── train_health_model.py
│   |     └── train_model.py
│   │
│   ├── templates/
│   │   ├── layout.html
│   │   ├── login.html
│   │   ├── index.html
│   │   ├── patients.html
│   │   ├── register_patient.html
│   │   ├── patient_details.html
│   │   ├── edit_patient.html
│   │   ├── doctors.html
│   │   ├── add_staff.html
│   │   ├── staff.html
│   │   ├── appointments.html
│   │   ├── beds.html
│   │   ├── billing.html
│   │   ├── pharmacy.html
│   │   ├── chatbot.html
│   │   ├── disease_prediction.html
│   │   ├── health_prediction.html
│   │   ├── hospital_performance.html
│   │   ├── department_report.html
│   │   ├── doctor_productivity.html
│   │   ├── patient_admission_analytics.html
│   │   ├── disease_statistics.html
│   │   ├── revenue_analytics.html
│   │   ├── reports.html
│   │   └── ... (other templates)
│   │
|   |
│   ├── uploads/
│   │   ├── voice.webm
│   │   ├── AI_Medical_Report.pdf
│   │   └── bill_1.pdf
│   |
|   ├── app.py/
|   ├── requirements.txt
|   └── README.md
|
|
├── database/
│   └── hospital_db.sql
│
└── venv/
    ├── Include
    ├── Lib
    ├── Scripts
    ├── share
    ├── .gitgnore
    └── pyvenv.cfg


## Technologies Used

- Python
- Flask
- MySQL
- HTML
- CSS
- Bootstrap
- JavaScript
- Chart.js
- Google Gemini AI
- Scikit-learn
- Pandas
- NumPy

---

## Features

- Admin Login
- Patient Management
- Doctor Management
- Staff Management
- Appointment Management
- Billing System
- Bed Management
- Pharmacy Management
- AI Disease Prediction
- Health Risk Prediction
- AI Chatbot
- AI Medical Report Generator
- Hospital Performance Report
- Department Performance Report
- Doctor Productivity Report
- Revenue Analytics
- Disease Statistics Dashboard
- PDF Report Generation

---

## Database

Database Name: hospital_db

Database file: hospital_db.sql

---

## Default Login

Admin

Username: admin

Password: admin123

Reception

Username: reception

Password: recep123

---

## Developed By

Dhiraj Bhamburkar