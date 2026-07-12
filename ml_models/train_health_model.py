import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

# Load Dataset
data = pd.read_csv("dataset/health_dataset.csv")

# Features
X = data.drop("Risk", axis=1)

# Target
y = data["Risk"]

# Split Data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Train Model
model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)

# Save Model
joblib.dump(model, "ml_models/health_prediction_model.pkl")

print("✅ Health Prediction Model Created Successfully!")
print("Features:", model.feature_names_in_)