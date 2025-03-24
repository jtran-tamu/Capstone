FROM python:3.13

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the container
COPY . /app/

# Expose the port Django runs on
EXPOSE 8080

# Run migrations and start the server
CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:8080"]