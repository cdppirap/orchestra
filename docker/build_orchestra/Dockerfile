FROM python:3.8

RUN apt-get update && apt-get install vim -y

ARG ORCHESTRA_GID
ARG ORCHESTRA_UID
ARG DOCKER_GID

RUN groupadd -g $ORCHESTRA_GID orchestra && \
    groupadd -g $DOCKER_GID docker && \
    useradd --gid $ORCHESTRA_GID -ms /bin/bash --uid $ORCHESTRA_UID orchestra && \
    usermod -aG docker orchestra && \
    echo 'orchestra ALL=(ALL)       NOPASSWD: ALL' >> /etc/sudoers

RUN mkdir -p /var/lib/orchestra/task_outputs && \
    chown -R orchestra:orchestra /var/lib/orchestra/task_outputs

RUN pip install --upgrade pip
USER orchestra

WORKDIR /home/orchestra
RUN git clone -b admin_website https://github.com/cdppirap/orchestra.git

WORKDIR /home/orchestra/orchestra

RUN pip install  --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD [ "/bin/bash", "./start_orchestra.sh"]
