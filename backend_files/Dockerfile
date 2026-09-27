
# Use a lightweight Python base image (upgraded to bullseye for consistency)
FROM python:3.9-slim-bullseye

# Set non-interactive frontend for apt-get commands
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory in the container
WORKDIR /app

# Update package lists and install net-tools (for netstat) and curl
RUN set -ex; \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get update && \
    apt-get install -y --no-install-recommends net-tools curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

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
