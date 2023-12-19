FROM python:3.9-slim-buster

WORKDIR /etl

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .
CMD ["python3", "main.py"]