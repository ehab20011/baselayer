FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app

# Install postgresql-client to provide pg_isready
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Chromium for Playwright
RUN playwright install chromium

# Copy your application code
COPY . /app

# Ensure the script is executable
RUN chmod +x init_service.py

# Expose port 8000
EXPOSE 8000

CMD ["python", "init_service.py"]
