"""
Tests for views:
- home-page (project-collection)
- project-page
- result-page
"""

import os

from pathlib import Path
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
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


@override_settings(
    PROJECTS_DIR=Path("dummy_projects"),
    RESTRICTED_PROJECTS=["my_other_project"],
)
class HomePageRestrictionsTest(TestCase):
    """
    The project-names listed on contented-based websites comprises a set of
    openly-accessible and a set of restricted projects. Only logged-in users
    can access the restricted projects
    """

    def setUp(self):
        self.collection_id = "dummy_projects"
        self.collection_details = get_collection_details(self.collection_id)
        self.open_projects = ["my_test_project"]
        self.restricted_projects = ["my_other_project"]

        get_user_model().objects.create_user(
            username="testuser1", password="not-a-password"
        )

        self.hyperlink_stub = """<a href="/projects/{proj}">{proj}</a>"""

    def test_unlogged_users_cannot_see_restricted_projects(self):
        """
        GIVEN: a user is not logged in
        WHEN: the user views the home page
        THEN: none of the restricted projects should be visible
        """
        response = self.client.get(reverse("home"))

        for project_id in self.restricted_projects:
            self.assertNotContains(
                response, self.hyperlink_stub.format(proj=project_id), html=True
            )

    def test_unlogged_users_can_see_all_open_projects(self):
        """
        GIVEN: a user is not logged in
        WHEN: the user views the home page
        THEN: all of the non-restricted projects should be visible
        """
        response = self.client.get(reverse("home"))

        for project_id in self.open_projects:
            self.assertContains(
                response, self.hyperlink_stub.format(proj=project_id), html=True
            )

    def test_logged_users_can_see_all_projects(self):
        """
        GIVEN: a logged-in user
        WHEN: the user views the home page
        THEN: all available projects should be visible
        """
        self.client.login(username="testuser1", password="not-a-password")
        response = self.client.get(reverse("home"))

        for project_id in self.collection_details["project_ids"]:
            self.assertContains(
                response, self.hyperlink_stub.format(proj=project_id), html=True
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
        get_user_model().objects.create_user(
            username="testuser1", password="not-a-password"
        )

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
        GIVEN: a project name, and all the results files that are stored in the
        project's directory

        WHEN: the user opens that project's project-page

        THEN: each results-file should be mentioned in the text for the
        project-page (not tested: in a table)
        """

        def does_project_page_text_contain_file(project_id, file_path):
            # GIVEN: a project name, and one of the results files that are
            # stored in the project's directory

            # WHEN: the user opens that project's project-page
            response = self.client.get(f"/projects/{project_id}")
            response_text = response.content.decode("utf8")

            # THEN: the results-file should be mentioned on the project-page
            self.assertIn(file_path, response_text)

        def does_project_page_contain_list_of_all_results_files(details):
            for project_id, files in details["file_paths"].items():
                for file_path in files:
                    does_project_page_text_contain_file(project_id, file_path)

        for _, details in self.project_collections.items():
            with self.settings(PROJECTS_DIR=details["path"]):
                does_project_page_contain_list_of_all_results_files(details)

    def test_project_page_contains_hyperlinks_to_results(self):
        """
        GIVEN: a project name, and all the results files that are stored in the
        project's directory

        WHEN: the user opens that project's project-page

        THEN: there should be a hyperlink for each results-file from the
        project-page
        """

        def does_project_page_contain_hyperlink_to_file(project_id, file_path):
            hyperlink_stub = """<a href="/projects/{proj}/{file}">{file}</a>"""
            response = self.client.get(f"/projects/{project_id}")
            self.assertContains(
                response,
                hyperlink_stub.format(proj=project_id, file=file_path),
                html=True,
            )

        def does_project_page_contain_hyperlinks_to_all_results_files(details):
            for project_id, files in details["file_paths"].items():
                for file_path in files:
                    does_project_page_contain_hyperlink_to_file(project_id, file_path)

        for _, details in self.project_collections.items():
            with self.settings(PROJECTS_DIR=details["path"]):
                does_project_page_contain_hyperlinks_to_all_results_files(details)

    # def test_nonexisting_projects_throw_404(self):
    #    response = self.client.get(f"/projects/not-a-project")
    #
    #    self.assertEqual(response.status_code, 404, f"Non-existing project")

    @override_settings(
        PROJECTS_DIR=Path("dummy_projects"),
        RESTRICTED_PROJECTS=["my_other_project"],
    )
    def test_logged_in_users_can_open_restricted_projects(self):
        """
        GIVEN: a logged-in user and a restricted project

        WHEN: the user tries to open the URL for that project

        THEN: the project page opens without error
        """
        self.client.login(username="testuser1", password="not-a-password")
        url = reverse("project", args=["my_other_project"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, f"Couldn't open {url}")
        self.assertTemplateUsed(response, "project.html")

    @override_settings(
        PROJECTS_DIR=Path("dummy_projects"),
        RESTRICTED_PROJECTS=["my_other_project"],
    )
    def test_unlogged_users_cannot_open_restricted_projects(self):
        """
        GIVEN: a user who has not logged in and a restricted project

        WHEN: the user tries to open the URL for the project

        THEN: the user is redirected to the login page
        """
        url = reverse("project", args=["my_other_project"])
        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            302,
            "Couldn't redirect to login when accessing a restricted project",
        )
        # Wanted to test that registration/login.html template is used when
        # redirecting unlogged users, but when I use assertTemplateUsed it
        # claims that no templates were used when rendering; I suspect this is
        # because the page redirects rather than renders the chosen page.
        self.assertEqual(response.url, settings.LOGIN_URL)


class ResultsPageTest(TestCase):
    """
    The results page just shows the contents of a results-file in the browser.

    If a user is not logged in then only files from non-restricted projects can
    be displayed.
    """

    def setUp(self):
        self.project_collections = {
            collection_id: get_collection_details(collection_id)
            for collection_id in ["dummy_projects", "dummy_projects2"]
        }
        get_user_model().objects.create_user(
            username="testuser1", password="not-a-password"
        )

    def test_results_page_opens(self):
        """
        WHEN: the user requests an existing file from a project

        THEN: the file should open in the browser
        """

        def does_results_page_open(project_id, file_name):
            url = f"/projects/{project_id}/{file_name}"
            response = self.client.get(url)

            self.assertEqual(response.status_code, 200, f"Couldn't open {url}")

        def do_all_results_pages_open(details):
            for project_id, files in details["file_paths"].items():
                for file_name in files:
                    does_results_page_open(project_id, file_name)

        for _, details in self.project_collections.items():
            with self.settings(PROJECTS_DIR=details["path"]):
                do_all_results_pages_open(details)

    def test_results_page_matches_expected_content_type(self):
        """
        GIVEN: a file `<projects_dir>/<project_id>/<some_file>` exists

        WHEN: the user requests to see the URL corresponding to that file
        (/projects/<project_id>/<some_file>)

        THEN: the content-type for the response should make sense for the
        original file (if it's a pdf, html, txt ... file then the content-type
        should be application/pdf, text/html, text/plain)
        """
        # Take the default content-type to be text/plain
        content_types = {
            ".pdf": "application/pdf",
            ".html": "text/html",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".svg": "image/svg+xml",
        }

        def does_results_page_have_correct_content_type(project_id, file_name):
            _, extension = os.path.splitext(file_name)

            url = f"/projects/{project_id}/{file_name}"
            response = self.client.get(url)

            self.assertEqual(
                response["content-type"], content_types.get(extension, "text/plain")
            )

        def do_all_results_pages_have_correct_content_type(details):
            for project_id, files in details["file_paths"].items():
                for file_name in files:
                    does_results_page_have_correct_content_type(project_id, file_name)

        for _, details in self.project_collections.items():
            with self.settings(PROJECTS_DIR=details["path"]):
                do_all_results_pages_have_correct_content_type(details)

    def test_results_page_content_matches_file_content(self):
        """
        GIVEN: a file `<projects_dir>/<project_id>/<some_file>` exists

        WHEN: the user requests to see the URL corresponding to that file
        (/projects/<project_id>/<some_file>).

        THEN: the contents of the file should open in the browser and be
        identical to the original contents.
        """

        def is_binary(file_name):
            _, extension = os.path.splitext(file_name)
            binary_extensions = {".pdf", ".svg", ".png", ".jpeg"}

            return extension in binary_extensions

        def get_file_contents(file_path):
            file_text = ""
            file_mode = "rb" if is_binary(file_path) else "r"
            with open(file_path, mode=file_mode) as file_object:
                file_text = file_object.read()

            return file_text

        def get_response_contents(response, binary):
            if binary:
                return b"".join(response.streaming_content)

            return response.content.decode("utf8")

        def does_file_match_browser_contents(path, project_id, file_name):
            file_path = path / project_id / file_name
            url = f"/projects/{project_id}/{file_name}"

            file_text = get_file_contents(file_path)

            response = self.client.get(url)
            response_contents = get_response_contents(
                response, binary=is_binary(file_path)
            )

            self.assertEqual(response_contents, file_text)

        def do_all_files_match_their_browser_rendering(details):
            for project_id, files in details["file_paths"].items():
                for file_name in files:
                    does_file_match_browser_contents(
                        path=details["path"], project_id=project_id, file_name=file_name
                    )

        for _, details in self.project_collections.items():
            with self.settings(PROJECTS_DIR=details["path"]):
                do_all_files_match_their_browser_rendering(details)

    @override_settings(
        PROJECTS_DIR=Path("dummy_projects"),
        RESTRICTED_PROJECTS=["my_other_project"],
    )
    def test_logged_in_users_can_open_restricted_files(self):
        """
        GIVEN: a logged-in user and a file within a restricted project
        WHEN: the user tries to open the URL for that file
        THEN: the results file opens without error
        """
        self.client.login(username="testuser1", password="not-a-password")
        url = reverse("results", args=["my_other_project", "README.md"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, f"Couldn't open {url}")

    @override_settings(
        PROJECTS_DIR=Path("dummy_projects"),
        RESTRICTED_PROJECTS=["my_other_project"],
    )
    def test_unlogged_users_cannot_open_restricted_files(self):
        """
        GIVEN: a user who has not logged in and a file in a restricted project
        WHEN: the user tries to open the URL for the file
        THEN: the user is redirected to the login page
        """
        url = reverse("results", args=["my_other_project", "README.md"])
        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            302,
            "Couldn't redirect to login when accessing a restricted project",
        )
        self.assertEqual(response.url, settings.LOGIN_URL)
