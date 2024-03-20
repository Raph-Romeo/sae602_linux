FROM python:3

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
RUN pip install nats-py

CMD ["python","-u","/app/script.py","nats://nats_server:4222","database"]
