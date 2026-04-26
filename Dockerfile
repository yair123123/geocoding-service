FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/geocoding-service

WORKDIR /opt/geocoding-service

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8080

CMD ["uvicorn", "--app-dir", "/opt/geocoding-service", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
