# `contented`

This is a django project for delivery of data-analysis results (notebooks,
tables etc) in a user-authorised way: Only those users with access to a given
project should be able to view it's deliverables.

To use `contented`: fork the repository, add your analysis deliverables to the
`projects` subdirectory and then pull the modified repository onto a web-server
(details follow).

## ENV

Environment is managed by `pipenv`

`django 3.1.0` is used, as in "Django for Beginners" book by WS Vincent.

`black` is used for styling: installed it into the dev environment using
`pipenv install black --dev --pre`

`pylint` and `pylint_django` are used for linting

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

----

## Notes

This is my first (non-tutorial) Django project. So there may be much better
ways of achieving the project's goals.

- Github complained about the first push of this project since django
  `SECRET_KEY` was present in `config/settings.py`. Therefore, copied code from
  superlists project into settings.py (so the `SECRET_KEY` is obtained from
  os.environ)
