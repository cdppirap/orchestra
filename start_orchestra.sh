# source environment variables
. orchestra_env.sh

# activate the virtual environment
echo "[$(date --iso-8601=seconds)] Starting orchestra REST service" >> orchestra.log
#python -m orchestra.rest &
flask init-db
flask run

