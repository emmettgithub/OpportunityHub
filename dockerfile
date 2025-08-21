# Use official Python slim image
FROM python:3.13-slim

# -------------------- Install dependencies --------------------
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    software-properties-common \
    chromium \
    chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# -------------------- Set working directory --------------------
WORKDIR /app

# -------------------- Copy requirements and install --------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -------------------- Copy app code --------------------
COPY . .

# -------------------- Environment variables --------------------
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# -------------------- Expose Flask port --------------------
EXPOSE 5000

# -------------------- Run Flask --------------------
CMD ["flask", "run"]
