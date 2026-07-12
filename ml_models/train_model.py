import pandas as pd
import mysql.connector
from sklearn.linear_model import LinearRegression

# MySQL Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Mysql@123",
    database="hospital_db"
)

# Load Data
query = "SELECT * FROM patients"
df = pd.read_sql(query, db)

print("Patients Data:\n")
print(df)

# Daily Patient Count
daily_data = df.groupby("admission_date").size().reset_index(name="patient_count")

print("\nDaily Patient Count:\n")
print(daily_data)

# Convert Date into Day Number
daily_data["day_number"] = range(1, len(daily_data) + 1)

print("\nPrepared Data:\n")
print(daily_data)

# Machine Learning Data
X = daily_data[["day_number"]]
y = daily_data["patient_count"]

# Train Model
model = LinearRegression()
model.fit(X, y)

print("\n✅ Machine Learning Model Trained Successfully!")

# Predict Next Day
next_day = [[len(daily_data) + 1]]

prediction = model.predict(next_day)

print("\n📊 Predicted Patients for Next Day:")
print(round(prediction[0]))

import joblib

# Save ML Model
joblib.dump(model, "ml_models/patient_prediction_model.pkl")

print("\n✅ Model Saved Successfully!")