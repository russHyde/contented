"""
Functional tests for `contented` app-skeleton
"""

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By


class ProjectVisibilityTest(StaticLiveServerTestCase):
    """
    Ensure user can see projects that they are permitted to see; that they can
    navigate to results files etc
    """

    def setUp(self):
        self.browser = webdriver.Firefox()

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
