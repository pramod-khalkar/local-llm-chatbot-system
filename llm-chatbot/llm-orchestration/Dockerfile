FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies with increased timeout
RUN pip install --default-timeout=1000 --retries 3 --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory for FAISS
RUN mkdir -p /data

# Expose port
EXPOSE 8001

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
