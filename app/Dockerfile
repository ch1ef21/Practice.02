FROM python:3.10-slim

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org

COPY integrationLib/ ./integrationLib/

COPY app/ .

CMD ["python", "app.py"]