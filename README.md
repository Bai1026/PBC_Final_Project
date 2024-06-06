# PBC_Final_Project
> Final Project of Programming for Business Computing, 2024
- Team 9
- Member: [Vincent Pai](https://github.com/Bai1026), [Max Liu](https://github.com/max09401), [Zoe Cheng](https://github.com/zoe891026), [Leona Hsu](https://github.com/Leonahsu)

## Our purpose:
- To build a exchange student matching platform.
- Built with Django and decorated with HTML and CSS.
  
## How to use:
- create a vitual environment
  ```bash
  conda create -n "env_name" python==3.9.12
  ```
  ```bash
  conda activate "env_name"
  ```
- Install the pip requirements
  ```bash
  pip install -r requirements.txt
  ```
- Further steps please refer to [platform folder](https://github.com/Bai1026/PBC_Final_Project/tree/main/platform)

## Architecture
```bash
└── platform: main folder of our project
    ├── avatars: store the avatar for each user
    ├── error_handlers: folder for error handling
    ├── friends: folder for all the friends data
    ├── login: folder for login page
    ├── matching: folder for welcome page
    ├── myproject: main folder contains settings and urls
    ├── templates: folder for all the HTML files
    ├── welcome: folder for welcome page
    ├
    ├── db.sqlite3: store the back-end data with sqlite
    ├── manage.py: the code to start the website
    ├── migrate.sh: shell script for migrate
    └── README.md  
```

```bash
└── each app(page) folder
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── tests.py
    ├── urls.py
    ├── views.py
    └── ...
```