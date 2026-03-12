# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app source
COPY . .

# Cloud Run injects the PORT env variable
ENV PORT=8080

# Expose the port
EXPOSE 8080

# Run with Gunicorn (production WSGI server)
CMD exec gunicorn --bind :$PORT --workers 2 --threads 4 --timeout 120 server:app
