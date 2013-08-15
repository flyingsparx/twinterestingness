uwsgi --logto /dev/null --socket 127.0.0.1:3033 --file app.py --callable app --processes 2
