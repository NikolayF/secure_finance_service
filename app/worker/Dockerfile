FROM python:3.11-slim

ARG RABBITMQ_PORT
ENV RABBITMQ_PORT=${RABBITMQ_PORT}

WORKDIR /app

COPY ../requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "worker.py"]