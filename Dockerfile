# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8001 available to the world outside this container
EXPOSE 8001

# Define environment variable
ENV LLM_PROFILES=local

# Run uvicorn when the container launches
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--reload", "--port", "8001"]
