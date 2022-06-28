# Project
export ORCHESTRA_BRANCH="with_flower" # admin_website

# Orchestra user
export ORCHESTRA_USER=$USER
export ORCHESTRA_UID=$UID
export ORCHESTRA_GID=$(id -g $USER)

# Docker
export DOCKER_GID=$(getent group docker | cut -d: -f3)

# Postgresql database
export POSTGRESQL_DB=orchestra
export POSTGRESQL_USER=orchestra
export POSTGRESQL_PASSWORD=orchestra
export POSTGRESQL_HOSTNAME=localhost

# Redis server
export REDIS_HOSTNAME=localhost

# Flask 
export FLASK_APP=orchestra.webservice
export FLASK_ENV=dev
export FLASK_DEBUG=0
export FLASK_HOST=0.0.0.0
export FLASK_PORT=5000

# For debug
#echo "ORCHESTRA_USER: $ORCHESTRA_USER"
#echo "ORCHESTRA_UID: $ORCHESTRA_UID"
#echo "ORCHESTRA_GID: $ORCHESTRA_GID"
#echo ""
#echo "DOCKER_GID: $DOCKER_GID"
#echo ""
#echo "POSTGRESQL_USER: $POSTGRESQL_USER" 
#echo "POSTGRESQL_PASSWORD: $POSTGRESQL_PASSWORD"
#echo "POSTGRESQL_HOSTNAME: $POSTGRESQL_HOSTNAME"
#echo "POSTGRESQL_DB: $POSTGRESQL_DB"
#echo ""
#echo "REDIS_HOSTNAME: $REDIS_HOSTNAME"
#echo ""
#echo "FLASK_APP: $FLASK_APP"
#echo "FLASK_ENV: $FLASK_ENV"
#echo "FLASK_DEBUG: $FLASK_DEBUG"
