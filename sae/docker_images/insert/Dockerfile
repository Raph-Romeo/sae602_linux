FROM python:3

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
RUN pip install nats-py

CMD ["python","-u","/app/script.py", "nats://172.16.1.30:4222", "172.16.1.20"]
