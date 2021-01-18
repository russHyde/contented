# Questions and Answers

## ?? Non-authorised user cannot see projects that require authorisation

Want to have a functional test that does the following:

- Add an authorised user to the Users table
- Add a non-authorised user to the Users table
- Define a restricted project
- Define a non-restricted project

- Check that an unlogged-in user:
    - cannot see a restricted project, but can see an open project
    - cannot open any URL associated with a restricted project
    - can open a URL associated with an open project

- Check that an authorised user:
    - can see both restricted projects and open projects
    - can open a restricted project's URL

- Check that a non-authorised user:
    - cannot see a restricted project
    - cannot open any URL associated with that project

Therefore, need a test database for this test

### ?? Setting up a test database for use in Functional Tests

Initial functional test used `unittest.TestCase` and was ran using
`unittest.main()`. This is somewhat limited: it uses whatever database is
available to it, and it requires that the django server is running in the
background.

Here we require a test database, so we use django's LiveServerTestCase instead.
This makes a test database available and means that the local server does not
need to already be running.

The subclass `StaticLiveServerTestCase` ensures any static files are served
during testing (eg, any css / javascript); which may be useful for subsequent
tests. So we use that.

### ?? Running Functional Tests based on `StaticLiveServerTestCase`

When using `unittest.TestCase` we

- set up a local webserver to run in the background on port 8000 (`./manage.py
  runserver`)

- had a main block to run all tests defined in `./functional_tests.py`:

```
if __name__ == "__main__":
        unittest.main()
```

- ran the test script was using `python functional_tests.py`

- and all tests accessed the URL for the site using "http://localhost:8000"

Tests based on `StaticLiveServerTestCase`

- automatically set up a webserver (running on a random port)

- can be found automatically by the django test runner

- are ran using the django-test runner

- access the URL for the site using `self.live_server_url`

So, no main() block is required when running the functional tests, and the
tests are ran as follows:

```
# to run FTs in ./functional_tests.py
./manage.py test functional_tests

# note the absence of the .py extension
```

### ?? Adding, Authorising, Logging-in users within Tests

To add a user:

```
# From the Django docs
from django.contrib.auth.models import User
user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
```

Then in tests:

```
# where `self` is a subclass of `django.test.TestCase`
self.client.login(username="john", ...blah...)
```

To add a log-in page

- add `path("accounts/", include("django.contrib.auth.urls"))` to urlpatterns
- add a `login.html` file to `contented/templates/registration/`
- use Django's default login form in the html template
- add `LOGIN_REDIRECT_URL = "home"` to `config/settings.py`
- there is no reason to add a 'view' function/class

To use the login page within the functional tests, either:

- go to `self.live_server_url + "/accounts/login/"`
- or follow a "Log In" button from the home-page (this should redirect to
  `<home>/accounts/login`)

### ?? Setting access-restrictions for a project

Options:
- add a config entry that indicates which projects are restricted
- add a database model for projects
- add a restrictions.yaml to the project-collection directory
- add an environment variable containing the names of restricted projects (and
  parse it into the config)

In the first two cases would need to do some manual work to ensure a project is
accessible (ie, tinker with the code for contented or in the admin for the site)

For now, added `RESTRICTED_PROJECTS = []` to config; plan to update this based
on env-vars or project-collection-associated config file

### ?? Test a user is redirected to login when accessing a restricted project

- Add a restricted project to `RESTRICTED_PROJECTS` using `@override_settings`
- Try to access that restricted project via it's URL
- Check for redirection (code 302 = redirection)
- Planned: Check that template for login is used (ie, login.html)
    - note the latter did not work; when using assertTemplateUsed, the
      testrunner claimed that no template was used at all (rather than the
      login.html template; that the latter template is used can be seen in the
      browser)
- Therefore checked that the redirection URL matches the login URL

## How to style the website using bootstrap

Bootstrap v5-beta1 is the latest version (as of 2021-01-10)

Add bootstrap to ./static folder of the `contented` app (rather than using
downloading each time the site loads)

```
wget \
  -O bootstrap.zip \
  https://github.com/twbs/bootstrap/releases/download/v5.0.0-beta1/bootstrap-5.0.0-beta1-dist.zip
unzip bootstrap.zip
mkdir contented/static
mv bootstrap-5.0.0-beta1-dist contented/static/bootstrap
rm bootstrap.zip
```

Load the css into the `head` of the html files:

```
...
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="/static/bootstrap/css/bootstrap.min.css" rel="stylesheet">
</head>
...
```

Indicate that the bootstrap URL ("/static/bootstrap/css/bootstrap.min.css")
used in the above is for a static file, rather than html. If a URL starts with
the `STATIC_URL` defined in `config/settings.py` (ie, "/static/") then the URL
is a static and will be loaded.

(Ensure that `django.contrib.staticfiles` is in the `INSTALLED_APPS`, which it
is by default)

Rather than coding the `STATIC_URL` ("/static/") into the URLs for static
files, you can use the 'static' template tag in any .html files (this will
prepend the `STATIC_URL` to filenames)

```
{% load static %}
...
<link href={% static "bootstrap/css/bootstrap.min.css" %} rel="stylesheet">
```

Similarly, add this to the body of an .html file to load the bootstrap/popper
bundled javascript file:

```
<body>
...
  <script src="{% static 'bootstrap/js/bootstrap.bundle.min.js' %}"></script>
</body>
```

The static files shouldn't be served by django in production (django is slower
at this than nginx), so it's better to make a single directory where nginx can
deploy static files from. These files are collected into `STATIC_ROOT` by
django's `collectstatic` command. We set `STATIC_ROOT` to "{`base_dir`}/static"

```
# config/settings.py
...
STATIC_ROOT = os.path.join(BASE_DIR, "static")
```

Then collect the static files together:

```
./manage.py collectstatic
```

## ?? Deploy to staging server

Want to run tests against staging site: `contented-staging.russlearnsweb.co.uk`

To run the functional tests against that site from local computer:

Define the `live_server_url` to be "http://contented-staging..." for the
functional tests during test setUp (obtain the URL from an env variable).

```
STAGING_SERVER=contented-staging.russlearnsweb.co.uk \
  python manage.py test functional_tests
```

### Prerequisites

(Add the URL/IP-address for the staging site/server to the registrar)
(Add gunicorn to the environment for the project using `pipenv install gunicorn`)

### Provision the server & obtain code

SSH into the server (user login is controlled by secret key)

Ensure the server has the following available:

- `python 3.8` (python3 was installed when superlists was deployed on the
  server; note that it is run using `python3` not `python`); but the versions
  of python used in superlists and contented differ: superlists used python3.6
  (the version that runs when calling python3 on the server) and contented uses
  python3.8. (Later, running `pipenv install` failed because it
  couldn't install python3.8: pyenv or asdf are required for pipenv to install
  alternative python versions). Therefore installed `python3.8` using
  `sudo apt install python3.8`

- `pip`. It wasn't: superlists used venv, not pipenv; therefore installed using
  `sudo apt install python3-pip`

- `pipenv`. It wasn't: therefore installed using `pip3 install pipenv`; then
  logged back into the server.

- `nginx`

All django projects are stored in ~/sites/. Clone code from github:

```
export SITENAME=contented-staging.russlearnsweb.co.uk
git clone git@github.com:russHyde/contented.git ~/sites/${SITENAME}
```

### Build the environment and define env-variables (& how to run in that env)

Generate environment from Pipfile

```
cd ~/sites/${SITENAME}
pipenv install
```

Add `DJANGO_DEBUG_FALSE`, `SITENAME`, `DJANGO_SECRET_KEY` environment vars to
`~/sites/${SITENAME}/.env`

```
echo DJANGO_DEBUG_FALSE=y >> .env
echo SITENAME=${SITENAME} >> .env
echo DJANGO_SECRET_KEY=$(python3.8 -c"import Random; print(''.join(random.SystemRandom().choices('abcdefghijklmnopqrstuvwxyz0123456789', k=50)))") >> .env
```

pipenv defines the virtual env in `${HOME}/.local/share/virtualenvs/`

To run code in the environment defined by pipenv, either start a `pipenv shell`
and write commands within it, or use `pipenv run <command>`. pipenv will load
any env-vars defined in .env before calling the commands.

For example, this will run the Django webserver listening on port 8000

```
# on the server in ~/sites/${SITENAME}
pipenv run \
  ./manage.py runserver 0.0.0.0:8000
```

Then we can run the functional tests from the laptop:

```
# from the laptop, run tests against the django webserver that is running on
# the server
STAGING_SERVER=${SITENAME}:8000 \
  ./manage.py test functional_tests
```

Note that some functional tests may fail when called against the staging site
if they depend on modifying Django settings, or on the state of the server's
database.

### ?? Set up / configure webserver

Collect the static files from across the django project into `./static` so they
can be served by nginx

```
# from ~/sites/${SITENAME}
pipenv run \
  ./manage.py collectstatic --noinput
```

Configure nginx to listen on port 80 (as is typical for a webserver). Tell it
where to find the static files that we just collected and tell it to use a unix
socket (so that we can serve several sites from the same server; all requests
to port 80 will be proxied to this random port) and to pass the host headers on
from the original web request (otherwise it will look like requests came from
'localhost')

```
# Contents of /etc/nginx/sites-available/DOMAIN
# where we replace DOMAIN with contented-staging.russlearnsweb.co.uk
# and USER with my username
server {
  listen 80;
  server_name DOMAIN;

  location /static {
    alias /home/USER/sites/DOMAIN/static;
  }

  location / {
    proxy_pass http://unix:/tmp/DOMAIN.socket;
    proxy_set_header Host $host;
  }
}
```

Then set up a symlink from `/etc/nginx/sites-enabled/DOMAIN` to the
`sites-available` config file

Configure systemd to run gunicorn.

Note since `wsgi.py` is in the 'config' directory of contented, and since we've
just defined a unix socket for the site, we can serve the site by running:

```
sudo systemctl start nginx # or ... systemctl reload nginx

pipenv run \
  gunicorn --bind unix:/tmp/${SITENAME}.socket config.wsgi:application
```

We use systemd to ensure that gunicorn is started whenever the server reloads.
To do this, we add a systemd `.service` file for the site:

```
# /etc/systemd/system/gunicorn-${SITENAME}.service
# Replace DOMAIN with SITENAME and USER with my username
# If your wsgi.py is not at ./config/wsgi.py then change 'config.wsgi' to
# appropriate pathname
[Unit]
Description=Gunicorn server for DOMAIN

[Service]
Restart=on-failure
User=USER
WorkingDirectory=/home/USER/sites/DOMAIN
EnvironmentFile=/home/USER/sites/DOMAIN/.env
ExecStart=/home/USER/.local/bin/pipenv run \
  gunicorn --bind unix:/tmp/DOMAIN.socket \
  config.wsgi:application

[Install]
WantedBy=multi-user.target
```

Run nginx

```
sudo systemctl start nginx
```

Run gunicorn from a systemd process

```
sudo systemctl daemon-reload
sudo systemctl enable gunicorn-${SITENAME}
sudo systemctl start gunicorn-${SITENAME}
```

## Why does trying to open a .pdf fail with server error 500 after adding code
to handle FileResponse(open("pdf-file", "rb"))

Not sure why this was the case.

Each time I tried modifying the config, or code on the server to work out why
the pdf was not being served I just kept getting the same server-error 500.

That happened even if I hard-coded a HttpResponse("hello world") as the return
value for displaying a requested pdf.

Turned out that I had to restart gunicorn: changing the code is not enough for
the site to be updated. So make sure you rerun `sudo systemctl restart
gunicorn-<my-site>.service` if, after pulling new code onto the server, the
features you have added are not implemented on the website.
