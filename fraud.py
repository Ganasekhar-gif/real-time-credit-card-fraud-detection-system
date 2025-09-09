from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import time
import sys
import types
import numpy as np

# ----------------------------
# Prometheus Imports
# ----------------------------
from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator

# ----------------------------
# Custom Transformer (needed for pipeline deserialization)
# ----------------------------
from sklearn.base import BaseEstimator, TransformerMixin

class AnomalyAdder(BaseEstimator, TransformerMixin):
    def __init__(self, iso):
        self.iso = iso

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        labels = self.iso.predict(X)
        scores = self.iso.decision_function(X)
        X_copy = X.copy()
        X_copy["anomaly_label"] = (labels == -1).astype(int)
        X_copy["anomaly_score"] = scores
        return X_copy


# ----------------------------
# Initialize FastAPI
# ----------------------------
app = FastAPI(title="Fraud Detection API", version="1.0")

instrumentator = Instrumentator().instrument(app)
instrumentator.expose(app)

# ----------------------------
# Load Trained Model Pipeline
# ----------------------------
try:
    # Ensure unpickling can resolve custom classes when started by uvicorn workers:
    # Map __main__ and __mp_main__ to this module so GLOBAL('__main__','AnomalyAdder') resolves
    this_module = sys.modules.get(__name__)
    sys.modules["__main__"] = this_module
    sys.modules["__mp_main__"] = this_module

    pipeline = joblib.load("model/fraud_detection_pipe_line.pkl")
    print("✅ Model pipeline loaded successfully.")
except Exception as e:
    raise RuntimeError(f"❌ Failed to load model: {e}")

# ----------------------------
# MongoDB Connection
# ----------------------------
try:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/fraud_detection")
    client = MongoClient(MONGO_URI)
    db = client["fraud_detection"]
    collection = db["transactions"]
    print("✅ Connected to MongoDB.")
except Exception as e:
    raise RuntimeError(f"❌ MongoDB connection error: {e}")

# ----------------------------
# Input Schema for Prediction
# ----------------------------
class Transaction(BaseModel):
    Amount: float
    Hour: int
    Day_Night: int

# ----------------------------
# Prometheus Custom Metrics
# ----------------------------
PREDICTIONS = Counter(
    "fraud_predictions_total", "Total fraud detection predictions", ["label"]
)
LATENCY = Histogram(
    "fraud_prediction_latency_seconds", "Latency for fraud prediction requests"
)

# ----------------------------
# Routes
# ----------------------------
@app.get("/ping")
def health_check():
    return {"status": "ok", "message": "Fraud Detection API is running 🚀"}


@app.post("/predict")
def predict(transaction: Transaction):
    start_time = time.time()
    try:
        # Feature engineering (must match training features!)
        amount = transaction.Amount
        hour = transaction.Hour
        day_night = transaction.Day_Night
        amount_per_hour = amount / max(hour, 1)
        amount_vs_time = amount * hour

        # Convert to DataFrame
        input_data = pd.DataFrame(
            [[amount, hour, day_night, amount_per_hour, amount_vs_time]],
            columns=["Amount", "Hour", "Day_Night", "Amount_per_Hour", "Amount_vs_Time"]
        )

        # Model Prediction
        prediction = int(pipeline.predict(input_data)[0])  # 0 = legit, 1 = fraud
        fraud_proba = float(pipeline.predict_proba(input_data)[0][1])  # Probability of fraud

        label = "fraud" if prediction == 1 else "legit"

        # Update Prometheus metrics
        PREDICTIONS.labels(label=label).inc()
        LATENCY.observe(time.time() - start_time)

        result = {
            "amount": amount,
            "hour": hour,
            "day_night": day_night,
            "fraud_probability": round(fraud_proba, 4),
            "predicted_label": label
        }

        # Save to MongoDB
        insert_result = collection.insert_one(result)
        result["_id"] = str(insert_result.inserted_id)

        return {"status": "success", "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/transactions")
def get_all_transactions():
    try:
        records = list(collection.find().sort("_id", -1).limit(10))  # last 10
        for r in records:
            r["_id"] = str(r["_id"])
        return {"transactions": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/transactions/{transaction_id}")
def get_transaction(transaction_id: str):
    try:
        record = collection.find_one({"_id": ObjectId(transaction_id)})
        if not record:
            raise HTTPException(status_code=404, detail="Transaction not found")
        record["_id"] = str(record["_id"])
        return record
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
