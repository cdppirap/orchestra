# move into the installation directory
cd /home/aschulz/Documents/python/orchestra

# source environment variables
. orchestra_env.sh

# activate the virtual environment
. venv/bin/activate
echo "[$(date --iso-8601=seconds)] Starting orchestra REST service" >> orchestra.log
#python -m orchestra.rest &
flask init-db
flask run

