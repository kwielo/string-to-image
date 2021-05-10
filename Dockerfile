FROM python:3.8.9-slim

EXPOSE 8080
WORKDIR /app

COPY requirements.txt .
COPY webapp/ .
RUN python -m pip install -r requirements.txt
RUN mkdir tmp/

CMD ["python", "app.py"]