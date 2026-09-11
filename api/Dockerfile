FROM python:3.11-slim

WORKDIR /app

# Install dependencies first so Docker can cache this layer
# separately from code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and the trained model
COPY main.py .
COPY pipeline.pkl .

EXPOSE 8000

# Basic container-level healthcheck hitting our /health endpoint
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
