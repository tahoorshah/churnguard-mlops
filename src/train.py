import pandas as pd
import mlflow, mlflow.sklearn, joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score

DATA = "data/churn.csv"

# 1. Load + clean
df = pd.read_csv(DATA)
df = df.drop(columns=["customerID"])
# TotalCharges has blank strings for new customers -> make numeric, drop the few blanks
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
df = df.dropna()
df["Churn"] = (df["Churn"] == "Yes").astype(int)

X = df.drop(columns=["Churn"])
y = df["Churn"]

num_cols = ["tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen"]
cat_cols = [c for c in X.columns if c not in num_cols]

# 2. Preprocess + model as ONE pipeline (so serving applies identical steps)
pre = ColumnTransformer([
    ("num", StandardScaler(), num_cols),
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
])
model = Pipeline([("pre", pre), ("clf", GradientBoostingClassifier(random_state=42))])

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# 3. Train + log to MLflow
mlflow.set_experiment("churn-prediction")
with mlflow.start_run():
    model.fit(X_tr, y_tr)
    proba = model.predict_proba(X_te)[:, 1]
    pred = (proba >= 0.5).astype(int)

    metrics = {
        "accuracy": accuracy_score(y_te, pred),
        "precision": precision_score(y_te, pred),
        "recall": recall_score(y_te, pred),
        "roc_auc": roc_auc_score(y_te, proba),
    }
    mlflow.log_param("model", "GradientBoosting")
    mlflow.log_metrics(metrics)
    mlflow.sklearn.log_model(model, name="model", skops_trusted_types=["sklearn.tree._tree.Tree"])

    Path("models").mkdir(exist_ok=True)
    joblib.dump(model, "models/model.pkl")
    print("Metrics:", {k: round(v, 4) for k, v in metrics.items()})
    print("Saved -> models/model.pkl  | logged to MLflow")
