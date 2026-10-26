"""Compare recent 'production' data against training data for drift."""
import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset

# reference = training data; current = simulated production sample (shifted)
ref = pd.read_csv("data/churn.csv").drop(columns=["customerID", "Churn"])
ref["TotalCharges"] = pd.to_numeric(ref["TotalCharges"], errors="coerce")
ref = ref.dropna()

# simulate drift: newer customers skew to higher charges + shorter tenure
cur = ref.sample(frac=0.3, random_state=1).copy()
cur["MonthlyCharges"] = cur["MonthlyCharges"] * 1.4
cur["tenure"] = (cur["tenure"] * 0.5).astype(int)

report = Report(metrics=[DataDriftPreset()])
result = report.run(reference_data=ref, current_data=cur)
result.save_html("drift_report.html")
print("Drift report saved -> drift_report.html")
