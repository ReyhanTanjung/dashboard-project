# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY app/ /app/
COPY templates/ /templates/
COPY databases/ /databases/

# Make sure the entry scripts are executable
RUN chmod +x /app/backend.py /app/mqtt-pub.py

# Run backend.py and mqtt-pub.py concurrently
CMD ["sh", "-c", "python /app/backend.py & python /app/mqtt-pub.py"]
