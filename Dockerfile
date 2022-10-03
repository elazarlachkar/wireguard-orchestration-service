FROM python:3.10-alpine

COPY requirements.txt .
RUN pip3 install -r requirements.txt && rm requirements.txt

COPY ./wireguard_orchestration/ /app/wireguard_orchestration/
WORKDIR /app
ENTRYPOINT ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "wireguard_orchestration.main:app"]