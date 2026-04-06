FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY alphagalleon-backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY alphagalleon-backend/app ./app

# Create .env placeholder
RUN echo "# Backend configuration\n\
CONVEX_URL=https://vibrant-spoonbill-564.eu-west-1.convex.cloud\n\
GOOGLE_API_KEY=\n\
UPSTOX_API_KEY=\n\
UPSTOX_API_SECRET=\n\
JWT_SECRET_KEY=change-this-to-random-value-in-production\n\
SERVER_HOST=0.0.0.0\n\
SERVER_PORT=8000" > .env.example

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
