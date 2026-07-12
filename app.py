from flask import Flask, render_template, request, jsonify, redirect, flash, session
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from flask import send_file
from faster_whisper import WhisperModel
import os
import traceback
import mysql.connector
import joblib
import google.generativeai as genai

model = joblib.load("ml_models/patient_prediction_model.pkl")
health_model = joblib.load("ml_models/health_prediction_model.pkl")
print(model.feature_names_in_)
app = Flask(__name__)
app.secret_key = "*******"

# Gemini AI Configuration
genai.configure(api_key="GEMINI_API_KEY")

gemini_model = genai.GenerativeModel("gemini-2.5-flash")

whisper_model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)

# MySQL Connection
db = mysql.connector.connect(
    host="*******",
    user="****",
    password="******",   
    database="hospital_db"
)

cursor = db.cursor()

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        cursor = db.cursor()

        cursor.execute("""
        SELECT
            user_id,
            username,
            full_name,
            role
        FROM users
        WHERE username=%s AND password=%s
        """, (username, password))

        user = cursor.fetchone()

        if user:

            session["user_id"] = user[0]
            session["username"] = user[1]
            session["full_name"] = user[2]
            session["role"] = user[3]

            return redirect("/dashboard")

        return render_template(
            "login.html",
            error="Invalid Username or Password"
        )

    return render_template("login.html")

#HOME
@app.route("/dashboard")
def home():

    print("session", dict(session))
    # Login check
    if "user_id" not in session:
        return redirect("/")

    # Total Patients
    cursor.execute("SELECT COUNT(*) FROM patients")
    total_patients = cursor.fetchone()[0]

    # Total Revenue
    cursor.execute("SELECT IFNULL(SUM(total_amount),0) FROM bills")
    total_revenue = cursor.fetchone()[0]

    # Total Bills
    cursor.execute("SELECT COUNT(*) FROM bills")
    total_bills = cursor.fetchone()[0]

    # Average Age
    cursor.execute("SELECT ROUND(AVG(age),1) FROM patients")
    average_age = cursor.fetchone()[0]

    if average_age is None:
        average_age = 0

    # Today's Admissions
    cursor.execute("SELECT COUNT(*) FROM patients WHERE admission_date = CURDATE()")
    daily_admissions = cursor.fetchone()[0]

    # Bed Details
    total_beds = 100
    occupied_beds = total_patients
    available_beds = total_beds - occupied_beds

    # Bed Occupancy Percentage
    occupancy_percentage = 0
    if total_beds > 0:
     occupancy_percentage = round((occupied_beds / total_beds) * 100)

    # AI Prediction
    next_day = [[total_patients + 1]]
    predicted_patients = round(model.predict(next_day)[0])

    # Department-wise Data
    cursor.execute("""
        SELECT department, COUNT(*)
        FROM patients
        GROUP BY department
    """)
    department_data = cursor.fetchall()

    department_labels = []
    department_values = []

    for row in department_data:
        department_labels.append(row[0])
        department_values.append(row[1])

    # Doctor-wise Patients
    cursor.execute("""
        SELECT
        d.doctor_name,
        COUNT(p.patient_id) AS total_patients
        FROM doctors d
        LEFT JOIN patients p
        ON d.doctor_id = p.doctor_id
        GROUP BY d.doctor_id, d.doctor_name
        ORDER BY d.doctor_name
        """)
    doctor_data = cursor.fetchall()

    doctor_labels = []
    doctor_values = []

    for row in doctor_data:
        doctor_labels.append(row[0])
        doctor_values.append(row[1])
        print("Doctor Data:", doctor_data)
        print("Doctor Labels:", doctor_labels)
        print("Doctor Values:", doctor_values)

    # Disease-wise Data
    cursor.execute("""
        SELECT disease, COUNT(*)
        FROM patients
        GROUP BY disease
    """)
    disease_data = cursor.fetchall()

    disease_labels = []
    disease_values = []

    for row in disease_data:
        disease_labels.append(row[0])
        disease_values.append(row[1])

    # Recent Patients
    cursor.execute("""
        SELECT
        p.patient_id,
        p.name,
        p.disease,
        d.doctor_name,
        p.admission_date
        FROM patients p
        LEFT JOIN doctors d
        ON p.doctor_id = d.doctor_id
        ORDER BY p.patient_id DESC
        LIMIT 5
        """)
    recent_patients = cursor.fetchall()
    
    # Today's Appointments
    cursor.execute("""
        SELECT
        p.name,
        d.doctor_name,
        a.appointment_time,
        a.status
        FROM appointments a
        JOIN patients p
        ON a.patient_id = p.patient_id
        JOIN doctors d
        ON a.doctor_id = d.doctor_id
        WHERE a.appointment_date = CURDATE()
        ORDER BY a.appointment_time
        LIMIT 5
        """)
    today_appointments = cursor.fetchall()

    # Notifications
    cursor.execute("""
        SELECT
        notification_id,
        message,
        type,
        created_at,
        status
        FROM notifications
        ORDER BY created_at DESC
        LIMIT 5
        """)

    notifications = cursor.fetchall()

    return render_template(
        "index.html",
        username=session["full_name"],
        current_date=datetime.now().strftime("%d-%m-%Y"),
        total_patients=total_patients,
        total_revenue=total_revenue,
        total_bills=total_bills,
        total_beds=total_beds,
        occupied_beds=occupied_beds,
        available_beds=available_beds,
        occupancy_percentage=occupancy_percentage,
        daily_admissions=daily_admissions,
        average_age=average_age,
        predicted_patients=predicted_patients,
        department_labels=department_labels,
        department_values=department_values,
        doctor_labels=doctor_labels,
        doctor_values=doctor_values,
        disease_labels=disease_labels,
        disease_values=disease_values,
        recent_patients=recent_patients,
        today_appointments=today_appointments,
        notifications=notifications,
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

@app.route("/chatbot")
def chatbot():

    return render_template("chatbot.html")

from flask import jsonify

@app.route("/ask_ai", methods=["POST"])
def ask_ai():

    user_message = request.form["message"]
    message = user_message.lower()


# Project Module Answers

    if "billing" in message and ("explain" in message or "what is" in message):

        return jsonify({
        "reply": """📄 Billing Module

        • Generate patient bills
        • Calculate treatment charges
        • Store payment records
        • Print billing reports"""
    })


    if "patient" in message and ("explain" in message or "what is" in message):

        return jsonify({
        "reply": """👨‍⚕️ Patient Management

        • Register new patients
        • Update patient details
        • Search patient records
        • Manage admission information"""
    })


    if "doctor" in message and ("explain" in message or "what is" in message):

        return jsonify({
        "reply": """🩺 Doctor Management

        • Add doctors
        • Update doctor information
        • Assign departments
        • Manage doctor records"""
    })


    if "appointment" in message and ("explain" in message or "what is" in message):

        return jsonify({
        "reply": """📅 Appointment Management

        • Book appointments
        • Assign doctors
        • View appointment schedule
        • Manage patient visits"""
    })


    if "staff" in message and ("explain" in message or "what is" in message):

        return jsonify({
        "reply": """👨‍💼 Staff Management

        • Add staff members
        • Edit staff details
        • Search staff records
        • Delete staff records"""
    })


    if "pharmacy" in message and ("explain" in message or "what is" in message):

        return jsonify({
        "reply": """💊 Pharmacy Management

        • Add medicines
        • Update medicine stock
        • Search medicines
        • Manage pharmacy inventory"""
    })


    if "bed" in message and ("explain" in message or "what is" in message):

        return jsonify({
        "reply": """🛏️ Bed Allocation

        • Allocate beds
        • View available beds
        • Track occupied beds
        • Manage departments"""
    })

    cursor = db.cursor()

    # Total Patients
    if "total patient" in message or "how many patients" in message:

        cursor.execute("SELECT COUNT(*) FROM patients")
        total = cursor.fetchone()[0]

        return jsonify({
        "reply": f"There are currently {total} registered patients."
    })

    # Total Doctors
    if "total doctor" in message or "how many doctors" in message:

        cursor.execute("SELECT COUNT(*) FROM doctors")
        total = cursor.fetchone()[0]

        return jsonify({
        "reply": f"There are currently {total} doctors in the hospital."
    })

    # Total Staff
    if "total staff" in message or "how many staff" in message:

        cursor.execute("SELECT COUNT(*) FROM staff")
        total = cursor.fetchone()[0]

        return jsonify({
        "reply": f"There are currently {total} staff members."
    })

    # Total Beds
    if "total beds" in message:

        cursor.execute("SELECT SUM(total_beds) FROM beds")
        total = cursor.fetchone()[0] or 0

        return jsonify({
        "reply": f"The hospital has {total} total beds."
    })

    # Available Beds
    if "available beds" in message:

        cursor.execute("""
        SELECT
        SUM(total_beds - occupied_beds)
        FROM beds
        """)

        available = cursor.fetchone()[0] or 0

        return jsonify({
        "reply": f"There are {available} beds currently available."
    })
    prompt = f"""
        You are the AI Assistant for City Care Hospital Management System.

        You can answer two types of questions:

        1. Questions about this Hospital Management System
            (Patients, Doctors, Staff, Billing, Pharmacy, Beds, Reports, Appointments).

        2. General medical and healthcare questions
            (Diseases, Symptoms, Medicines, First Aid, Medical Tests, Health Tips).

        Rules:
            - Keep answers short (3–6 lines).
            - Use simple English.
            - For project/module questions, answer according to this software.
            - For medical questions, provide general educational information only.
            - Never prescribe medicines or give emergency medical advice.
            - If asked about politics, coding, movies, sports, etc., reply:
            "I can assist with hospital management and general medical information only."

        User Question:
            {user_message}
        """
    try:
        print("Using model:", gemini_model.model_name)
        print("Sending request...")
        print("User Question:", user_message)

        response = gemini_model.generate_content(prompt)

        print("Gemini Response:", response.text)

        return jsonify({
            "reply": response.text
        })

    except Exception as e:

        import traceback

        print("========== GEMINI ERROR ==========")
        traceback.print_exc()
        print("==================================")

        return jsonify({
            "reply": f"AI Error: {str(e)}"
        })

from werkzeug.utils import secure_filename

@app.route("/upload_voice", methods=["POST"])
def upload_voice():

    if "audio" not in request.files:
        return jsonify({"success": False})

    audio = request.files["audio"]

    os.makedirs("uploads", exist_ok=True)

    filepath = os.path.join("uploads", "voice.webm")

    audio.save(filepath)

    if os.path.getsize(filepath) < 1000:
        return jsonify({
        "success": False,
        "text": ""
    })

    try:
        segments, info = whisper_model.transcribe(
            filepath,
            beam_size=5
        )

        text = ""

        for segment in segments:
            text += segment.text + " "

    except Exception as e:
        print("Whisper Error:", e)
            
    
        return jsonify({
            "success": False,
            "text": ""
        })
    
@app.route("/health_prediction")
def health_prediction():

    return render_template("health_prediction.html")

@app.route("/predict_health", methods=["POST"])
def predict_health():

    age = float(request.form["age"])
    gender = float(request.form["gender"])
    height = float(request.form["height"])
    weight = float(request.form["weight"])
    bp = float(request.form["bp"])
    sugar = float(request.form["sugar"])
    heart_rate = float(request.form["heart_rate"])
    smoking = float(request.form["smoking"])
    alcohol = float(request.form["alcohol"])
    exercise = float(request.form["exercise"])

    prediction = health_model.predict([[
        age,
        gender,
        height,
        weight,
        bp,
        sugar,
        heart_rate,
        smoking,
        alcohol,
        exercise
    ]])

    score = max(0, min(100, int(prediction[0])))

    if score < 35:
        risk = "🟢 Low Risk"
        color = "success"

    elif score < 70:
        risk = "🟡 Moderate Risk"
        color = "warning"

    else:
        risk = "🔴 High Risk"
        color = "danger"

    prompt = f"""
    You are a health assistant.

    Patient Details:

    Age: {age}
    Height: {height} cm
    Weight: {weight} kg
    Blood Pressure: {bp}
    Blood Sugar: {sugar}
    Heart Rate: {heart_rate}
    Smoking: {"Yes" if smoking else "No"}
    Alcohol: {"Yes" if alcohol else "No"}
    Exercise Level: {exercise}

    Risk Score: {score}

    Give:

    1. Health Summary (2 lines)

    2. Five health tips.

    Keep answer simple.
    """

    try:

        response = gemini_model.generate_content(prompt)

        advice = response.text

    except:

        advice = """
    • Eat healthy food
    • Walk 30 minutes daily
    • Drink enough water
    • Sleep 7-8 hours
    • Visit doctor regularly
    """

    return jsonify({

        "risk": risk,
        "score": score,
        "color": color,
        "advice": advice

    })

@app.route("/reports")
def reports():

    return render_template("reports.html")

@app.route("/hospital_performance")
def hospital_performance():

    return render_template("hospital_performance.html")

@app.route("/department_report")
def department_report():

    return render_template("department_report.html")

@app.route("/doctor_productivity")
def doctor_productivity():

    return render_template("doctor_productivity.html")

@app.route("/patient_admission_analytics")
def patient_admission_analytics():

    return render_template("patient_admission_analytics.html")

@app.route("/generate_patient_admission_report")
def generate_patient_admission_report():

    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM patients")
    total_patients = cursor.fetchone()[0]

    cursor.execute("""
        SELECT MONTHNAME(admission_date) AS month,
               COUNT(*) AS total
        FROM patients
        GROUP BY MONTH(admission_date), MONTHNAME(admission_date)
        ORDER BY MONTH(admission_date)
    """)

    data = cursor.fetchall()

    labels = []
    values = []

    for month, total in data:
        labels.append(month)
        values.append(total)

    return jsonify({

        "total_patients": total_patients,
        "labels": labels,
        "values": values

    })

@app.route("/disease_statistics")
def disease_statistics():

    return render_template("disease_statistics.html")

@app.route("/generate_disease_statistics")
def generate_disease_statistics():

    cursor = db.cursor()

    cursor.execute("""
        SELECT disease, COUNT(*) AS total
        FROM patients
        GROUP BY disease
        ORDER BY total DESC
    """)

    data = cursor.fetchall()

    labels = []
    values = []

    for disease, total in data:
        labels.append(disease)
        values.append(total)

    total_cases = sum(values)

    if len(labels) > 0:
        common_disease = labels[0]
    else:
        common_disease = "No Data"

    return jsonify({

        "labels": labels,
        "values": values,
        "total_cases": total_cases,
        "common_disease": common_disease

    })

@app.route("/revenue_analytics")
def revenue_analytics():

    return render_template("revenue_analytics.html")

@app.route("/generate_revenue_report")
def generate_revenue_report():

    cursor = db.cursor()

    # Total Bills
    cursor.execute("SELECT COUNT(*) FROM bills")
    total_bills = cursor.fetchone()[0]

    # Total Revenue
    cursor.execute("SELECT SUM(total_amount) FROM bills")
    total_revenue = cursor.fetchone()[0] or 0

    # Highest Bill
    cursor.execute("SELECT MAX(total_amount) FROM bills")
    highest_bill = cursor.fetchone()[0] or 0

    # Average Bill
    average_bill = 0

    if total_bills > 0:
        average_bill = round(total_revenue / total_bills, 2)

    return jsonify({

        "total_revenue": total_revenue,
        "total_bills": total_bills,
        "highest_bill": highest_bill,
        "average_bill": average_bill

    })

@app.route("/generate_doctor_productivity")
def generate_doctor_productivity():

    cursor = db.cursor()

    cursor.execute("""
        SELECT
        d.doctor_name,
        COUNT(DISTINCT a.appointment_id) AS appointments,
        COUNT(DISTINCT p.patient_id) AS patients
     FROM doctors d
       LEFT JOIN appointments a
       ON d.doctor_id = a.doctor_id
       LEFT JOIN patients p
       ON d.doctor_id = p.doctor_id
       GROUP BY d.doctor_id, d.doctor_name
       """)

    doctor_data = cursor.fetchall()

    report = ""

    labels = []
    values = []
    patient_values = []

    best_doctor = ""
    max_appointments = -1

    for doctor, appointments, patients in doctor_data:

        labels.append(doctor)
        values.append(appointments)
        patient_values.append(patients)

        if appointments >= 30:
            rating = "⭐⭐⭐⭐⭐"

        elif appointments >= 20:
            rating = "⭐⭐⭐⭐"

        elif appointments >= 10:
            rating = "⭐⭐⭐"

        else:
            rating = "⭐⭐"

        report += f"""
    Doctor : {doctor}
    Appointments : {appointments}
    Rating : {rating}
    """
        
        if appointments > max_appointments:
            max_appointments = appointments
            best_doctor = doctor

    prompt = f"""
You are an AI Hospital Administrator.

Doctor Productivity Data:

{report}

Most Productive Doctor:
{best_doctor}

Give:
1. Doctor Performance Summary
2. Five AI Insights
3. Five Recommendations
Keep answer under 200 words.
"""

    try:

        response = gemini_model.generate_content(prompt)
        ai_report = response.text
        ai_report = ai_report.replace("*", "")
        ai_report = ai_report.replace("•", "🔹")

    except Exception as e:

        print("Gemini Error:", e)

        total_appointments = sum(values)

        avg = 0

        if len(values) > 0:
            avg = round(total_appointments / len(values), 1)

        ai_report = f"""

        🏥 Doctor Productivity Analysis

        🔹 Total Doctors : {len(labels)}

        🔹 Total Appointments : {total_appointments}

        🔹 Average Appointments per Doctor : {avg}

        🔹 Best Performing Doctor : {best_doctor}

        🔹 Overall Productivity : Good

        Recommendations

        ✅ Balance appointments among doctors.

        ✅ Encourage doctors with lower workload.

        ✅ Improve appointment scheduling.

        ✅ Monitor patient satisfaction regularly.

        ✅ Review doctor performance every month.

        """
        
        try:

            response = gemini_model.generate_content(prompt)

            print(response.text)

            ai_report = response.text

        except Exception as e:

            print("Gemini Error:", e)

    return jsonify({

        "report": report,
        "ai_report": ai_report,
        "labels": labels,
        "values": values,
        "patients": patient_values,
        "best_doctor": best_doctor

    })

@app.route("/generate_hospital_report")
def generate_hospital_report():

    cursor = db.cursor()

    # Total Patients
    cursor.execute("SELECT COUNT(*) FROM patients")
    total_patients = cursor.fetchone()[0]

    # Total Doctors
    cursor.execute("SELECT COUNT(*) FROM doctors")
    total_doctors = cursor.fetchone()[0]

    # Total Staff
    cursor.execute("SELECT COUNT(*) FROM staff")
    total_staff = cursor.fetchone()[0]

    # Total Appointments
    cursor.execute("SELECT COUNT(*) FROM appointments")
    total_appointments = cursor.fetchone()[0]

    # Total Beds
    cursor.execute("SELECT SUM(total_beds) FROM beds")
    total_beds = cursor.fetchone()[0] or 0

    # Available Beds
    cursor.execute("""
        SELECT SUM(total_beds - occupied_beds)
        FROM beds
    """)
    available_beds = cursor.fetchone()[0] or 0

    # Bed Occupancy
    occupied_beds = total_beds - available_beds

    if total_beds > 0:
        occupancy = round((occupied_beds / total_beds) * 100, 2)
    else:
        occupancy = 0

    # Hospital Score
    score = 100

    if occupancy > 90:
        score -= 20

    if total_doctors == 0:
        score -= 30

    if total_staff == 0:
        score -= 20

    if score >= 90:
        status = "🟢 Excellent"

    elif score >= 75:
        status = "🟡 Good"

    elif score >= 50:
        status = "🟠 Average"

    else:
        status = "🔴 Needs Improvement"

    prompt = f"""
You are an AI Hospital Administrator.

Hospital Statistics

Total Patients : {total_patients}
Total Doctors : {total_doctors}
Total Staff : {total_staff}
Total Appointments : {total_appointments}
Total Beds : {total_beds}
Available Beds : {available_beds}
Bed Occupancy : {occupancy}%
Hospital Score : {score}/100

Generate a professional report.

Format:

🏥 Hospital Performance Report
Current Statistics
AI Insights (5 bullet points)
Recommendations (5 bullet points)
Overall Status
Keep answer under 250 words.
"""

    try:

        response = gemini_model.generate_content(prompt)

        report = response.text

    except Exception:

        report = f"""
🏥 Hospital Performance Report

Current Statistics

• Total Patients : {total_patients}
• Total Doctors : {total_doctors}
• Total Staff : {total_staff}
• Total Appointments : {total_appointments}
• Total Beds : {total_beds}
• Available Beds : {available_beds}
• Bed Occupancy : {occupancy}%

Recommendations

• Increase hospital efficiency.
• Improve patient management.
• Monitor bed occupancy.
• Conduct regular audits.
• Continue quality healthcare.

Overall Status : {status}
"""

    return jsonify({

        "patients": total_patients,
        "doctors": total_doctors,
        "staff": total_staff,
        "appointments": total_appointments,
        "beds": total_beds,
        "available": available_beds,
        "occupancy": occupancy,
        "score": score,
        "status": status,
        "report": report

    })

@app.route("/generate_department_report")
def generate_department_report():

    cursor = db.cursor()

    cursor.execute("""
        SELECT department, COUNT(*) AS patients
        FROM patients
        GROUP BY department
    """)

    patient_data = cursor.fetchall()

    cursor.execute("""
        SELECT specialization, COUNT(*) AS doctors
        FROM doctors
        GROUP BY specialization
    """)

    doctor_data = cursor.fetchall()

    departments = []
    patient_counts = []
    doctor_counts = []

    report = ""

    best_department = ""
    max_patients = 0

    for dept, patients in patient_data:

        doctors = 0

        for spec, total in doctor_data:

            if spec and spec.lower() == dept.lower():

                doctors = total
                break

        if patients > max_patients:

            max_patients = patients
            best_department = dept

        departments.append(dept)
        patient_counts.append(patients)
        doctor_counts.append(doctors)

        if patients >= 20:
            status = "🔴 Busy"

        elif patients >= 10:
            status = "🟡 Moderate"

        else:
            status = "🟢 Good"

        report += f"""
Department : {dept}
Patients   : {patients}
Doctors    : {doctors}
Status     : {status}

"""

    prompt = f"""
You are an AI Hospital Administrator.
Department Statistics

{report}

Generate:

🏥 Department Performance Report
Current Statistics
AI Insights (5 Bullet Points)
Recommendations (5 Bullet Points)
Overall Best Department
Keep answer under 250 words.
"""

    try:

        response = gemini_model.generate_content(prompt)

        ai_report = response.text

    except:

        ai_report = report

    return jsonify({

        "departments": departments,
        "patients": patient_counts,
        "doctors": doctor_counts,
        "best_department": best_department,
        "department_report": report,
        "ai_report": ai_report

    })

@app.route("/disease_prediction")
def disease_prediction():

    return render_template("disease_prediction.html")

latest_age = ""
latest_temp = ""
latest_symptoms = ""
latest_prediction = ""

@app.route("/predict_disease", methods=["POST"])
def predict_disease():
     
    global latest_age
    global latest_temp
    global latest_symptoms
    global latest_prediction
    age = request.form["age"]
    temp = request.form["temp"]
    symptoms = request.form["symptoms"]
    latest_age = age
    latest_temp = temp
    latest_symptoms = symptoms

    prompt = f"""
   You are an experienced hospital AI assistant.
   Patient Details:
   Age: {age}
   Temperature: {temp} °F
   Symptoms: {symptoms}

   Analyze the patient and return the answer EXACTLY in this format.

   ## 🩺 Possible Disease
   ...

   ## 📊 Confidence
   ...

   ## 🧪 Recommended Tests
   - Test 1
   - Test 2
   - Test 3

   ## 🏠 Home Care
   - Tip 1
   - Tip 2
   - Tip 3

   ## 👨‍⚕️ Doctor Advice
   ...

   Rules:
   - Use headings.
   - Use bullet points.
   - Keep every point on a new line.
   - Don't write everything in one paragraph.
   - Maximum 180 words.
   """

    try:

        response = gemini_model.generate_content(prompt)
        advice = response.text
        latest_prediction = advice

        return jsonify({

            "disease": "AI Disease Prediction",
            "advice": advice

        })

    except Exception as e:

        return jsonify({

            "disease": "Prediction Failed",
            "advice": str(e)

        })

@app.route("/download_ai_report")
def download_ai_report():

    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    from datetime import datetime

    pdf_file = "AI_Medical_Report.pdf"

    doc = SimpleDocTemplate(pdf_file)

    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("<b><font size=18>CITY CARE HOSPITAL</font></b>", styles["Title"]))
    story.append(Paragraph("AI Medical Report", styles["Heading2"]))
    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph(f"<b>Date:</b> {datetime.now()}", styles["Normal"]))
    story.append(Paragraph(f"<b>Age:</b> {latest_age}", styles["Normal"]))
    story.append(Paragraph(f"<b>Temperature:</b> {latest_temp} °F", styles["Normal"]))
    story.append(Paragraph(f"<b>Symptoms:</b> {latest_symptoms}", styles["Normal"]))
    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph("<b>AI Prediction</b>", styles["Heading2"]))
    story.append(Paragraph(latest_prediction.replace("\n","<br/>"), styles["Normal"]))

    story.append(Paragraph("<br/><br/>", styles["Normal"]))
    story.append(Paragraph("Doctor Signature: ____________________", styles["Normal"]))

    doc.build(story)

    return send_file(pdf_file, as_attachment=True)

@app.route("/doctors")
def doctors():

    if "user_id" not in session:
        return redirect("/")
    
    if session["role"] != "Admin":
     return "Access Denied"

    cursor.execute("SELECT * FROM doctors")
    data = cursor.fetchall()

    return render_template("doctors.html", doctors=data)

@app.route("/add_doctor", methods=["POST"])
def add_doctor():

    if "user_id" not in session:
        return redirect("/")

    doctor_name = request.form["doctor_name"]
    specialization = request.form["specialization"]
    experience = request.form["experience"]
    mobile = request.form["mobile"]
    email = request.form["email"]

    sql = """
    INSERT INTO doctors
    (doctor_name, specialization, experience, mobile, email)
    VALUES (%s,%s,%s,%s,%s)
    """

    values = (
        doctor_name,
        specialization,
        experience,
        mobile,
        email
    )

    cursor.execute(sql, values)
    db.commit()

    flash("Doctor Added Successfully!")

    return redirect("/doctors")

@app.route("/billing")
def billing():

    if "user_id" not in session:
        return redirect("/")

    cursor.execute("""
        SELECT patient_id, name
        FROM patients
        ORDER BY name
    """)

    patients = cursor.fetchall()

    cursor.execute("""
        SELECT
    b.bill_id,
    p.name,
    b.consultation_fee,
    b.medicine_charge,
    b.room_charge,
    b.total_amount,
    b.payment_status
FROM bills b
JOIN patients p
ON b.patient_id = p.patient_id
ORDER BY b.bill_id DESC
    """)

    bills = cursor.fetchall()

    return render_template(
        "billing.html",
        patients=patients,
        bills=bills
    )

@app.route("/appointments")
def appointments():

    if "user_id" not in session:
        return redirect("/")

    cursor = db.cursor()

    search = request.args.get("search", "")

    # Patients
    cursor.execute("SELECT patient_id,name FROM patients")
    patients = cursor.fetchall()

    # Doctors
    cursor.execute("SELECT doctor_id,doctor_name FROM doctors")
    doctors = cursor.fetchall()

    # Appointment Search
    if search:

        cursor.execute("""
        SELECT
        a.appointment_id,
        p.name,
        d.doctor_name,
        a.appointment_date,
        a.appointment_time,
        a.reason,
        a.status
        FROM appointments a
        JOIN patients p
        ON a.patient_id=p.patient_id
        JOIN doctors d
        ON a.doctor_id=d.doctor_id
        WHERE
        p.name LIKE %s
        OR d.doctor_name LIKE %s
        ORDER BY a.appointment_date DESC
        """, (
            "%" + search + "%",
            "%" + search + "%"
        ))

    else:

        cursor.execute("""
        SELECT
        a.appointment_id,
        p.name,
        d.doctor_name,
        a.appointment_date,
        a.appointment_time,
        a.reason,
        a.status
        FROM appointments a
        JOIN patients p
        ON a.patient_id=p.patient_id
        JOIN doctors d
        ON a.doctor_id=d.doctor_id
        ORDER BY a.appointment_date DESC
        """)

    appointments = cursor.fetchall()

    # Today's Appointments
    cursor.execute("""
    SELECT COUNT(*)
    FROM appointments
    WHERE appointment_date = CURDATE()
    """)
    today_count = cursor.fetchone()[0]

    # Upcoming Appointments
    cursor.execute("""
    SELECT COUNT(*)
    FROM appointments
    WHERE appointment_date > CURDATE()
    """)
    upcoming_count = cursor.fetchone()[0]

    # Completed
    cursor.execute("""
    SELECT COUNT(*)
    FROM appointments
    WHERE status='Completed'
    """)
    completed_count = cursor.fetchone()[0]

    # Cancelled
    cursor.execute("""
    SELECT COUNT(*)
    FROM appointments
    WHERE status='Cancelled'
    """)
    cancelled_count = cursor.fetchone()[0]

    return render_template(
        "appointments.html",
        patients=patients,
        doctors=doctors,
        appointments=appointments,
        search=search,
        today_count=today_count,
        upcoming_count=upcoming_count,
        completed_count=completed_count,
        cancelled_count=cancelled_count
    )

@app.route("/add_appointment", methods=["POST"])
def add_appointment():

    if "user_id" not in session:
        return redirect("/")

    patient_id = request.form["patient_id"]
    doctor_id = request.form["doctor_id"]
    appointment_date = request.form["appointment_date"]
    appointment_time = request.form["appointment_time"]
    reason = request.form["reason"]

    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO appointments
        (patient_id, doctor_id, appointment_date, appointment_time, reason)
        VALUES (%s,%s,%s,%s,%s)
    """, (
        patient_id,
        doctor_id,
        appointment_date,
        appointment_time,
        reason
    ))

    db.commit()

    cursor.execute("""
        INSERT INTO notifications (message, type)
        VALUES (%s, %s)
        """, (
        f"New appointment booked for Patient ID {patient_id}.",
        "Appointment"
    ))

    db.commit()

    return redirect("/appointments")

@app.route("/edit_appointment/<int:id>")
def edit_appointment(id):

    if "user_id" not in session:
        return redirect("/")

    cursor = db.cursor()

    # Current Appointment
    cursor.execute("""
        SELECT
        appointment_id,
        patient_id,
        doctor_id,
        appointment_date,
        appointment_time,
        reason,
        status
        FROM appointments
        WHERE appointment_id=%s
    """,(id,))

    appointment = cursor.fetchone()

    # Patients
    cursor.execute("SELECT patient_id,name FROM patients")
    patients = cursor.fetchall()

    # Doctors
    cursor.execute("SELECT doctor_id,doctor_name FROM doctors")
    doctors = cursor.fetchall()

    return render_template(
        "edit_appointment.html",
        appointment=appointment,
        patients=patients,
        doctors=doctors
    )

@app.route("/update_appointment/<int:id>", methods=["POST"])
def update_appointment(id):

    if "user_id" not in session:
        return redirect("/")

    patient_id = request.form["patient_id"]
    doctor_id = request.form["doctor_id"]
    appointment_date = request.form["appointment_date"]
    appointment_time = request.form["appointment_time"]
    reason = request.form["reason"]
    status = request.form["status"]

    cursor = db.cursor()

    cursor.execute("""
        UPDATE appointments
        SET
            patient_id=%s,
            doctor_id=%s,
            appointment_date=%s,
            appointment_time=%s,
            reason=%s,
            status=%s
        WHERE appointment_id=%s
    """, (
        patient_id,
        doctor_id,
        appointment_date,
        appointment_time,
        reason,
        status,
        id
    ))

    db.commit()

    return redirect("/appointments")

@app.route("/delete_appointment/<int:id>")
def delete_appointment(id):

    if "user_id" not in session:
        return redirect("/")

    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM appointments WHERE appointment_id=%s",
        (id,)
    )

    db.commit()

    return redirect("/appointments")

@app.route("/add_bill", methods=["POST"])
def add_bill():

    if "user_id" not in session:
        return redirect("/")

    patient_id = request.form["patient_id"]
    consultation_fee = float(request.form["consultation_fee"])
    medicine_charge = float(request.form["medicine_charge"])
    room_charge = float(request.form["room_charge"])
    payment_status = request.form["payment_status"]

    total_amount = consultation_fee + medicine_charge + room_charge

    sql = """
    INSERT INTO bills
    (patient_id, consultation_fee, medicine_charge,
    room_charge, total_amount, payment_status)
    VALUES (%s,%s,%s,%s,%s,%s)
    """

    values = (
        patient_id,
        consultation_fee,
        medicine_charge,
        room_charge,
        total_amount,
        payment_status
    )

    cursor.execute(sql, values)
    db.commit()

    cursor.execute("""
        INSERT INTO notifications (message, type)
        VALUES (%s, %s)
        """, (
        f"Bill generated for Patient ID {patient_id}.",
        "Billing"
    ))

    db.commit()

    flash("Bill Generated Successfully!")

    return redirect("/billing")

@app.route("/print_bill/<int:bill_id>")
def print_bill(bill_id):

    if "user_id" not in session:
        return redirect("/")

    cursor.execute("""
    SELECT
        b.bill_id,
        p.name,
        b.consultation_fee,
        b.medicine_charge,
        b.room_charge,
        b.total_amount,
        b.payment_status
    FROM bills b
    JOIN patients p
    ON b.patient_id = p.patient_id
    WHERE b.bill_id=%s
    """, (bill_id,))

    bill = cursor.fetchone()

    pdf_file = f"bill_{bill_id}.pdf"

    doc = SimpleDocTemplate(pdf_file)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>🏥 Hospital Management System</b>", styles["Title"]))
    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph(f"<b>Bill ID:</b> {bill[0]}", styles["Normal"]))
    story.append(Paragraph(f"<b>Patient:</b> {bill[1]}", styles["Normal"]))
    story.append(Paragraph(f"<b>Consultation Fee:</b> ₹ {bill[2]}", styles["Normal"]))
    story.append(Paragraph(f"<b>Medicine Charge:</b> ₹ {bill[3]}", styles["Normal"]))
    story.append(Paragraph(f"<b>Room Charge:</b> ₹ {bill[4]}", styles["Normal"]))
    story.append(Paragraph(f"<b>Total Amount:</b> ₹ {bill[5]}", styles["Heading2"]))
    story.append(Paragraph(f"<b>Status:</b> {bill[6]}", styles["Normal"]))

    doc.build(story)

    return send_file(pdf_file, as_attachment=True)

#VIEW & SEARCH PATIENTS

@app.route("/patients")
def patients():

    if "user_id" not in session:
        return redirect("/")

    search = request.args.get("search")

    if search:
        sql = """
        SELECT
        p.patient_id,
        p.name,
        p.age,
        p.gender,
        p.mobile,
        p.disease,
        p.department,
        d.doctor_name,
        p.admission_date
    FROM patients p
    LEFT JOIN doctors d
    ON p.doctor_id = d.doctor_id
    WHERE
        p.name LIKE %s
        OR p.disease LIKE %s
        OR p.department LIKE %s
    """
        value = (
            "%" + search + "%",
            "%" + search + "%",
            "%" + search + "%"
        )

        cursor.execute(sql, value)

    else:
        cursor.execute("""
            SELECT
            p.patient_id,
            p.name,
            p.age,
            p.gender,
            p.mobile,
            p.disease,
            p.department,
            d.doctor_name,
            p.admission_date
            FROM patients p
            LEFT JOIN doctors d
            ON p.doctor_id = d.doctor_id
        """)

    data = cursor.fetchall()

    return render_template("patients.html", patients=data)

@app.route("/register")
def register():

    if "user_id" not in session:
        return redirect("/")

    cursor.execute("SELECT doctor_id, doctor_name FROM doctors")
    doctors = cursor.fetchall()

    return render_template(
        "register_patient.html",
        doctors=doctors
    )

#ADD PATIENT

@app.route("/add_patient", methods=["POST"])
def add_patient():

    print("SESSION =", dict(session))

    if "user_id" not in session:
        return redirect("/patients")

    name = request.form["name"]
    age = request.form["age"]
    gender = request.form["gender"]
    mobile = request.form["mobile"]
    disease = request.form["disease"]
    department = request.form["department"]
    doctor_id = request.form["doctor_id"]

    sql = """
    INSERT INTO patients
    (name, age, gender, mobile, disease, department, doctor_id, admission_date)
    VALUES (%s,%s,%s,%s,%s,%s,%s,CURDATE())
    """

    values = (name, age, gender, mobile, disease, department, doctor_id)

    cursor.execute(sql, values)
    db.commit()

    # Notification
    cursor.execute("""
        INSERT INTO notifications (message, type)
        VALUES (%s, %s)
        """, (
        f"New patient '{name}' registered successfully.",
        "Patient"
    ))

    db.commit()

    flash("Patient Registered Successfully!")

    return redirect("/patients")

@app.route("/patient/<int:id>")
def patient_details(id):

    if "user_id" not in session:
        return redirect("/")

    sql= """
    SELECT
        p.patient_id,
        p.name,
        p.age,
        p.gender,
        p.mobile,
        p.disease,
        p.department,
        d.doctor_name
    FROM patients p
    LEFT JOIN doctors d
    ON p.doctor_id = d.doctor_id
    WHERE p.patient_id= %s
    """

    cursor.execute(sql, (id,))
    patient = cursor.fetchone()

    return render_template(
        "patient_details.html",
        patient=patient
    )

#DELETE PATIENT

@app.route("/delete/<int:id>")
def delete_patient(id):

    if "user_id" not in session:
        return redirect("/")

    cursor.execute(
        "DELETE FROM patients WHERE patient_id=%s",
        (id,)
    )

    db.commit()

    flash("Patient deleted successfully!")

    return redirect("/patients")


#EDIT PATIENT

@app.route("/edit/<int:id>")
def edit_patient(id):

    if "user_id" not in session:
        return redirect("/")

    cursor.execute(
        "SELECT * FROM patients WHERE patient_id=%s",
        (id,)
    )

    patient = cursor.fetchone()

    return render_template(
        "edit_patient.html",
        patient=patient
    )


#UPDATE PATIENT

@app.route("/update_patient/<int:id>", methods=["POST"])
def update_patient(id):

    if "user_id" not in session:
        return redirect("/")

    name = request.form["name"]
    age = request.form["age"]
    disease = request.form["disease"]
    department = request.form["department"]

    sql = """
    UPDATE patients
    SET
        name=%s,
        age=%s,
        disease=%s,
        department=%s
    WHERE patient_id=%s
    """

    values = (
        name,
        age,
        disease,
        department,
        id
    )

    cursor.execute(sql, values)
    db.commit()

    flash("Patient Updated Successfully!")

    return redirect("/patients")

@app.route("/pharmacy")
def pharmacy():

    if "user_id" not in session:
        return redirect("/")

    if session["role"] != "Admin":
     return "Access Denied"

    cursor = db.cursor()

    search = request.args.get("search", "")

    if search:

        cursor.execute("""
       SELECT
       medicine_id,
       medicine_name,
       company,
       category,
       price,
       stock,
       expiry_date,
       DATEDIFF(expiry_date, CURDATE()) AS days_left
       FROM medicines
       WHERE
       medicine_name LIKE %s
       OR company LIKE %s
       OR category LIKE %s
       ORDER BY medicine_name
       """, (
       "%" + search + "%",
       "%" + search + "%",
       "%" + search + "%"
        ))

    else:

        cursor.execute("""
        SELECT
        medicine_id,
        medicine_name,
        company,
        category,
        price,
        stock,
        expiry_date,
        DATEDIFF(expiry_date, CURDATE()) AS days_left               
        FROM medicines
        ORDER BY medicine_name
        """)

    medicines = cursor.fetchall()
    # Low Stock Count
    cursor.execute("""
    SELECT COUNT(*)
    FROM medicines
    WHERE stock < 10
    """)
    low_stock_count = cursor.fetchone()[0]
    
    return render_template(
        "pharmacy.html",
        medicines=medicines,
        search=search,
        low_stock_count=low_stock_count
    )

@app.route("/add_medicine")
def add_medicine():

    if "user_id" not in session:
        return redirect("/")

    return render_template("add_medicine.html")

@app.route("/save_medicine", methods=["POST"])
def save_medicine():

    if "user_id" not in session:
        return redirect("/")

    medicine_name = request.form["medicine_name"]
    company = request.form["company"]
    category = request.form["category"]
    price = request.form["price"]
    stock = request.form["stock"]
    expiry_date = request.form["expiry_date"]

    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO medicines
        (medicine_name, company, category, price, stock, expiry_date)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (
        medicine_name,
        company,
        category,
        price,
        stock,
        expiry_date
    ))

    db.commit()

    cursor.execute("""
        INSERT INTO notifications (message, type)
        VALUES (%s, %s)
        """, (
        f"Medicine '{medicine_name}' added to inventory.",
        "Pharmacy"
    ))

    db.commit()

    return redirect("/pharmacy")

@app.route("/edit_medicine/<int:id>")
def edit_medicine(id):

    if "user_id" not in session:
        return redirect("/")

    cursor = db.cursor()

    cursor.execute("""
        SELECT
        medicine_id,
        medicine_name,
        company,
        category,
        price,
        stock,
        expiry_date
        FROM medicines
        WHERE medicine_id=%s
    """, (id,))

    medicine = cursor.fetchone()

    return render_template(
        "edit_medicine.html",
        medicine=medicine
    )

@app.route("/update_medicine", methods=["POST"])
def update_medicine():

    if "user_id" not in session:
        return redirect("/")

    medicine_id = request.form["medicine_id"]
    medicine_name = request.form["medicine_name"]
    company = request.form["company"]
    category = request.form["category"]
    price = request.form["price"]
    stock = request.form["stock"]
    expiry_date = request.form["expiry_date"]

    cursor = db.cursor()

    cursor.execute("""
        UPDATE medicines
        SET
        medicine_name=%s,
        company=%s,
        category=%s,
        price=%s,
        stock=%s,
        expiry_date=%s
        WHERE medicine_id=%s
    """, (
        medicine_name,
        company,
        category,
        price,
        stock,
        expiry_date,
        medicine_id
    ))

    db.commit()

    return redirect("/pharmacy")

@app.route("/delete_medicine/<int:id>")
def delete_medicine(id):

    if "user_id" not in session:
        return redirect("/")

    cursor = db.cursor()

    cursor.execute("""
    DELETE FROM medicines
    WHERE medicine_id=%s
    """,(id,))

    db.commit()

    return redirect("/pharmacy")

@app.route("/beds")
def beds():

    if "user_id" not in session:
        return redirect("/")

    cursor = db.cursor()
    search = request.args.get("search", "")
    
    # Patient List
    cursor.execute("""
    SELECT patient_id,name
    FROM patients
    ORDER BY name
    """)
    patients = cursor.fetchall()

    # Department Bed Summary
    cursor.execute("""
    SELECT
    bed_id,
    department,
    total_beds,
    occupied_beds
    FROM beds
    """)
    bed_summary = cursor.fetchall()

    # Allocation List
    if search:
     cursor.execute("""
     SELECT
     b.allocation_id,
     p.name,
     b.bed_number,
     b.allocation_date,
     b.discharge_date,
     b.status
     FROM bed_allocation b
     JOIN patients p
     ON b.patient_id = p.patient_id
     WHERE
     p.name LIKE %s
     OR b.bed_number LIKE %s
     OR b.status LIKE %s
     ORDER BY b.allocation_date DESC
     """,(
        "%" + search + "%",
        "%" + search + "%",
        "%" + search + "%"
    ))

    else:
     cursor.execute("""
    SELECT
    b.allocation_id,
    p.name,
    b.bed_number,
    b.allocation_date,
    b.discharge_date,
    b.status
    FROM bed_allocation b
    JOIN patients p
    ON b.patient_id = p.patient_id
    ORDER BY b.allocation_date DESC
    """)
    allocations = cursor.fetchall()

    return render_template(
        "beds.html",
        patients=patients,
        bed_summary=bed_summary,
        allocations=allocations,
        search=search
    )

@app.route("/add_bed")
def add_bed():

    if "user_id" not in session:
        return redirect("/")

    cursor = db.cursor()

    cursor.execute("""
    SELECT patient_id,name
    FROM patients
    ORDER BY name
    """)
    patients = cursor.fetchall()

    cursor.execute("""
    SELECT bed_id, department
    FROM beds
    """)
    departments = cursor.fetchall()
    print("Departments:", departments)
    return render_template(
        "add_bed.html",
        patients=patients,
        departments=departments
    )

@app.route("/save_bed", methods=["POST"])
def save_bed():

    if "user_id" not in session:
        return redirect("/")

    patient_id = request.form["patient_id"]
    bed_id = request.form["bed_id"]
    bed_number = request.form["bed_number"]
    allocation_date = request.form["allocation_date"]

    cursor = db.cursor()

    cursor.execute("""
    INSERT INTO bed_allocation
    (patient_id,bed_id,bed_number,allocation_date)
    VALUES(%s,%s,%s,%s)
    """,(
        patient_id,
        bed_id,
        bed_number,
        allocation_date
    ))

    cursor.execute("""
    UPDATE beds
    SET occupied_beds=occupied_beds+1
    WHERE bed_id=%s
    """,(bed_id,))

    db.commit()

    return redirect("/beds")

@app.route("/discharge_bed/<int:id>")
def discharge_bed(id):

    if "user_id" not in session:
        return redirect("/")

    cursor = db.cursor()

    # Find bed_id
    cursor.execute("""
    SELECT bed_id
    FROM bed_allocation
    WHERE allocation_id=%s
    """,(id,))

    bed = cursor.fetchone()

    if bed:

        bed_id = bed[0]

        # Update Allocation
        cursor.execute("""
        UPDATE bed_allocation
        SET
        status='Available',
        discharge_date=CURDATE()
        WHERE allocation_id=%s
        """,(id,))

        # Reduce Occupied Beds
        cursor.execute("""
        UPDATE beds
        SET occupied_beds=occupied_beds-1
        WHERE bed_id=%s
        """,(bed_id,))

        db.commit()

    return redirect("/beds")

@app.route("/edit_bed/<int:id>")
def edit_bed(id):

    if "user_id" not in session:
        return redirect("/")

    cursor = db.cursor()

    # Current Allocation
    cursor.execute("""
    SELECT
    allocation_id,
    patient_id,
    bed_id,
    bed_number,
    allocation_date,
    discharge_date,
    status
    FROM bed_allocation
    WHERE allocation_id=%s
    """, (id,))

    allocation = cursor.fetchone()

    # Patient List
    cursor.execute("""
    SELECT patient_id,name
    FROM patients
    ORDER BY name
    """)

    patients = cursor.fetchall()

    # Department List
    cursor.execute("""
    SELECT bed_id,department
    FROM beds
    ORDER BY department
    """)

    departments = cursor.fetchall()

    return render_template(
        "edit_bed.html",
        allocation=allocation,
        patients=patients,
        departments=departments
    )

@app.route("/update_bed", methods=["POST"])
def update_bed():

    if "user_id" not in session:
        return redirect("/")

    allocation_id = request.form["allocation_id"]
    patient_id = request.form["patient_id"]
    bed_id = request.form["bed_id"]
    bed_number = request.form["bed_number"]
    allocation_date = request.form["allocation_date"]

    cursor = db.cursor()

    cursor.execute("""
    UPDATE bed_allocation
    SET
    patient_id=%s,
    bed_id=%s,
    bed_number=%s,
    allocation_date=%s
    WHERE allocation_id=%s
    """,(
        patient_id,
        bed_id,
        bed_number,
        allocation_date,
        allocation_id
    ))

    db.commit()

    return redirect("/beds")

@app.route("/staff")
def staff():

    if "user_id" not in session:
        return redirect("/")

    if session["role"] != "Admin":
     return "Access Denied"
    
    cursor = db.cursor()
    search = request.args.get("search", "")
    if search:
     cursor.execute("""
    SELECT
    staff_id,
    staff_name,
    designation,
    department,
    salary,
    mobile,
    email,
    joining_date
    FROM staff
   WHERE
    staff_name LIKE %s
    OR designation LIKE %s
    OR department LIKE %s
    ORDER BY staff_name
    """,(
        "%" + search + "%",
        "%" + search + "%",
        "%" + search + "%"
    ))

    else:
     cursor.execute("""
      SELECT
    staff_id,
    staff_name,
    designation,
    department,
    salary,
    mobile,
    email,
    joining_date
    FROM staff
    ORDER BY staff_name
    """)               

    staff_list = cursor.fetchall()

    return render_template(
        "staff.html",
        staff_list=staff_list,
        search=search
    )

@app.route("/add_staff")
def add_staff_page():

    return render_template("add_staff.html")

@app.route("/save_staff", methods=["POST"])
def save_staff():

    if "user_id" not in session:
        return redirect("/")

    staff_name = request.form["staff_name"]
    designation = request.form["designation"]
    department = request.form["department"]
    salary = request.form["salary"]
    mobile = request.form["mobile"]
    email = request.form["email"]
    joining_date = request.form["joining_date"]

    cursor = db.cursor()

    cursor.execute("""
    INSERT INTO staff
    (staff_name,designation,department,salary,mobile,email,joining_date)
    VALUES(%s,%s,%s,%s,%s,%s,%s)
    """,(
        staff_name,
        designation,
        department,
        salary,
        mobile,
        email,
        joining_date
    ))

    db.commit()

    cursor.execute("""
        INSERT INTO notifications(message, type)
        VALUES(%s, %s)
        """, (
        f"New staff '{staff_name}' added successfully.",
        "Staff"
    ))

    db.commit()

    return redirect("/staff")

@app.route("/edit_staff/<int:id>")
def edit_staff(id):

    if "user_id" not in session:
        return redirect("/")

    cursor = db.cursor()

    cursor.execute("""
    SELECT
    staff_id,
    staff_name,
    designation,
    department,
    salary,
    mobile,
    email,
    joining_date
    FROM staff
    WHERE staff_id=%s
    """,(id,))

    staff = cursor.fetchone()

    return render_template(
        "edit_staff.html",
        staff=staff
    )

@app.route("/update_staff", methods=["POST"])
def update_staff():

    if "user_id" not in session:
        return redirect("/")
    staff_id = request.form["staff_id"]
    staff_name = request.form["staff_name"]
    designation = request.form["designation"]
    department = request.form["department"]
    salary = request.form["salary"]
    mobile = request.form["mobile"]
    email = request.form["email"]
    joining_date = request.form["joining_date"]

    cursor = db.cursor()

    cursor.execute("""
    UPDATE staff
    SET
    staff_name=%s,
    designation=%s,
    department=%s,
    salary=%s,
    mobile=%s,
    email=%s,
    joining_date=%s
    WHERE staff_id=%s
    """,(
        staff_name,
        designation,
        department,
        salary,
        mobile,
        email,
        joining_date,
        staff_id
    ))

    db.commit()

    return redirect("/staff")

@app.route("/delete_staff/<int:id>")
def delete_staff(id):

    if "user_id" not in session:
        return redirect("/")
    cursor = db.cursor()

    cursor.execute("""
    DELETE FROM staff
    WHERE staff_id=%s
    """,(id,))

    db.commit()

    return redirect("/staff")

if __name__ == "__main__":
    app.run(debug=True)