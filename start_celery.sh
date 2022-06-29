. venv/bin/activate

#celery -A orchestra.webservice.app.celery worker --loglevel=info

# auto restart on code change
watchmedo auto-restart --directory=./orchestra/ --pattern=*.py --recursive -- celery -A orchestra.webservice.app.celery worker --loglevel=info

