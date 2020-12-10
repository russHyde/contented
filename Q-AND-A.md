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

TODO

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
