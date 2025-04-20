import json
import time
import random
import uuid  # For generating unique transaction IDs
from kafka import KafkaProducer

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    api_version=(2, 8, 0),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Function to generate transaction data
def generate_transaction():
    amount = round(random.uniform(1, 1000), 2)  # Keep raw amount
    return {
        "Transaction_ID": str(uuid.uuid4()),       # Unique transaction ID
        "Timestamp": time.time(),                  # Current Unix timestamp
        "Amount": amount,                          # Raw amount, used for model
        "Hour": random.randint(0, 23),
        "Day_Night": random.choice([0, 1])         # Could represent context feature
    }

# Send transactions continuously
while True:
    transaction = generate_transaction()
    producer.send('fraud_detection', transaction)
    print(f"Sent: {transaction}")
    time.sleep(2)
