import json
import pandas as pd
from kafka import KafkaConsumer
import joblib
from pymongo import MongoClient

# Load fraud detection model
pipeline = joblib.load('fraud_detection_pipeline.pkl')


# Kafka Consumer
consumer = KafkaConsumer(
    'fraud_detection',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    api_version=(2, 8, 0)
)

# Connect to MongoDB
try:
    client = MongoClient("mongodb://localhost:27017/")  # Change "mongodb" to "localhost"
    db = client["fraud_detection"]
    collection = db["transactions"]
    print("Connected to MongoDB")
except Exception as e:
    print(f"MongoDB connection error: {e}")

print("Consumer is listening for messages...")

def preprocess_transaction(transaction):
    try:
        log_amount = transaction["Log_Amount"]
        hour = transaction["Hour"]
        day_night = transaction["Day_Night"]

        amount_per_hour = log_amount / max(hour, 1)  
        amount_vs_time = log_amount * hour

        input_data = pd.DataFrame([[log_amount, hour, day_night, amount_per_hour, amount_vs_time]],
                                  columns=['Log_Amount', 'Hour', 'Day_Night', 'Amount_per_Hour', 'Amount_vs_Time'])
        return input_data
    except Exception as e:
        print(f"Error in preprocessing: {e}")
        return None

# Consume messages
for message in consumer:
    try:
        transaction = message.value
        print(f"Received: {transaction}")

        processed_data = preprocess_transaction(transaction)
        if processed_data is not None:
            fraud_probability = pipeline.predict_proba(processed_data)[:, 1][0]
            fraud_label = "fraud" if fraud_probability > 0.5 else "legit"

            print(f"Fraud Probability: {fraud_probability:.4f}, Label: {fraud_label}")

            fraud_record = {
                "transaction_id": transaction.get("Transaction_ID", "unknown"),
                "timestamp": transaction.get("Timestamp", "unknown"),
                "log_amount": transaction["Log_Amount"],
                "hour": transaction["Hour"],
                "day_night": transaction["Day_Night"],
                "fraud_probability": round(fraud_probability, 4),
                "predicted_label": fraud_label
            }

            collection.insert_one(fraud_record)
            print("Stored transaction in MongoDB")

    except Exception as e:
        print(f"Error processing message: {e}")
