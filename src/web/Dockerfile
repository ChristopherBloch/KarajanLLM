FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Environment
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Run with gunicorn - gevent workers for async, longer timeout
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--worker-class", "gevent", "--timeout", "300", "--keep-alive", "5", "--graceful-timeout", "120", "app:create_app()"]
