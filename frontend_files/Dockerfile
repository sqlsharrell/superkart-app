
# Use a lightweight Python base image
FROM python:3.9-slim-buster

# Set non-interactive frontend for apt-get commands
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory in the container
WORKDIR /app

# Update package lists with verbose error reporting
RUN set -ex; apt-get update

# Install network utilities (ping, curl) for debugging
RUN apt-get install -y iputils-ping curl && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit application code
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Command to run the Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
