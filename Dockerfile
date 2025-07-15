# Use the official Playwright image which has all browsers pre-installed
FROM mcr.microsoft.com/playwright/python:v1.53.0-jammy

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .

# Remove playwright from requirements.txt if it exists, since it's already in the base image
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
