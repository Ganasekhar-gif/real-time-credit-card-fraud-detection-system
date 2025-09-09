#!/usr/bin/env python3
"""
Improved consumer with adjustable fraud detection threshold
"""
import json
import pandas as pd
from kafka import KafkaConsumer
import joblib
from pymongo import MongoClient

# Load your model pipeline
pipeline = joblib.load('model/Fraud_Detection_Pipeline.pkl')

# Initialize Kafka Consumer
consumer = KafkaConsumer(
    'fraud_detection',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    api_version=(2, 8, 0),
    auto_offset_reset='earliest',
    group_id='improved_fraud_consumer_group',
    consumer_timeout_ms=10000
)

# Connect to MongoDB
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["fraud_detection"]
    collection = db["transactions"]
    print("Connected to MongoDB")
except Exception as e:
    print(f"MongoDB connection error: {e}")

# Configurable fraud detection threshold
FRAUD_THRESHOLD = 0.05  # 5% - much more sensitive than 50%
print(f"🚨 Fraud Detection Threshold: {FRAUD_THRESHOLD*100}%")

print("Consumer is listening for messages...")
print(f"Consumer configuration:")
print(f"  - Bootstrap servers: localhost:9092")
print(f"  - Topic: fraud_detection")
print(f"  - Consumer group: improved_fraud_consumer_group")
print(f"  - Fraud threshold: {FRAUD_THRESHOLD*100}%")

def preprocess_transaction(transaction):
    try:
        amount = transaction["Amount"]
        hour = transaction["Hour"]
        day_night = transaction["Day_Night"]

        # Feature engineering
        amount_per_hour = amount / max(hour, 1)
        amount_vs_time = amount * hour

        input_data = pd.DataFrame([[amount, hour, day_night, amount_per_hour, amount_vs_time]],
                                  columns=['Amount', 'Hour', 'Day_Night', 'Amount_per_Hour', 'Amount_vs_Time'])
        return input_data
    except Exception as e:
        print(f"Error in preprocessing: {e}")
        return None

def get_risk_level(fraud_probability):
    """Categorize risk level based on fraud probability"""
    if fraud_probability >= 0.20:
        return "HIGH_RISK"
    elif fraud_probability >= 0.10:
        return "MEDIUM_RISK"
    elif fraud_probability >= 0.05:
        return "LOW_RISK"
    else:
        return "SAFE"

# Start listening
print("Starting to listen for messages...")
message_count = 0
fraud_count = 0

try:
    for message in consumer:
        try:
            message_count += 1
            print(f"📨 Message #{message_count} received from topic: {message.topic}, partition: {message.partition}, offset: {message.offset}")
            transaction = message.value
            print(f"📄 Transaction data: {transaction}")

            processed_data = preprocess_transaction(transaction)
            if processed_data is not None:
                # Get prediction and probability
                prediction = pipeline.predict(processed_data)[0]
                fraud_proba = pipeline.predict_proba(processed_data)[0][1]
                
                # Use custom threshold instead of model's 50% threshold
                is_fraud = fraud_proba >= FRAUD_THRESHOLD
                risk_level = get_risk_level(fraud_proba)
                
                if is_fraud:
                    fraud_count += 1
                    label = "FRAUD"
                    emoji = "🚨"
                else:
                    label = "legit"
                    emoji = "✅"

                fraud_record = {
                    "transaction_id": transaction.get("Transaction_ID", "unknown"),
                    "timestamp": transaction.get("Timestamp", "unknown"),
                    "amount": transaction["Amount"],
                    "hour": transaction["Hour"],
                    "day_night": transaction["Day_Night"],
                    "fraud_probability": round(float(fraud_proba), 4),
                    "predicted_label": label,
                    "risk_level": risk_level,
                    "threshold_used": FRAUD_THRESHOLD
                }

                # Save to MongoDB
                result = collection.insert_one(fraud_record)
                print(f"{emoji} Stored transaction in MongoDB with ID: {result.inserted_id}")
                print(f"🏷️  Prediction: {label} (probability: {fraud_proba:.4f})")
                print(f"⚠️  Risk Level: {risk_level}")
                
                if is_fraud:
                    print(f"🚨 FRAUD ALERT! Transaction flagged for review!")
                    print(f"   Amount: ${transaction['Amount']}")
                    print(f"   Time: {transaction['Hour']}:00")
                    print(f"   Fraud Probability: {fraud_proba:.4f}")

            else:
                print("❌ Failed to preprocess transaction data")

        except Exception as e:
            print(f"❌ Error processing message: {e}")
            import traceback
            traceback.print_exc()

except Exception as e:
    if "timeout" in str(e).lower():
        print(f"⏰ Consumer timeout - no messages received in 10 seconds")
    else:
        print(f"❌ Consumer error: {e}")
        import traceback
        traceback.print_exc()

print(f"\n📊 Session Summary:")
print(f"   Total messages processed: {message_count}")
print(f"   Fraud alerts triggered: {fraud_count}")
print(f"   Fraud rate: {(fraud_count/message_count*100):.2f}%" if message_count > 0 else "   Fraud rate: 0%")
consumer.close()
print("🔚 Consumer closed")

