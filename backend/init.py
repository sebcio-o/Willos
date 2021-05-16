import os

os.system("python manage.py makemigrations")
os.system("python manage.py migrate --noinput")
os.system("python manage.py collectstatic --noinput")
os.system("python manage.py createsuperuser")
