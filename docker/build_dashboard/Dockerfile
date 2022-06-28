FROM python:3.8

RUN apt-get update > /dev/null 2>&1
RUN apt-get install git vim -y > /dev/null 2>&1 

#ARG ORCHESTRA_USER
#ARG ORCHESTRA_GID
#ARG ORCHESTRA_UID
#ARG DOCKER_GID
#ARG FLASK_PORT


RUN git clone -b admin_website https://github.com/cdppirap/orchestra.git > /dev/null 2>&1
WORKDIR orchestra

RUN pip install  --no-cache-dir -r requirements.txt --no-warn-script-location > /dev/null 2>&1 
RUN pip install flower

EXPOSE 5555

#RUN ls -ali
CMD ["celery --app orchestra.webservice.app.celery flower --broker=redis://redis:6379/0"]
