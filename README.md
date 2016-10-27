# Simple i-gaming platform

## Installing
* Install `Python 3.5`, `pip`, `virtualenv`
* Create and activate virtualenv
```bash
virtualenv -p python3.5 venv
source venv/bin/activate
```

## Running development mode
* Set env variables
```bash
export WERKZEUG_DEBUG_PIN=off DEBUG=True
```
* Create database and superuser
```bash
python manage.py migrate
python manage.py createsuperuser
```
* Run tests
```bash
python manage.py runserver_plus
```
* Start server listening on http://127.0.0.1:8000
```bash
python manage.py runserver_plus 127.0.0.1:8000
```

## Running production mode
* Set env variables
```bash
unset WERKZEUG_DEBUG_PIN
unset DEBUG
export ALLOWED_HOSTS=example.com
````
* Start server listening on `/tmp/igaming_uwsgi.socket`
```bash
uwsgi --ini uwsgi.ini
```
