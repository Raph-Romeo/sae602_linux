FROM python:3.11

ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND moninteractive
ENV PYTHONPATH /usr/local/lib/python3.11/site-packages:/usr/local/lib/python3.11:/app/base

RUN apt-get update && apt-get install -y apache2 && apt-get install -y build-essential apache2-dev && apt-get install -y libapache2-mod-wsgi-py3
RUN a2enmod wsgi
RUN mkdir /app

WORKDIR /app
COPY . /app
RUN chmod -R a+r /app
RUN chmod -R +rx /app/base/
RUN chown -R www-data:www-data /app
RUN pip install -r requirements.txt
RUN pip install nats-py
RUN echo LoadModule wsgi_module modules/mod_wsgi.so >> /etc/apache2/apache2.conf

COPY apache-config.conf /etc/apache2/sites-available/000-default.conf

EXPOSE 80
