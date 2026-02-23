# Use official Python image
FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project code
COPY . .

# Install the local package to expose the `coding-agent` command
RUN pip install --no-cache-dir -e .

# By default, show CLI help when container starts
CMD ["coding-agent", "--help"]
