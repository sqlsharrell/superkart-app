
# Use a lightweight Python base image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port the Flask app will run on
EXPOSE 7860

# Set the FLASK_APP environment variable
ENV FLASK_APP=app.py

# Command to run the Flask application
CMD ["flask", "run", "--host=0.0.0.0", "--port=7860"]
