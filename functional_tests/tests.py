"""
Functional tests for `contented` app-skeleton
"""

from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings

from selenium import webdriver
from selenium.webdriver.common.by import By


class ProjectVisibilityTest(StaticLiveServerTestCase):
    """
    Ensure user can see projects that they are permitted to see; that they can
    navigate to results files etc
    """

    def setUp(self):
        self.browser = webdriver.Firefox()
        User.objects.create_user("edith", "edith@somewhere.net", "edithpassword")
        User.objects.create_user("fred", "fred@somewhere_else.com", "fredpassword")

    def tearDown(self):
        self.browser.quit()

    def test_can_open_a_data_analysis_notebook(self):
        """
        A user should be able to navigate to a project they are interested in
        and open an analysis notebook / results file in the browser
        """
        # Edith has heard about a cool new app that shows the results of data
        # analysis projects. She goes to check out its homepage.
        self.browser.get(self.live_server_url)

        # She notices the page title and header mention data analysis projects
        self.assertIn("Data Analysis Results", self.browser.title)
        header_text = self.browser.find_element(By.TAG_NAME, "h1").text
        self.assertIn("Data Analysis Results", header_text)

        # She notices there is a list of data analysis projects to look at
        table = self.browser.find_element(By.ID, "project_table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        self.assertIn("my_test_project", [row.text for row in rows])
        self.assertIn("my_other_project", [row.text for row in rows])

        # She enters the web-page for a particular analysis project and sees
        # the name of the project in the title
        project_link = self.browser.find_element(By.LINK_TEXT, "my_test_project")
        project_link.click()
        self.assertIn("Data Analysis Results: my_test_project", self.browser.title)
        header_text = self.browser.find_element(By.TAG_NAME, "h1").text
        self.assertIn("Data Analysis Results: my_test_project", header_text)

        # She sees there is a list of URLs: for documents, figures and
        # processed data
        results_table = self.browser.find_element(By.ID, "results_table")
        results_rows = results_table.find_elements(By.TAG_NAME, "tr")
        self.assertIn("README.md", [row.text for row in results_rows])
        self.assertIn("abc.csv", [row.text for row in results_rows])
        self.assertIn("my_subfolder/def.tsv", [row.text for row in results_rows])

        # She opens the webpage for an analysis report
        result_abc_link = self.browser.find_element(By.LINK_TEXT, "abc.csv")
        result_abc_link.click()
        self.assertIn("abc,123,345", self.browser.page_source)

        # Satisfied she goes back to sleep

    @override_settings(RESTRICTED_PROJECTS=["my_other_project"])
    def test_only_logged_in_users_can_see_restricted_projects(self):
        """
        Some projects in a project-collection may be flagged as restricted, and
        to access these projects a user needs to be logged in.
        """

        # Fred wants to check a report for the classified "my_other_project"
        restricted_project = "my_other_project"

        # He opens the URL for the homepage
        self.browser.get(self.live_server_url)

        # He notes that the classified project is not visible at the moment
        table = self.browser.find_element(By.ID, "project_table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        self.assertNotIn(restricted_project, [row.text for row in rows])

    #         # He opens the URL for logging in to the site
    #         self.browser.get(self.live_server_url + "/accounts/login/")
    #
    #         # He logs into the site, but uses the wrong password
    #         username_input = self.browser.find_element(By.NAME, "username")
    #         username_input.send_keys('fred')
    #         password_input = self.browser.find_element(By.NAME, "password")
    #         password_input.send_keys('not-freds-password')
    #         self.browser.find_element(By.XPATH, '//button[text()="Log In"]').click()
    #
    #         # After being redirected to the home page, he notes that the classified
    #         # project is not visible
    #         table = self.browser.find_element(By.ID, "project_table")
    #         rows = table.find_elements(By.TAG_NAME, "tr")
    #         self.assertNotIn(restricted_project, [row.text for row in rows])

        # He logs into the site with the correct password
        self.browser.get(self.live_server_url + "/accounts/login/")
        username_input = self.browser.find_element(By.NAME, "username")
        username_input.send_keys('fred')
        password_input = self.browser.find_element(By.NAME, "password")
        password_input.send_keys('fredpassword')
        self.browser.find_element(By.XPATH, '//button[text()="Log In"]').click()

        # After being redirected to the home-page, he notices the classified
        # project is visible
        table = self.browser.find_element(By.ID, "project_table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        self.assertIn(restricted_project, [row.text for row in rows])

        # He opens the project he wanted to view and stores it's URL for later
        # use
        self.browser.find_element(By.LINK_TEXT, restricted_project).click()
        restricted_url = self.browser.current_url
        header_text = self.browser.find_element(By.TAG_NAME, "h1").text
        self.assertIn(restricted_project, header_text)

        # He logs out of the site and is returned to the home page
        self.browser.find_element(By.XPATH, '//button[text()="Log Out"]').click()

        # Once again, the restricted project is no-longer visible in the
        # projects table
        table = self.browser.find_element(By.ID, "project_table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        self.assertNotIn(restricted_project, [row.text for row in rows])

        # He wonders whether he could access the project with it's URL if he
        # isn't logged in
        self.browser.get(restricted_url)
        header_text = self.browser.find_element(By.TAG_NAME, "h1").text
        self.assertNotIn(restricted_project, header_text)

        # Satisfied that people have to be logged in to access the report he
        # goes back to sleep
        self.fail("Finish the test!")
