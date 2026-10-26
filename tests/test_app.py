from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

SAMPLE = {"gender":"Female","SeniorCitizen":0,"Partner":"Yes","Dependents":"No",
"tenure":1,"PhoneService":"No","MultipleLines":"No phone service","InternetService":"DSL",
"OnlineSecurity":"No","OnlineBackup":"Yes","DeviceProtection":"No","TechSupport":"No",
"StreamingTV":"No","StreamingMovies":"No","Contract":"Month-to-month",
"PaperlessBilling":"Yes","PaymentMethod":"Electronic check",
"MonthlyCharges":29.85,"TotalCharges":29.85}

def test_health():
    assert client.get("/health").json()["status"] == "ok"

def test_predict():
    r = client.post("/predict", json=SAMPLE)
    assert r.status_code == 200
    body = r.json()
    assert 0.0 <= body["churn_probability"] <= 1.0
    assert isinstance(body["churn"], bool)
