# Base image
FROM python:3.13-slim

# Install Chromium and other necessary tools
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    wget \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set environment variable for headless Chrome
ENV CHROME_BIN=/usr/bin/chromium

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
