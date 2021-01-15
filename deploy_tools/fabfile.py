"""
Fabric file for connecting to a server and deploying a django app.

This django app uses pipenv and a server-localised .env file for defining the
python environment and any environment variables.

Call this using
fab deploy:host=<username>@<url>
... where
    - url is the name of the website (eg, cml-stem-cell.russlearnsweb.co.uk)
    - and username is your username on the server that hosts that website
"""

import random
from fabric.contrib.files import append, exists
from fabric.api import cd, env, local, run

REPO_URL = "git@github.com:russHyde/contented.git"


def deploy():
    """
    Connect to a server and deploy this django project
    """
    site_folder = f"/home/{env.user}/sites/{env.host}"
    run(f"mkdir -p {site_folder}")
    with cd(site_folder):
        _get_latest_source()
        _update_pipenv()
        _create_or_update_dotenv()
        _update_static_files()
        _update_database()


def _get_latest_source():
    """
    Download the source code onto the server and checkout the commit that
    matches the most recent commit on the local computer.
    """
    if exists(".git"):
        run("git fetch")
    else:
        run(f"git clone {REPO_URL} .")

    current_commit = local("git log -n 1 --format=%H", capture=True)
    run(f"git reset --hard {current_commit}")


def _update_pipenv():
    """
    Ensure the pipenv for the project matches the environment defined in
    Pipfile
    """
    run("pipenv install")


def _create_or_update_dotenv():
    """
    Define environment variables for use when running this django project
    """
    append(".env", "DJANGO_DEBUG_FALSE=y")
    append(".env", f"SITENAME={env.host}")
    current_contents = run("cat .env")
    if "DJANGO_SECRET_KEY" not in current_contents:
        new_secret = _random_key()
        append(".env", f"DJANGO_SECRET_KEY={new_secret}")


def _update_static_files():
    """
    Put all static files (.css / .js) into the directory ./static so that nginx
    can serve them
    """
    run("pipenv run ./manage.py collectstatic --noinput")


def _update_database():
    """
    Run all database migrations
    """
    run("pipenv run ./manage.py migrate --noinput")


def _random_key():
    """
    Make a random string of length 50, using alphanumeric characters
    """
    key = "".join(
        random.SystemRandom().choices("abcdefghijklmnopqrstuvwxyz0123456789", k=50)
    )
    return key
