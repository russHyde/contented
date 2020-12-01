"""
Functional tests for `contented` app-skeleton
"""

import time
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By


class NewVisitorTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_can_open_a_data_analysis_notebook(self):
        # Edith has heard about a cool new app that shows the results of data
        # analysis projects. She goes to check out its homepage.
        self.browser.get("http://localhost:8000")

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
        self.fail("Finish the test!")

        # Satisfied she goes back to sleep


if __name__ == "__main__":
    unittest.main()
