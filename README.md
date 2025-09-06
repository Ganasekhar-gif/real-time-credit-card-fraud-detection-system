# 🚨 Real-Time Credit card Fraud Detection System

This project is a real-time fraud detection pipeline built with FastAPI, Kafka, MongoDB, and Machine Learning. It simulates financial transactions, predicts fraudulent activity using a trained ML model, and stores results in MongoDB for monitoring and analytics.

---

## 📝 Project Overview

This system:
- Streams synthetic transactions using Kafka.
- Predicts fraudulent activity in real-time with an unsupervised ML model.
- Logs predictions into MongoDB for visualization or auditing.
- Is fully containerized via Docker and deployed on Kubernetes (Minikube).

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

# 🚀 Real-Time Fraud Detection System (Docker Compose Deployment)

# 1. Start all services (Zookeeper, Kafka, MongoDB, FastAPI)
docker-compose up -d

# 2. Check running containers
docker ps

# 3. API Endpoints (FastAPI is on port 8000)

# Produce Endpoint (simulate transaction stream)
curl -X POST http://localhost:8000/produce

# Prediction Endpoint
curl -X POST http://localhost:8000/predict \
-H "Content-Type: application/json" \
-d '{"Log_Amount": 6.5, "Hour": 12, "Day_Night": 1}'

# 4. MongoDB Storage Schema (example document)
{
  "transaction_id": "uuid",
  "timestamp": 1712134567.123,
  "log_amount": 6.52,
  "hour": 14,
  "day_night": 1,
  "fraud_probability": 0.86,
  "predicted_label": "fraud"
}

# 5. Logs & Monitoring

# View logs of all services
docker-compose logs -f

# View logs for FastAPI specifically
docker logs fraud_api

# View logs for Kafka
docker logs kafka

# 6. Access MongoDB (inside the container)
docker exec -it mongodb mongosh
use fraud_detection
db.transactions.find().pretty()

# 7. Stop all services
docker-compose down

# 8. Future Improvements
# - Integrate Redis as an optional message broker
# - Add Prometheus & Grafana for monitoring
# - Add healthchecks in docker-compose.yml
# - Stream results to a dashboard (Dash/Streamlit)
# - Deploy to Kubernetes later with Helm

# 📧 Author
# Email: ganasekharkalla@gmail.com
