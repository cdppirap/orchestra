# source environment variables
. orchestra_env.sh

# activate the virtual environment
echo "[$(date --iso-8601=seconds)] Starting orchestra REST service" >> orchestra.log
#python -m orchestra.rest &

# celery
python -m celery -A orchestra.webservice.app.celery worker --loglevel=info &

# webserver
python -m flask init-db
python -m flask run --host 0.0.0.0
#flask init-db
#flask run

