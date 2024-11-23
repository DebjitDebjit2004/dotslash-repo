# diabetes_model_training.py

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

# Step 1: Load Dataset
df = pd.read_csv('diabetes.csv')

# Step 2: Split Features and Labels
X = df.drop('Outcome', axis=1)
y = df['Outcome']

# Step 3: Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Step 4: Data Preprocessing (Scaling)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Step 5: Train the ML Model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# Step 6: Save the Trained Model and Scaler
joblib.dump(model, 'model/diabetes_model.pkl')  # Save ML model
joblib.dump(scaler, 'model/scaler.pkl')        # Save scaler

print("Model and scaler saved successfully!")
