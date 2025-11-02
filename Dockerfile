# Use official Python image
FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project code
COPY . .

# By default, show CLI help when container starts
CMD ["python", "cli.py", "--help"]
