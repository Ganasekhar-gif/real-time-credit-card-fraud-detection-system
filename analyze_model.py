#!/usr/bin/env python3
"""
Analyze the fraud detection model to understand its behavior
"""
import joblib
import pandas as pd
import numpy as np
from pymongo import MongoClient

def analyze_model():
    print("🔍 Analyzing Fraud Detection Model...")
    
    # Load the model
    try:
        pipeline = joblib.load('model/Fraud_Detection_Pipeline.pkl')
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return
    
    # Check model components
    print(f"\n📊 Model Type: {type(pipeline).__name__}")
    if hasattr(pipeline, 'steps'):
        print("🔧 Pipeline Steps:")
        for i, (name, step) in enumerate(pipeline.steps):
            print(f"  {i+1}. {name}: {type(step).__name__}")
    
    # Test with different scenarios
    print(f"\n🧪 Testing Model with Different Scenarios:")
    
    # Scenario 1: Normal transaction
    normal_tx = pd.DataFrame([[
        100.0,  # Amount
        14,     # Hour (2 PM)
        1,      # Day_Night (day)
        100.0/14,  # Amount_per_Hour
        100.0*14   # Amount_vs_Time
    ]], columns=['Amount', 'Hour', 'Day_Night', 'Amount_per_Hour', 'Amount_vs_Time'])
    
    pred_normal = pipeline.predict(normal_tx)[0]
    prob_normal = pipeline.predict_proba(normal_tx)[0]
    print(f"  Normal Transaction (Amount: $100, Hour: 14):")
    print(f"    Prediction: {'Fraud' if pred_normal == 1 else 'Legit'}")
    print(f"    Probabilities: Legit={prob_normal[0]:.4f}, Fraud={prob_normal[1]:.4f}")
    
    # Scenario 2: High amount transaction
    high_amount_tx = pd.DataFrame([[
        5000.0,  # High amount
        14,      # Hour
        1,       # Day_Night
        5000.0/14,
        5000.0*14
    ]], columns=['Amount', 'Hour', 'Day_Night', 'Amount_per_Hour', 'Amount_vs_Time'])
    
    pred_high = pipeline.predict(high_amount_tx)[0]
    prob_high = pipeline.predict_proba(high_amount_tx)[0]
    print(f"  High Amount Transaction (Amount: $5000, Hour: 14):")
    print(f"    Prediction: {'Fraud' if pred_high == 1 else 'Legit'}")
    print(f"    Probabilities: Legit={prob_high[0]:.4f}, Fraud={prob_high[1]:.4f}")
    
    # Scenario 3: Unusual time transaction
    unusual_time_tx = pd.DataFrame([[
        100.0,  # Normal amount
        3,      # Very early morning
        0,      # Night
        100.0/3,
        100.0*3
    ]], columns=['Amount', 'Hour', 'Day_Night', 'Amount_per_Hour', 'Amount_vs_Time'])
    
    pred_unusual = pipeline.predict(unusual_time_tx)[0]
    prob_unusual = pipeline.predict_proba(unusual_time_tx)[0]
    print(f"  Unusual Time Transaction (Amount: $100, Hour: 3 AM):")
    print(f"    Prediction: {'Fraud' if pred_unusual == 1 else 'Legit'}")
    print(f"    Probabilities: Legit={prob_unusual[0]:.4f}, Fraud={prob_unusual[1]:.4f}")
    
    # Scenario 4: Very high amount at unusual time
    suspicious_tx = pd.DataFrame([[
        10000.0,  # Very high amount
        2,        # Very early morning
        0,        # Night
        10000.0/2,
        10000.0*2
    ]], columns=['Amount', 'Hour', 'Day_Night', 'Amount_per_Hour', 'Amount_vs_Time'])
    
    pred_suspicious = pipeline.predict(suspicious_tx)[0]
    prob_suspicious = pipeline.predict_proba(suspicious_tx)[0]
    print(f"  Suspicious Transaction (Amount: $10000, Hour: 2 AM):")
    print(f"    Prediction: {'Fraud' if pred_suspicious == 1 else 'Legit'}")
    print(f"    Probabilities: Legit={prob_suspicious[0]:.4f}, Fraud={prob_suspicious[1]:.4f}")

def check_mongodb_data():
    print(f"\n📊 Checking MongoDB Data...")
    
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["fraud_detection"]
        collection = db["transactions"]
        
        # Get total count
        total_count = collection.count_documents({})
        print(f"  Total transactions in MongoDB: {total_count}")
        
        # Get fraud vs legit counts
        fraud_count = collection.count_documents({"predicted_label": "fraud"})
        legit_count = collection.count_documents({"predicted_label": "legit"})
        
        print(f"  Fraud predictions: {fraud_count}")
        print(f"  Legit predictions: {legit_count}")
        
        if total_count > 0:
            fraud_percentage = (fraud_count / total_count) * 100
            print(f"  Fraud rate: {fraud_percentage:.2f}%")
        
        # Get highest fraud probabilities
        print(f"\n🔍 Top 5 Highest Fraud Probabilities:")
        high_fraud = list(collection.find().sort("fraud_probability", -1).limit(5))
        for i, record in enumerate(high_fraud, 1):
            print(f"  {i}. Amount: ${record['amount']}, Hour: {record['hour']}, "
                  f"Probability: {record['fraud_probability']:.4f}, Label: {record['predicted_label']}")
        
        # Get statistics
        print(f"\n📈 Fraud Probability Statistics:")
        fraud_probs = [record['fraud_probability'] for record in collection.find()]
        if fraud_probs:
            print(f"  Min: {min(fraud_probs):.4f}")
            print(f"  Max: {max(fraud_probs):.4f}")
            print(f"  Mean: {np.mean(fraud_probs):.4f}")
            print(f"  Median: {np.median(fraud_probs):.4f}")
        
    except Exception as e:
        print(f"❌ Error accessing MongoDB: {e}")

if __name__ == "__main__":
    analyze_model()
    check_mongodb_data()
