# Base image Python 3.11 (slim untuk ukuran kecil)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies untuk SQLite (biasanya sudah ada)
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Buat user non-root untuk security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

# Copy requirements dan install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Buat folder data dan set permissions
RUN mkdir -p /app/data && chown -R appuser:appuser /app/data

# Switch ke user non-root
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

# Run aplikasi
CMD ["python", "-m", "src.main"]
