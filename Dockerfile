FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage cache
COPY requirements.txt .

# Install python dependencies
# Note: TTS might have conflicting dependencies, so we install it carefully.
# We install requirements.txt which includes litserve and TTS.
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY server.py .
COPY speakers .

# Expose port
EXPOSE 8000

# Run the server
CMD ["python", "server.py"]
