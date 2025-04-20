import json
import pandas as pd
from kafka import KafkaConsumer
import joblib
from pymongo import MongoClient

# Load your Isolation Forest model pipeline
pipeline = joblib.load('anomaly_model.pkl')  # Assumed to include preprocessing

# Initialize Kafka Consumer
consumer = KafkaConsumer(
    'fraud_detection',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    api_version=(2, 8, 0)
)

# Connect to MongoDB
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["fraud_detection"]
    collection = db["transactions"]
    print("Connected to MongoDB")
except Exception as e:
    print(f"MongoDB connection error: {e}")

print("Consumer is listening for messages...")

# Function to preprocess raw transaction data
def preprocess_transaction(transaction):
    try:
        amount = transaction["Amount"]
        hour = transaction["Hour"]
        day_night = transaction["Day_Night"]

        # Optional engineered features
        amount_per_hour = amount / max(hour, 1)
        amount_vs_time = amount * hour

        input_data = pd.DataFrame([[amount, hour, day_night, amount_per_hour, amount_vs_time]],
                                  columns=['Amount', 'Hour', 'Day_Night', 'Amount_per_Hour', 'Amount_vs_Time'])
        return input_data
    except Exception as e:
        print(f"Error in preprocessing: {e}")
        return None

# Start listening
for message in consumer:
    try:
        transaction = message.value
        print(f"Received: {transaction}")

        processed_data = preprocess_transaction(transaction)
        if processed_data is not None:
            # Isolation Forest doesn't do predict_proba
            prediction = pipeline.predict(processed_data)[0]       # -1 = anomaly, 1 = normal
            score = pipeline.decision_function(processed_data)[0]  # anomaly score

            label = "anomaly" if prediction == -1 else "normal"

            print(f"Anomaly Score: {score:.4f}, Label: {label}")

            # Prepare record
            fraud_record = {
                "transaction_id": transaction.get("Transaction_ID", "unknown"),
                "timestamp": transaction.get("Timestamp", "unknown"),
                "amount": transaction["Amount"],
                "hour": transaction["Hour"],
                "day_night": transaction["Day_Night"],
                "anomaly_score": round(score, 4),
                "predicted_label": label
            }

            # Save to MongoDB
            collection.insert_one(fraud_record)
            print("Stored transaction in MongoDB")

            # (Optional) Send anomaly to another Kafka topic
            # if label == "anomaly":
            #     alert_producer.send("anomaly_alerts", fraud_record)

    except Exception as e:
        print(f"Error processing message: {e}")
