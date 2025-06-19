# coursera django project

Example Django App from Coursera Course
Link: https://www.coursera.org/professional-certificates/meta-back-end-developer

### Summary

Doing the final project as a refresher.

#### To build your python env and install packages

```
mkdir .venv
pipenv shell
pipenv install ___
```

#### To run app

```
# set up database w. dummy data
./loaddata.sh
```

then do:

```
python manage.py runserver
```

or hit f5.

#### testing

```
python -Wa manage.py test tests

# a specific test
python manage.py test LittlelemonAPI.tests.TestMenuItemsEndpoints.test_menu_items_post_admin_only
```

Backup database to fixtures:

```
python manage.py dumpdata auth > ./fixtures/littlelemon_auth.json
python manage.py dumpdata LittlelemonAPI > ./fixtures/littlelemon_api.json
python manage.py dumpdata contenttypes > ./fixtures/littlelemon_contenttypes.json
```

Personal notes: https://gist.github.com/ryansutc/64b3a4b17442cb50c75359dec3d96e6d
