import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

model = joblib.load("models/model.pkl")
app = FastAPI(title="ChurnGuard API")
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)

class Customer(BaseModel):
    gender: str
    SeniorCitizen: int
    Partner: str
    Dependents: str
    tenure: int
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    MonthlyCharges: float
    TotalCharges: float

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(c: Customer):
    row = pd.DataFrame([c.model_dump()])
    proba = float(model.predict_proba(row)[0, 1])
    return {"churn_probability": round(proba, 4),
            "churn": bool(proba >= 0.5)}

from fastapi.responses import FileResponse

@app.get("/")
def home():
    return FileResponse("src/index.html")
