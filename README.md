# 🚨 Real-Time Credit card Fraud Detection System

This project is a real-time fraud detection pipeline built with FastAPI, Kafka, MongoDB, and Machine Learning. It simulates financial transactions, predicts fraudulent activity using a trained ML model, and stores results in MongoDB for monitoring and analytics.

---

## 📦 Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python** | Core programming language |
| **FastAPI** | REST API server for real-time prediction and Kafka integration |
| **Kafka** | Real-time message streaming between producer and consumer |
| **MongoDB** | NoSQL database to store processed transaction results |
| **Docker** | Containerization of the complete stack |
| **Kubernetes (Minikube)** | Orchestration and scaling |
| **joblib** | Model serialization |
| **scikit-learn** | Machine learning model training & prediction |
| **NumPy, Pandas** | Data preprocessing and manipulation |

---

## 🎯 Features

- ✅ Real-time data generation and ingestion
- ✅ Machine learning-based fraud prediction
- ✅ Kafka-based producer-consumer architecture
- ✅ MongoDB storage for logging predictions
- ✅ REST APIs for transaction simulation
- ✅ Containerized deployment using Docker
- ✅ Scalable architecture using Kubernetes

---

## 🧠 Model

- Trained using historical transaction data.
- Feature engineered fields:
  - `Log_Amount`
  - `Hour`
  - `Day_Night`
  - `Amount_per_Hour`
  - `Amount_vs_Time`
- Output: Fraud probability and fraud label (`fraud` / `legit`)

---

## 📁 Project Structure
fraud_detection_project/
│── app/
│   ├── producer.py
│   ├── consumer.py
│   ├── fraud_detection_pipeline.pkl
│── docker/
│── k8s/  <-- Put YAML files here
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── kafka.yaml
│   ├── mongodb.yaml
│   ├── zookeeper.yaml
│── Dockerfile
│── requirements.txt
│── ...


## 🚀 Getting Started

### 1️⃣ Prerequisites

- Python 3.8+
- Docker
- Minikube (for Kubernetes)
- Kafka & Zookeeper
- MongoDB

---

### 2️⃣ Build & Run with Docker (Local)

```bash
docker build -t fraud-api .
docker run -p 8000:8000 fraud-api

#--> Running with kubernetes(minikube)
# Start minikube
minikube start

# Enable Kubernetes dashboard (optional)
minikube dashboard

# Deploy services
kubectl apply -f k8s/

# --> Access FastAPI service
minikube service fraud-api --url

# API endpoints/ POST/produce
curl -X POST http://<MINIKUBE-URL>/produce

# prediction endpoint/predict
curl -X POST http://<MINIKUBE-URL>/predict \
-H "Content-Type: application/json" \
-d '{"Log_Amount": 6.5, "Hour": 12, "Day_Night": 1}'

# MongoDB storage schema
{
  "transaction_id": "uuid",
  "timestamp": 1712134567.123,
  "log_amount": 6.52,
  "hour": 14,
  "day_night": 1,
  "fraud_probability": 0.86,
  "predicted_label": "fraud"
}

# monitoring and logging
kubectl logs <pod-name>
kubectl get pods

# To check MongoDB entries (inside container):
kubectl exec -it <mongodb-pod> -- bash
mongosh
use fraud_detection
db.transactions.find().pretty()

# Future improvements
 --> Integrate Redis as an optional message broker

 --> Add Prometheus & Grafana for monitoring

 --> Deploy using Helm charts

 --> Stream results to dashboard (e.g., using Dash or Streamlit)

# AUTHOR
email: ganasekharkalla@gmail.com
