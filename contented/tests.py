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
        response = self.client.get("/")
        response_text = response.content.decode("utf8")

        project_names = os.listdir(path_to_projects)

        self.assertTrue(
            all([proj in response_text for proj in project_names]),
            """A project-name was present in the project-directory, but absent
            from the home-page""",
        )
