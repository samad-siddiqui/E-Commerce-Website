# Use the official Python image from the Docker Hub
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Install dependencies for the system
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt file into the container
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the entire project into the container
COPY . /app/

# Expose the port that the Django app will run on
EXPOSE 8000

# Set the default command to run when the container starts
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]