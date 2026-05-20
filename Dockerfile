FROM python:3.12-slim

# Create non-root user
RUN groupadd --gid 1001 appuser \
    && useradd --uid 1001 --gid appuser --shell /bin/bash --create-home appuser

WORKDIR /app

# Install dependencies in a separate layer for cache efficiency
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Transfer ownership to non-root user
RUN chown -R appuser:appuser /app

USER appuser

CMD ["python", "main.py"]
