## How to use
- `conda activate PBC`
- `python manage.py runserver` or `python3 manage.py runserver` to start the server
- type given 'url/login' to the log in page

- If we change the models.py in login folder
    - Which means that we change the architecture of the backend
        - We could see the log of changing in the login/migrations folder
    - `python manage.py makemigrations`
    - `python manage.py migrate`
    - or directly use migrate.sh by `./migrate.sh`
        - remember to `chmod +x migrate.sh` to open the execute mode.

## How to open a new app
- create app in a specified folder
```bash
python manage.py startapp 'myapp_name'
```
- to setting.py add the app u added
```bash
INSTALLED_APPS = [
    ...
    'myapp_name',
]
```

## How to open the Django shell
- `python manage.py shell` to open the shell

- create a superuser
```bash
python manage.py createsuperuser
```

- delete a superuser:
```bash
from django.contrib.auth.models import User
User.objects.filter(is_superuser=True).delete()
# or use the user name directly.
User.objects.get(username='your_super_username').delete()
```

- check the user condition
```bash
from django.contrib.auth.models import User
users = User.objects.all()
for user in users:
    print(user)
```

## Architecture
- All the HTML files are in [template](https://github.com/Bai1026/PBC_Final_Project/tree/main/platform/templates) folder
- ALl the css files are in [myproject/static/css](https://github.com/Bai1026/PBC_Final_Project/tree/main/platform/myproject/static/css) folder
