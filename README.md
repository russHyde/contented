# `contented`

This is a django project for delivery of data-analysis results (notebooks,
tables etc) in a user-authorised way: Only those users with access to a given
project should be able to view it's deliverables.

To use `contented`:

- obtain a webserver, register a website domain and point the website URL to
  the webserver;
- put your analysis deliverables in a directory on the webserver;
- follow the provisioning notes in `./deploy_tools/provisioning_notes.md` (eg,
  install python / nginx etc on the webserver)
- run the fabric script in `./deploy_tools` - this will clone the `contented`
  repository onto the webserver, install the python env / update the database
  etc
- then add the filepath for your analysis deliverables to the `PROJECTS_DIR`
  environment variable defined in `./.env`

## ENV

Environment is managed by `pipenv`

`django 3.1.0` is used, as in "Django for Beginners" book by WS Vincent.

`black` is used for styling: installed it into the dev environment using
`pipenv install black --dev --pre`

`pylint` and `pylint_django` are used for linting

## CONFIG

A directory is specified by the superuser (as the `PROJECTS_DIR` environment
var on the webserver; to do this modify the value in `.env`) that contains all
projects that should be made visible: `PROJECTS_DIR`.

The default value of `PROJECTS_DIR` points to a set of projects that are used
during testing.

## Tests

`contented` is developed using TDD (based brazenly on the tests in TDD with
Python by H Percival). Write functional tests first, then unit tests, then
code.

`selenium` is used for functional testing
- Some differences between current selenium (4.0.0a7) and the one used in the
  TDD book project (3.141.0)
- Use `find_element(By.ID, "ID")` and `find_elements(By.TAG_NAME, "TAG-NAME")`
  instead of `find_element_by_id("ID")` and
  `find_elements_by_tag_name("TAG-NAME")` functions

Use Django test client to check that which templates are used in response to a
http request, eg, `self.client.get("/")`

Note you can use `@override_settings` decorator, if you want to change the
project data that is presented by `contented` during tests (plan is to use env
variable to define the location of the data that is presented; this env var
will be parsed by settings.py)

----

## Notes

This is my first (non-tutorial) Django project. So there may be much better
ways of achieving the project's goals.

- Github complained about the first push of this project since django
  `SECRET_KEY` was present in `config/settings.py`. Therefore, copied code from
  superlists project into settings.py (so the `SECRET_KEY` is obtained from
  os.environ)
