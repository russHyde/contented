Provisioning a new `contented` site
===================================

## Required packages:

* nginx
* python 3.8
* pip + pipenv
* git

eg, on Ubuntu:
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install nginx git python38 python3-pip
    `pip3 install pipenv`

## Obtain code

* Pull down 'contented' from github

## Build environment

* From ~/sites/DOMAIN run `pipenv install`

## Collect static files

* From ~/sites/DOMAIN run `pipenv run ./manage.py collectstatic`

## Nginx Virtual Host config

* see nginx.template.conf
* replace DOMAIN with your site's URL
* replace USER with your username

## Systemd service

* see gunicorn-systemd.template.service
* replace DOMAIN with your site's URL
* replace USER with your username

## Folder structure:

Assume we have a user account at /home/username

/home/username
|-  sites
    |-  DOMAIN1
    |   |- .env
        |- db.sqlite3
        |- manage.py etc
        |- static/
        -- Pipfile / Pipfile.lock
