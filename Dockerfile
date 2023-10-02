# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

ENV PORT 80

EXPOSE $PORT

CMD ["python", "start_api.py"]
