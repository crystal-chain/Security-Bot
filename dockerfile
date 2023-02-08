# Use an official Python runtime as the base image
FROM python:3.8-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install required packages
RUN pip install -r requirements.txt

# Copy the application code to the container
COPY . .

# Set environment variables
ENV FLASK_APP=app.py

# Expose port 5000 for Flask
EXPOSE 5000

# Run the command to start the Flask application
CMD ["flask", "run", "--host=0.0.0.0"]