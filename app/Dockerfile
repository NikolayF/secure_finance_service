FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip && pip install -r /app/requirements.txt

EXPOSE 8080

ENTRYPOINT ["/bin/bash"]

CMD ["-c", "python api.py"]
