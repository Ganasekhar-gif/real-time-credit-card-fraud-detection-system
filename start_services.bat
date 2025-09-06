@echo off
echo Starting Fraud Detection Services...
echo.

echo Starting Docker services (Kafka, MongoDB)...
docker-compose up -d

echo.
echo Waiting for services to start...
timeout /t 10 /nobreak > nul

echo.
echo Services started! You can now run:
echo   python producer.py    (in one terminal)
echo   python consumer.py    (in another terminal)
echo   python test_kafka_connection.py  (to test connections)
echo.
echo To stop services: docker-compose down
echo.
pause
