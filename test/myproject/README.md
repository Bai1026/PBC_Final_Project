## How to use
- `conda activate PBC`
- `python manage.py runserver` or `python3 manage.py runserver` to start the server
- type given 'url/login' to the log in page

- If click the log in button and not working
    - `python manage.py makemigrations`
    - `python manage.py migrate`

- How to open the Django shell
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
    print(user.username)
        ```