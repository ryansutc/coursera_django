# coursera_django

Example Django App from Coursera Course
Link: https://www.coursera.org/professional-certificates/meta-back-end-developer

### Summary

Doing the final project as a refresher.

### To run

```
mkdir .venv
pipenv shell
pipenv install ___
```

```
python3 manage.py makemigrations # To compile the migrations
python3 manage.py migrate  # To migrate the changes in Database
```

```
python manage.py runserver
```

testing

```
python -Wa manage.py test tests
```

Backup database to fixtures:

```
python manage.py dumpdata auth > ./fixtures/littlelemon_auth.json
python manage.py dumpdata LittlelemonAPI > ./fixtures/littlelemon_api.json
python manage.py dumpdata contenttypes > ./fixtures/littlelemon_contenttypes.json
```

Personal notes: https://gist.github.com/ryansutc/64b3a4b17442cb50c75359dec3d96e6d
