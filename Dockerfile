# Use the official Python image
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    default-libmysqlclient-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /usr/src/app

# Copy the requirements file to install dependencies
COPY req.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r req.txt

# Copy the entire application code into the container
COPY . .

# Collect static files (if applicable)
RUN python manage.py collectstatic --noinput

# Expose the application's port
EXPOSE 8000

# Set the command to start the application with Gunicorn and Uvicorn Worker
CMD ["gunicorn", "core.asgi:application", "-w", "3", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
