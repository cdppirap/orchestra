FROM python:3.8

RUN apt-get update && apt-get install vim -y > /dev/null

ARG ORCHESTRA_USER
ARG ORCHESTRA_GID
ARG ORCHESTRA_UID
ARG DOCKER_GID

RUN groupadd -g $ORCHESTRA_GID $ORCHESTRA_USER && \
    groupadd -g $DOCKER_GID docker && \
    useradd --gid $ORCHESTRA_GID -ms /bin/bash --uid $ORCHESTRA_UID $ORCHESTRA_USER && \
    usermod -aG docker $ORCHESTRA_USER && \
    echo '$ORCHESTRA_USER ALL=(ALL)       NOPASSWD: ALL' >> /etc/sudoers

RUN echo "orchestra_user: $ORCHESTRA_USER - orchestra_gid: $ORCHESTRA_GID - orchestra_uid: $ORCHESTRA_UID - docker_gid: $DOCKER_GID"
RUN grep $ORCHESTRA_USER /etc/passwd
RUN getent group docker

RUN mkdir -p /var/lib/orchestra/task_outputs && \
    chown -R $ORCHESTRA_USER:$ORCHESTRA_USER /var/lib/orchestra/task_outputs

RUN pip install --upgrade pip > /dev/null
USER $ORCHESTRA_USER

WORKDIR /home/$ORCHESTRA_USER
RUN git clone -b admin_website https://github.com/cdppirap/orchestra.git

WORKDIR /home/$ORCHESTRA_USER/orchestra

RUN pip install  --no-cache-dir -r requirements.txt --no-warn-script-location > /dev/null

EXPOSE 5000

CMD [ "/bin/bash", "./start_orchestra.sh"]
