# main.py
from fastapi import FastAPI
from pydantic import BaseModel
import joblib

app = FastAPI()

# Load model at startup (IMPORTANT)
model = joblib.load("./bmi_model.pkl")

# Input schema
class BMIPredictRequest(BaseModel):
    height: float
    weight: float

# Health check
@app.get("/")
def health():
    return {"status": "model server running"}

# Prediction endpoint
@app.post("/predict")
def predict_bmi(data: BMIPredictRequest):
    X = [[data.height, data.weight]]
    prediction = model.predict(X)[0]

    return {
        "bmi": round(prediction, 2)
    }
