# 🏥 AI Powered Hospital Management System

<p align="center">

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black?logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-Database-blue?logo=mysql)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple?logo=bootstrap)
![Machine Learning](https://img.shields.io/badge/Machine-Learning-green)
![Google Gemini AI](https://img.shields.io/badge/Google-Gemini%20AI-orange)

</p>

---

# 📌 Project Overview

AI Powered Hospital Management System is a web-based application developed using **Python Flask**, **MySQL**, **Machine Learning**, and **Google Gemini AI**.

The system digitizes hospital operations by managing patients, doctors, staff, appointments, pharmacy, billing, bed allocation, and intelligent AI reports.

It also provides predictive healthcare features using Machine Learning models and AI-powered analytics using Google Gemini.

---

# ✨ Features

## 🔐 Authentication

- Secure Login System
- Session Management
- Admin Access
- Reception Access

---

## 👨‍⚕️ Patient Management

- Register Patient
- Edit Patient
- Delete Patient
- Search Patient
- View Patient Details

---

## 🩺 Doctor Management

- Add Doctor
- Update Doctor
- Delete Doctor
- Doctor Productivity Report
- AI Performance Analysis

---

## 👨‍💼 Staff Management

- Add Staff
- Update Staff
- Delete Staff

---

## 📅 Appointment Management

- Book Appointment
- View Appointments
- Search Appointment
- Edit Appointment
- Delete Appointment

---

## 🛏 Bed Management

- Add Bed
- Update Bed
- Delete Bed
- Available Bed Tracking
- Occupied Bed Monitoring

---

## 💊 Pharmacy Management

- Medicine Inventory
- Medicine Search
- Add Medicine
- Update Medicine
- Delete Medicine
- Low Stock Alert
- Expiry Monitoring

---

## 💰 Billing System

- Generate Bill
- PDF Bill Generation
- Payment Status
- Revenue Analytics

---

## 🤖 Artificial Intelligence Features

- AI Chatbot
- AI Disease Prediction
- AI Medical Report Generator
- AI Hospital Performance Report
- AI Department Performance Report
- AI Doctor Productivity Report
- AI Revenue Analysis
- AI Disease Statistics Report

---

## 🧠 Machine Learning Features

- Health Risk Prediction
- Disease Prediction

---

## 📊 Analytics Dashboard

- Dashboard Statistics
- Charts
- Notifications
- Reports

---

# 🛠 Technologies Used

### Backend

- Python
- Flask

### Frontend

- HTML5
- CSS3
- Bootstrap 5
- JavaScript

### Database

- MySQL

### AI

- Google Gemini API

### Machine Learning

- Scikit-Learn
- Pandas
- NumPy
- Joblib

### Visualization

- Chart.js
- Matplotlib

### PDF

- ReportLab

---

# 📂 Project Structure

```text
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
|   |   ├── layout.html
│   │   ├── login.html
│   │   ├── index.html
│   │   ├── patients.html
│   │   ├── register_patient.html
|   |   └── ... (other templates)
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
```

---

# ⚙ Installation Guide

## Step 1

Clone Repository

```bash
git clone https://github.com/yourusername/AI-Powered-Hospital-Management-System.git
```

---

## Step 2

Go to Project Folder

```bash
cd AI-Powered-Hospital-Management-System
```

---

## Step 3

Create Virtual Environment

```bash
python -m venv venv
```

---

## Step 4

Activate Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

---

## Step 5

Install Required Libraries

```bash
pip install -r requirements.txt
```

---

## Step 6

Configure Database

Open MySQL

Create Database

```sql
CREATE DATABASE hospital_db;
```

Import

```
hospital_db.sql
```

---

## Step 7

Configure Gemini API

Open **app.py**

Replace

```python
YOUR_GEMINI_API_KEY
```

with your own Google Gemini API Key.

---

## Step 8

Run Application

```bash
python app.py
```

---

## Step 9

Open Browser

```
http://127.0.0.1:5000
```

---

# 🔑 Default Login

## Admin

Username

```
admin
```

Password

```
admin123
```

---

## Reception

Username

```
reception
```

Password

```
recep123
```

---

# 📸 Screenshots

## 🔐 Login Page
![Login Page](https://github.com/Dhirajbhamburkar/AI-Powered-Hospital-Management-System/blob/main/Screenshots/Login%20Page.png)

## 🏠 Dashboard
![Dashboard](screenshots/dashboard.png)
- Dashboard
- Helth Risk Prediction
- AI Disease Prediction
- AI Chatbot
- Patient Management
- Doctor Management
- Staff Management
- Appointemt Management
- Pharmacy
- Bed Allocation Management
- Billing
- AI Reports

---

# 📦 Python Packages

- Flask
- mysql-connector-python
- google-generativeai
- pandas
- numpy
- scikit-learn
- joblib
- matplotlib
- reportlab

---

# 🚀 Future Improvements

- Email Notification
- SMS Notification
- Online Payment Gateway
- Face Recognition Login
- QR Code Patient ID
- Multi Hospital Support
- Cloud Deployment

---

# 👨‍💻 Developed By

**Dhiraj Bhamburkar**

---

# ⭐ If you like this project

Please consider giving this repository a ⭐ on GitHub.
