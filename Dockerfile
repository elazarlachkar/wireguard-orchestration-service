FROM python:3.10-alpine

COPY requirements.txt .
RUN pip3 install -r requirements.txt && rm requirements.txt

COPY ./src/ /app/
WORKDIR /app
ENTRYPOINT ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "main:app"]