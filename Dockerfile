FROM --platform=amd64 python:3.9.9-alpine

RUN apk update && apk add --no-cache --virtual build-deps gcc python3-dev musl-dev jpeg-dev zlib-dev libjpeg

EXPOSE 8080
WORKDIR /app

COPY requirements.txt .
COPY webapp/ .
RUN python -m pip install -r requirements.txt
RUN mkdir -p tmp/

RUN apk del build-deps

CMD ["python", "app.py"]

