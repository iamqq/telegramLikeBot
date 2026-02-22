FROM python:3.7-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure the database file is not overwritten if a volume is mounted, 
# but we need the sql file to initialize it if it doesn't exist.

CMD ["python", "server.py"]
