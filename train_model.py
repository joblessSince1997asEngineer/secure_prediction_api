from sklearn.linear_model import LinearRegression
import joblib
import numpy as np

# Features: [study_hours, attendance, prev_grade]
X = np.array([
    [10, 85, 70],
    [5, 50, 45],
    [15, 95, 90],
    [8, 75, 60],
    [12, 88, 80],
    [3, 40, 30],
    [20, 100, 95],
    [7, 70, 55]
])

# Target: final_score
y = np.array([80, 45, 92, 65, 78, 35, 98, 60])

model = LinearRegression().fit(X, y)
joblib.dump(model, "model.pkl")

print("Model trained and saved as model.pkl ✅")