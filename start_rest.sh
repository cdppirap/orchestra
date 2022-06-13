# move into the installation directory
cd /home/orchestra/orchestra/orchestra
# activate the virtual environment
. venv/bin/activate
echo "[$(date --iso-8601=seconds)] Starting orchestra REST service" >> orchestra.log
python -m orchestra.rest &

