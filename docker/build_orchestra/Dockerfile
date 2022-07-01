FROM python:3.8

RUN apt-get update > /dev/null 2>&1
RUN apt-get install vim -y > /dev/null 2>&1 

ARG ORCHESTRA_BRANCH
ARG ORCHESTRA_USER
ARG ORCHESTRA_GID
ARG ORCHESTRA_UID
ARG DOCKER_GID
ARG FLASK_PORT

RUN groupadd -g $ORCHESTRA_GID $ORCHESTRA_USER && \
 groupadd -g $DOCKER_GID docker && \
 useradd --gid $ORCHESTRA_GID -ms /bin/bash --uid $ORCHESTRA_UID $ORCHESTRA_USER && \
 usermod -aG docker $ORCHESTRA_USER && \
 echo '$ORCHESTRA_USER ALL=(ALL)       NOPASSWD: ALL' >> /etc/sudoers && \
 mkdir -p /var/lib/orchestra/task_outputs && \
 chown -R $ORCHESTRA_USER:$ORCHESTRA_USER /var/lib/orchestra && \
 chmod -R 777 /var/lib/orchestra

RUN pip install --upgrade pip > /dev/null 2>&1
USER $ORCHESTRA_USER

WORKDIR /home/$ORCHESTRA_USER
RUN git clone -b $ORCHESTRA_BRANCH https://github.com/cdppirap/orchestra.git > /dev/null 2>&1

WORKDIR /home/$ORCHESTRA_USER/orchestra

RUN pip install  --no-cache-dir -r requirements.txt --no-warn-script-location > /dev/null 2>&1 

EXPOSE $FLASK_PORT

CMD [ "/bin/bash", "./start_orchestra.sh"]
