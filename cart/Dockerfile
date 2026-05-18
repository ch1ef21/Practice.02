FROM python:3.10-slim

WORKDIR /app

COPY cart/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY integrationLib/ ./integrationLib/
COPY mapping/ ./mapping/

COPY cart/ .

CMD ["python", "cartService.py"]