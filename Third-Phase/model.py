# train_model.py
import joblib
from sklearn.linear_model import LinearRegression
import numpy as np

# Dummy data
X = np.array([[170, 65], [160, 60], [180, 75], [175, 70]])  # height, weight
y = np.array([22, 23, 24, 23])

model = LinearRegression()
model.fit(X, y)

joblib.dump(model, "bmi_model.pkl")

print("Model saved to bmi_model.pkl")