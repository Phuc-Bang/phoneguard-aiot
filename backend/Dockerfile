FROM python:3.10-slim

WORKDIR /app

# Install build dependencies if needed, then copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY . .

# Expose port 8000
EXPOSE 8000

ENV PYTHONUNBUFFERED=1

# Run FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
