# Use an official Python runtime as a base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI application code to the container
COPY main.py /app
COPY src/ /app/src

# Expose the port FastAPI runs on
EXPOSE 8000

# Start the FastAPI app using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]