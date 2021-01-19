"""
View functions for the home-page, project-pages and results-pages of a given
collection of projects
"""

import os
from pathlib import Path
from django.conf import settings
from django.shortcuts import render
from django.http import FileResponse, HttpResponse, HttpResponseRedirect


BINARY_EXTENSIONS = {
    ".pdf", ".jpeg", ".png", ".svg"
}

def home_page(request):
    """
    Home page displays a list of projects
    If the user is not logged in, only the non-restricted projects are shown
    Otherwise, all available projects are shown.
    """
    projects = get_accessible_projects(request.user)
    return render(request, "home.html", {"project_ids": projects})


def project_page(request, project_id):
    """
    Project page displays a list of the files that are available for a given
    project.
    If the user is not logged in and the project is restricted, the user is
    redirected to the log-in page when trying to open a given project page.
    """
    if not project_id in get_accessible_projects(request.user):
        return HttpResponseRedirect(settings.LOGIN_URL)

    project_collection = settings.PROJECTS_DIR
    project_path = project_collection / project_id
    project_files = get_relative_results_files(project_path)

    return render(
        request,
        "project.html",
        {"project_id": project_id, "results_files": [str(f) for f in project_files]},
    )


def results_page(request, project_id, file_name):
    """
    Selects an appropriate report / results file to display in the browser
    based on users-selection.

    If the user is not logged in, and the file is within a restricted project,
    then the user is redirected to the login page.
    """
    if not project_id in get_accessible_projects(request.user):
        return HttpResponseRedirect(settings.LOGIN_URL)

    project_collection = settings.PROJECTS_DIR
    file_path = project_collection / project_id / file_name

    _, file_extension = os.path.splitext(file_name)
    if file_extension in BINARY_EXTENSIONS:
        return FileResponse(open(file_path, "rb"))

    content_type = "text/html" if file_extension == ".html" else "text/plain"
    file_contents = ""
    with open(file_path, "r") as file_object:
        file_contents = file_object.read()

    return HttpResponse(file_contents, content_type=content_type)


# Helpers


def get_accessible_projects(user):
    """
    A logged-in user can view all projects, both restricted and non-restricted.
    A user who is not logged in can only view non-restricted projects.
    """
    project_collection = settings.PROJECTS_DIR
    projects = os.listdir(project_collection)
    if settings.RESTRICTED_PROJECTS and not user.is_authenticated:
        projects = [p for p in projects if p not in settings.RESTRICTED_PROJECTS]

    return projects


def get_relative_results_files(project_path):
    """
    For a given directory, `project_path`, return a list of `Path`s for all the
    files in or below that directory, relative to `project_path`

    That is, with,
    a/
      b/temp.txt
      c.tsv

    get_relative_results_path(Path("a"))
    should return [Path("b/temp.txt"), Path("c.tsv")]
    """
    result_files = []

    for root, _, files in os.walk(project_path):
        relative_root = Path(root).relative_to(project_path)
        for my_file in files:
            result_files.append(relative_root / my_file)

    return result_files
