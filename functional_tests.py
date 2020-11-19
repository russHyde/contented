"""
Functional tests for `contented` app-skeleton
"""

from selenium import webdriver
import time
import unittest


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
        header_text = self.browser.find_element_by_tag_name("h1").text
        self.assertIn("Data Analysis Results", header_text)

        # She notices there is a list of data analysis projects to look at
        table = self.browser.find_element_by_id("project_table")
        rows = table.find_elements_by_tag_name("tr")
        self.assertTrue(any(row.text == "my_test_project" for row in rows))

        # She enters the web-page for a particular analysis project
        self.fail("Finish the test!")

        # She sees there is a list of URLs: for documents, figures and
        # processed data

        # She opens the webpage for an analysis report

        # Satisfied she goes back to sleep


if __name__ == "__main__":
    unittest.main()
