
# Use a lightweight Python base image
FROM python:3.9-slim-buster

# Set non-interactive frontend for apt-get commands
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory in the container
WORKDIR /app

# Install network utilities (ping, curl) for debugging with retry for apt-get update
RUN set -ex; \
    MAX_RETRIES=5; \
    RETRY_DELAY=5; \
    for i in $(seq 1 $MAX_RETRIES); do \
        if apt-get update; then break; fi; \
        echo "apt-get update failed, retrying in $RETRY_DELAY seconds..."; \
        sleep $RETRY_DELAY; \
    done; \
    if [ $i -eq $MAX_RETRIES ]; then echo "apt-get update failed after $MAX_RETRIES retries, exiting."; exit 1; fi; \
    apt-get install -y iputils-ping curl && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit application code
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Command to run the Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
