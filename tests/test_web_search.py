import unittest
from unittest.mock import patch, MagicMock
from tools.web_search import WebSearchTool

class TestWebSearchTool(unittest.TestCase):
    def setUp(self):
        self.tool = WebSearchTool()

    @patch('tools.web_search.DDGS')
    def test_run_successful_search(self, MockDDGS):
        # Arrange
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = [
            {'title': 'Result 1', 'href': 'http://example.com/1', 'body': 'Snippet 1'},
            {'title': 'Result 2', 'href': 'http://example.com/2', 'body': 'Snippet 2'}
        ]
        MockDDGS.return_value.__enter__.return_value = mock_ddgs_instance

        query = "test query"
        expected_output = (
            "Result 1:\n"
            "  Title: Result 1\n"
            "  URL: http://example.com/1\n"
            "  Snippet: Snippet 1\n"
            "Result 2:\n"
            "  Title: Result 2\n"
            "  URL: http://example.com/2\n"
            "  Snippet: Snippet 2"
        )

        # Act
        result = self.tool.run(query=query)

        # Assert
        MockDDGS.assert_called_once()
        mock_ddgs_instance.text.assert_called_once_with(query, max_results=5)
        self.assertEqual(result, expected_output)

    @patch('tools.web_search.DDGS')
    def test_run_no_results(self, MockDDGS):
        # Arrange
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = []
        MockDDGS.return_value.__enter__.return_value = mock_ddgs_instance

        query = "no results query"
        expected_output = "No results found."

        # Act
        result = self.tool.run(query=query)

        # Assert
        MockDDGS.assert_called_once()
        mock_ddgs_instance.text.assert_called_once_with(query, max_results=5)
        self.assertEqual(result, expected_output)

    @patch('tools.web_search.DDGS')
    def test_run_error_during_search(self, MockDDGS):
        # Arrange
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.side_effect = Exception("Network error")
        MockDDGS.return_value.__enter__.return_value = mock_ddgs_instance

        query = "error query"
        expected_output_prefix = "An error occurred during the web search: Network error"

        # Act
        result = self.tool.run(query=query)

        # Assert
        MockDDGS.assert_called_once()
        mock_ddgs_instance.text.assert_called_once_with(query, max_results=5)
        self.assertTrue(result.startswith(expected_output_prefix))

if __name__ == '__main__':
    unittest.main()
