FROM python:3.7

RUN apt-get update && apt-get install vim -y

ARG ORCHESTRA_GID
ARG ORCHESTRA_UID
ARG DOCKER_GID

RUN groupadd -g $ORCHESTRA_GID orchestra && \
    groupadd -g $DOCKER_GID docker && \
    useradd --gid $ORCHESTRA_GID -ms /bin/bash --uid $ORCHESTRA_UID orchestra && \
    usermod -aG docker orchestra && \
    echo 'orchestra ALL=(ALL)       NOPASSWD: ALL' >> /etc/sudoers

RUN mkdir -p /orchestra_data/task_outputs && \
    chown -R orchestra:orchestra /orchestra_data

USER orchestra

WORKDIR /home/orchestra
RUN git clone -b with_docker_new_fix_bre https://github.com/cdppirap/orchestra.git

WORKDIR /home/orchestra/orchestra
COPY configuration.py orchestra/configuration.py
RUN pip install  --no-cache-dir -r requirements.txt

EXPOSE 6000

CMD [ "python3", "-m" , "orchestra.rest"]
