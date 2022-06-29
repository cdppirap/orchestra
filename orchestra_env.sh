# Project
export ORCHESTRA_BRANCH="with_flower" # admin_website
export ORCHESTRA_HOSTNAME=$HOSTNAME

# Orchestra user
export ORCHESTRA_USER=$USER
export ORCHESTRA_UID=$UID
export ORCHESTRA_GID=$(id -g $USER)

# Docker
export DOCKER_GID=$(getent group docker | cut -d: -f3)

# Postgresql database
export POSTGRESQL_DB=test_database #orchestra
export POSTGRESQL_USER=$USER #orchestra
export POSTGRESQL_PASSWORD= #orchestra
export POSTGRESQL_HOSTNAME=localhost
export POSTGRESQL_PORT=5432

# Redis server
export REDIS_HOSTNAME=localhost
export REDIS_PORT=6379

# Flask 
export FLASK_APP=orchestra.webservice
export FLASK_ENV=dev
export FLASK_DEBUG=0
export FLASK_HOST=0.0.0.0
export FLASK_PORT=5000


