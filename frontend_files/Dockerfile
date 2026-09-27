
# Use a lightweight Python base image
FROM python:3.9-slim-bullseye

# Set non-interactive frontend for apt-get commands
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory in the container
WORKDIR /app

# Update package lists and install network utilities (ping, curl)
# Ensure full cache cleanup before and after to prevent issues with stale package references
# Removed 'apt-get upgrade -y' as it was causing 404 errors for security packages.
RUN set -ex; \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get update && \
    apt-get install -y --no-install-recommends iputils-ping curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit application code
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Command to run the Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
