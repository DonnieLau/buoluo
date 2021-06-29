redis-server &
python3 /opt/buoluo/manage.py celery -A buoluo worker -l info --beat &
python3 /opt/buoluo/manage.py runserver 0.0.0.0:8000
