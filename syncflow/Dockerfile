FROM python:3.12-slim

# control the buffering behavior of the standard streams (stdin, stdout, and stderr) within the Python process.
# helpful in real time logging
ENV PYTHONUNBUFFERED 1

# Create and set the working directory
RUN mkdir /app
# all  commands or instructions in the Dockerfile will be executed in the context of this directory, unless explicitly specified otherwise.
WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy the rest of your application code into the container
COPY . /app/

# Expose the port your application will run on (if applicable)
EXPOSE 8000

# Start your Django application in development mode
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
