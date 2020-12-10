"""
Tests for views:
- home-page (project-collection)
- project-page
- result-page
"""

import os

from pathlib import Path
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


def get_relative_results_files(project_path):
    """
    Return a list containing all files in the directory `project_path` and it's
    subdirectories. The files are specified relative to `project_path`.
    """
    result_files = []
    for root, _, files in os.walk(project_path):
        relative_root = Path(root).relative_to(project_path)
        for my_file in files:
            result_files.append(str(relative_root / my_file))

    return result_files


def get_collection_details(collection_id):
    """
    A collection is a directory containing projects (each of which is a
    directory).
    Given a collection_id, this returns
    - the path to the corresponding collection-directory;
    - the names of any projects within that directory;
    - and the relative-path for any project-associated files (as a dictionary).
    """
    path = Path(collection_id)
    project_ids = os.listdir(path)
    file_paths = {
        project_id: get_relative_results_files(path / project_id)
        for project_id in project_ids
    }
    return {"path": path, "project_ids": project_ids, "file_paths": file_paths}


class HomePageTest(TestCase):
    """
    The home-page for contented-based websites contains
    - a list of project-names.
    """

    def setUp(self):
        self.project_collections = {
            collection_id: get_collection_details(collection_id)
            for collection_id in ["dummy_projects", "dummy_projects2"]
        }
        User.objects.create_user(username="testuser1", password="not-a-password")

    def test_uses_home_template(self):
        """
        WHEN: the user requests the home page (using `reverse("home")`)
        THEN: the home-page template is used
        """
        for _, details in self.project_collections.items():
            with self.settings(PROJECTS_DIR=details["path"]):
                response = self.client.get(reverse("home"))
                self.assertTemplateUsed(response, "home.html")

    def test_alternative_url_specification_for_homepage(self):
        """
        WHEN: the user requests the home page (using `"/"`)
        THEN: the home-page template is used
        """
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")

    def test_home_page_contains_list_of_projects(self):
        """
        Admin specifies a directory for presentation to the users; this
        directory comprises (possibly 0) a set of directories, one per
        data-analysis project. Each project should be accessible via the home
        page (ie, the name of the project should be visible)
        """

        for _, details in self.project_collections.items():
            with self.settings(PROJECTS_DIR=details["path"]):

                response = self.client.get(reverse("home"))
                response_text = response.content.decode("utf8")

                self.assertTrue(
                    all(
                        [
                            project_id in response_text
                            for project_id in details["project_ids"]
                        ]
                    ),
                    """A project-name was present in the project-directory, but
                    absent from the home-page""",
                )

    def test_home_page_contains_hyperlinks_to_projects(self):
        """
        WHEN: the user opens the home-page
        THEN: a list of projects is visible and each one has an associated
        hyperlink
        """
        hyperlink_stub = """<a href="/projects/{proj}">{proj}</a>"""

        for _, details in self.project_collections.items():
            with self.settings(PROJECTS_DIR=details["path"]):

                response = self.client.get(reverse("home"))

                for project_id in details["project_ids"]:
                    self.assertContains(
                        response, hyperlink_stub.format(proj=project_id), html=True
                    )

    def test_unlogged_users_cannot_see_restricted_projects(self):
        """
        GIVEN: a user is not logged in
        WHEN: the user views the home page
        THEN: none of the restricted projects should be visible
        """
        collection_id = "dummy_projects"
        collection_details = self.project_collections[collection_id]
        restricted_projects = ["my_other_project"]

        hyperlink_stub = """<a href="/projects/{proj}">{proj}</a>"""

        with self.settings(
            PROJECTS_DIR=collection_details["path"],
            RESTRICTED_PROJECTS=restricted_projects,
        ):
            response = self.client.get(reverse("home"))

            for project_id in restricted_projects:
                self.assertNotContains(
                    response, hyperlink_stub.format(proj=project_id), html=True
                )

    def test_unlogged_users_can_see_all_open_projects(self):
        """
        GIVEN: a user is not logged in
        WHEN: the user views the home page
        THEN: all of the non-restricted projects should be visible
        """
        collection_id = "dummy_projects"
        collection_details = self.project_collections[collection_id]
        open_projects = ["my_test_project"]
        restricted_projects = ["my_other_project"]

        hyperlink_stub = """<a href="/projects/{proj}">{proj}</a>"""

        with self.settings(
            PROJECTS_DIR=collection_details["path"],
            RESTRICTED_PROJECTS=restricted_projects,
        ):
            response = self.client.get(reverse("home"))

            for project_id in open_projects:
                self.assertContains(
                    response, hyperlink_stub.format(proj=project_id), html=True
                )

    def test_logged_users_can_see_all_projects(self):
        """
        GIVEN: a logged-in user
        WHEN: the user views the home page
        THEN: all available projects should be visible
        """
        collection_id = "dummy_projects"
        collection_details = self.project_collections[collection_id]
        restricted_projects = ["my_other_project"]

        hyperlink_stub = """<a href="/projects/{proj}">{proj}</a>"""

        with self.settings(
            PROJECTS_DIR=collection_details["path"],
            RESTRICTED_PROJECTS=restricted_projects,
        ):
            self.client.login(username="testuser1", password="not-a-password")
            response = self.client.get(reverse("home"))

            for project_id in collection_details["project_ids"]:
                self.assertContains(
                    response, hyperlink_stub.format(proj=project_id), html=True
                )


class ProjectPageTest(TestCase):
    """
    The project-page is a webpage that contains
    - info about all files connected to a specific analysis project
    """

    def setUp(self):
        self.project_collections = {
            collection_id: get_collection_details(collection_id)
            for collection_id in ["dummy_projects", "dummy_projects2"]
        }

    def test_uses_project_template(self):
        """
        WHEN: the user requests the webpage for a specific project-ID
        THEN: the project-page template should be used
        """
        for _, details in self.project_collections.items():
            with self.settings(PROJECTS_DIR=details["path"]):
                for project_id in details["project_ids"]:

                    response = self.client.get(f"/projects/{project_id}")

                    self.assertTemplateUsed(response, "project.html")

    def test_project_page_contains_project_id(self):
        """
        WHEN: the user requests a webpage for a specific project-ID
        THEN: the project-ID should appear in the title of the webpage
        """
        for _, details in self.project_collections.items():
            with self.settings(PROJECTS_DIR=details["path"]):
                for project_id in details["project_ids"]:

                    response = self.client.get(f"/projects/{project_id}")
                    response_text = response.content.decode("utf8")

                    self.assertIn(project_id, response_text)

    def test_project_page_contains_list_of_results(self):
        """
        Every file that is in the project-directory for a given project should
        be mentioned on the project-page for that project
        """
        for _, details in self.project_collections.items():
            with self.settings(PROJECTS_DIR=details["path"]):
                for project_id in details["project_ids"]:
                    # GIVEN: a project name, and all the results files for that
                    # project that are stored in the projects directory
                    path_to_project = details["path"] / project_id
                    results_files = get_relative_results_files(path_to_project)

                    # WHEN: the user opens that project's project-page
                    response = self.client.get(f"/projects/{project_id}")
                    response_text = response.content.decode("utf8")

                    # THEN: all results-files for that project should be
                    # mentioned on the project-page
                    for file_name in results_files:
                        self.assertIn(file_name, response_text)

    def test_project_page_contains_hyperlinks_to_results(self):
        """
        Every file that is in the project-directory for a given project should
        have a hyperlink on the project-page
        """
        for _, details in self.project_collections.items():
            with self.settings(PROJECTS_DIR=details["path"]):
                for project_id in details["project_ids"]:
                    # GIVEN: a project name, and all the results files for that
                    # project that are stored in the projects directory
                    path_to_project = details["path"] / project_id
                    results_files = get_relative_results_files(path_to_project)

                    # WHEN: the user opens that project's project-page
                    response = self.client.get(f"/projects/{project_id}")

                    # THEN: there should be a hyperlink for each results-file
                    # from the project-page
                    hyperlink_stub = """<a href="/projects/{proj}/{file}">{file}</a>"""
                    for my_file in results_files:
                        self.assertContains(
                            response,
                            hyperlink_stub.format(proj=project_id, file=my_file),
                            html=True,
                        )

    # def test_nonexisting_projects_throw_404(self):
    #    response = self.client.get(f"/projects/not-a-project")
    #
    #    self.assertEqual(response.status_code, 404, f"Non-existing project")


class ResultsPageTest(TestCase):
    def setUp(self):
        self.project_collections = {
            collection_id: get_collection_details(collection_id)
            for collection_id in ["dummy_projects", "dummy_projects2"]
        }

    def test_results_page_opens(self):
        """
        WHEN: the user requests an existing file from a project
        THEN: the file should open in the browser
        """
        for _, details in self.project_collections.items():
            with self.settings(PROJECTS_DIR=details["path"]):
                for project_id, files in details["file_paths"].items():

                    for file_name in files:
                        url = f"/projects/{project_id}/{file_name}"
                        response = self.client.get(url)

                        self.assertEqual(
                            response.status_code, 200, f"Couldn't open {url}"
                        )

    def test_results_page_content_matches_file_content(self):
        """
        GIVEN: a file `<projects_dir>/<project_id>/<some_file>` exists

        WHEN: the user requests to see the URL corresponding to that file
        (/projects/<project_id>/<some_file>).

        THEN: the contents of the file should open in the browser and be
        identical to the original contents.
        """
        for _, details in self.project_collections.items():
            with self.settings(PROJECTS_DIR=details["path"]):
                for project_id, files in details["file_paths"].items():

                    for file_name in files:
                        file_path = details["path"] / project_id / file_name
                        url = f"/projects/{project_id}/{file_name}"

                        file_text = ""
                        with open(file_path, mode="r") as file_object:
                            file_text = file_object.read()
                        response = self.client.get(url)
                        response_text = response.content.decode("utf8")

                        self.assertEqual(response_text, file_text)
