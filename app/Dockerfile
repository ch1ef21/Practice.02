FROM python:3.10-slim

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY integrationLib/ ./integrationLib/

COPY app/ .

CMD ["python", "app.py"]