# Use an official Python runtime as a parent image
FROM python:3.11-slim
 
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
 
# Set work directory
WORKDIR /app
 
# Install system dependencies (if needed, e.g., for psycopg2)
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
 
# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
 
# Copy project files
COPY app ./app
COPY .env .env
 
# Expose the port FastAPI will run on
EXPOSE 8000
 
# Start the FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
 