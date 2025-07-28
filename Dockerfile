FROM --platform=linux/amd64 python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY pdf_outline_extractor.py .

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Set permissions
RUN chmod +x pdf_outline_extractor.py

# Run the application
CMD ["python", "pdf_outline_extractor.py"]
