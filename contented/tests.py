import os
from pathlib import Path
from django.urls import reverse
from django.test import TestCase


class HomePageTest(TestCase):

    path_to_projects = Path("dummy_projects")
    project_ids = os.listdir(path_to_projects)

    def test_uses_home_template(self):
        """
        WHEN: the user requests the home page (using `reverse("home")`)
        THEN: the home-page template is used
        """
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

        response = self.client.get(reverse("home"))
        response_text = response.content.decode("utf8")

        self.assertTrue(
            all([project_id in response_text for project_id in self.project_ids]),
            """A project-name was present in the project-directory, but absent
            from the home-page""",
        )

    def test_home_page_contains_hyperlinks_to_projects(self):
        hyperlink_stub = """<a href="/projects/{proj}">{proj}</a>"""

        response = self.client.get(reverse("home"))

        for project_id in self.project_ids:
            self.assertContains(
                response, hyperlink_stub.format(proj=project_id), html=True
            )


class ProjectPageTest(TestCase):

    path_to_projects = Path("dummy_projects")
    project_ids = os.listdir(path_to_projects)

    @staticmethod
    def get_relative_results_files(project_path):
        result_files = []
        for root, _, files in os.walk(project_path):
            relative_root = Path(root).relative_to(project_path)
            for my_file in files:
                result_files.append(str(relative_root / my_file))

        return result_files

    def test_uses_project_template(self):
        for project_id in self.project_ids:

            response = self.client.get(f"/projects/{project_id}")

            self.assertTemplateUsed(response, "project.html")

    def test_project_page_contains_project_id(self):
        for project_id in self.project_ids:

            response = self.client.get(f"/projects/{project_id}")
            response_text = response.content.decode("utf8")

            self.assertIn(project_id, response_text)

    def test_project_page_contains_list_of_results(self):
        """
        Every file that is in the project-directory for a given project should
        be mentioned on the project-page for that project
        """

        for project_id in self.project_ids:
            # GIVEN: a project name, and all the results files for that project
            # that are stored in the projects directory
            path_to_project = self.path_to_projects / project_id
            results_files = self.get_relative_results_files(path_to_project)

            # WHEN: the user opens that project's project-page
            response = self.client.get(f"/projects/{project_id}")
            response_text = response.content.decode("utf8")

            # THEN: all results-files for that project should be mentioned on
            # the project-page
            for file_name in results_files:
                self.assertIn(file_name, response_text)

    def test_project_page_contains_hyperlinks_to_results(self):
        """
        Every file that is in the project-directory for a given project should
        have a hyperlink on the project-page
        """
        for project_id in self.project_ids:
            # GIVEN: a project name, and all the results files for that project
            # that are stored in the projects directory
            path_to_project = self.path_to_projects / project_id
            results_files = self.get_relative_results_files(path_to_project)

            # WHEN: the user opens that project's project-page
            response = self.client.get(f"/projects/{project_id}")

            # THEN: there should be a hyperlink for each results-file from the
            # project-page
            hyperlink_stub = """<a href="/projects/{proj}/{file}">{file}</a>"""
            for my_file in results_files:
                self.assertContains(
                    response,
                    hyperlink_stub.format(proj=project_id, file=my_file),
                    html=True,
                )


class ResultsPageTest(TestCase):
    path_to_projects = Path("dummy_projects")
    project_ids = os.listdir(path_to_projects)

    def test_results_page_opens(self):
        response = self.client.get(f"/projects/my_test_project/abc.csv")

        self.assertEqual(response.status_code, 200)
