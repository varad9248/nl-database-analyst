# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependencies and install
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy application code
COPY main.py .

# Expose the FastAPI port
EXPOSE 8000

# Run the Uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]