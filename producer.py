import json
import time
import random
import uuid  # Import for generating unique transaction IDs
from kafka import KafkaProducer
import numpy as np  # Import numpy for log transformation

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    api_version=(2, 8, 0),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Function to generate transaction data
def generate_transaction():
    amount = random.uniform(1, 1000)  # Generate random amount (avoid log(0))
    log_amount = np.log(amount)  # Apply log transformation
    return {
        "Transaction_ID": str(uuid.uuid4()),  # Generate unique transaction ID
        "Timestamp": time.time(),  # Current Unix timestamp
        "Log_Amount": round(log_amount, 4),  
        "Hour": random.randint(0, 23),
        "Day_Night": random.choice([0, 1])
    }

# Send transactions continuously
while True:
    transaction = generate_transaction()
    producer.send('fraud_detection', transaction)
    print(f"Sent: {transaction}")
    time.sleep(2)
