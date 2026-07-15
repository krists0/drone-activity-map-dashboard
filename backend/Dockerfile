# Use an official Python runtime environment as a parent image
FROM python:3.11-slim

# Set the working directory inside the docker container
WORKDIR /app

# Copy the requirements file into the container image layer
COPY requirements.txt .

# Install all python runtime service libraries
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend source files into the image setup
COPY . .

# Expose port 8000 for network communication links
EXPOSE 8000

# Fire up the live uvicorn application listener loop directly
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
