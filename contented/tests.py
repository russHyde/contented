import os
from django.test import TestCase


class HomePageTest(TestCase):
    def test_uses_home_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")

    def test_home_page_contains_list_of_projects(self):
        """
        Admin specifies a directory for presentation to the users; this
        directory comprises (possibly 0) a set of directories, one per
        data-analysis project. Each project should be accessible via the home
        page (ie, the name of the project should be visible)
        """

        path_to_projects = "dummy_projects"
        project_names = os.listdir(path_to_projects)

        response = self.client.get("/")
        response_text = response.content.decode("utf8")

        self.assertTrue(
            all([proj in response_text for proj in project_names]),
            """A project-name was present in the project-directory, but absent
            from the home-page""",
        )

    def test_home_page_contains_hyperlinks_to_projects(self):
        path_to_projects = "dummy_projects"
        project_names = os.listdir(path_to_projects)
        hyperlink_stub = """<a href="/projects/{proj}">{proj}</a>"""

        response = self.client.get("/")

        for proj in project_names:
            self.assertContains(response, hyperlink_stub.format(proj=proj), html=True)


class ProjectPageTest(TestCase):
    def test_uses_project_template(self):
        project_name = "my_test_project"

        response = self.client.get(f"/projects/{project_name}")

        self.assertTemplateUsed(response, "project.html")

    def test_project_page_contains_project_name(self):
        project_name = "my_test_project"

        response = self.client.get(f"/projects/{project_name}")
        response_text = response.content.decode("utf8")

        self.assertIn(project_name, response_text)
