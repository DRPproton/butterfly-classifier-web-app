# Use standard python image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies (required for some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files (db.sqlite3 will be included)
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --no-input

# Expose port (Render defaults to 10000, we'll map to PORT variable)
EXPOSE 8000

# Start server
# Using gunicorn and mapping to the dynamic PORT environment variable provided by Render
CMD ["sh", "-c", "python manage.py migrate && gunicorn ButterflyProject.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]
