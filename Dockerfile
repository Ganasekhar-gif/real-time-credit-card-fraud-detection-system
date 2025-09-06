# Use an official Python image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy all files to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the FastAPI application port
EXPOSE 8000

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "fraud:app", "--host", "0.0.0.0", "--port", "8000"]
