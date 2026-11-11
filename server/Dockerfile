FROM python:3.12-slim

WORKDIR /app
COPY studyhub_server.py /app/studyhub_server.py

ENV DATA_DIR=/data \
    CONTENT_DIR=/content \
    PORT=8099 \
    PYTHONUNBUFFERED=1

VOLUME ["/data"]
EXPOSE 8099

CMD ["python", "/app/studyhub_server.py"]
