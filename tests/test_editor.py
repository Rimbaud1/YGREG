import unittest
from unittest.mock import MagicMock, patch
from ygreg.editor import Editor

class TestEditor(unittest.TestCase):
    def setUp(self):
        self.mock_stdscr = MagicMock()
        self.mock_settings = MagicMock()
        self.mock_settings.get.return_value = 4  # tab_size
        self.file_path = "test.txt"

        # We need to mock open, so we can control the content of the file
        mock_open = unittest.mock.mock_open(read_data="line 1\nline 3\nline 2")
        with patch("builtins.open", mock_open):
            self.editor = Editor(self.mock_stdscr, self.file_path, self.mock_settings)

        self.editor._set_status_message = MagicMock()

    @patch('ygreg.editor.prompt_input')
    def test_sort_lines_current_line(self, mock_prompt_input):
        # Arrange
        self.editor.lines = ["c b a"]
        self.editor.cursor_y = 0
        mock_prompt_input.return_value = 'a'

        # Act
        self.editor._sort_lines()

        # Assert
        self.assertEqual(self.editor.lines[0], "a b c")
        self.assertTrue(self.editor.modified)
        self.editor._set_status_message.assert_called_with("Ligne actuelle ordonnée")

    @patch('ygreg.editor.prompt_input')
    def test_sort_lines_all_document(self, mock_prompt_input):
        # Arrange
        self.editor.lines = ["c", "a", "b"]
        mock_prompt_input.return_value = 't'

        # Act
        self.editor._sort_lines()

        # Assert
        self.assertEqual(self.editor.lines, ["a", "b", "c"])
        self.assertTrue(self.editor.modified)
        self.editor._set_status_message.assert_called_with("Document ordonné")

    @patch('ygreg.editor.prompt_input')
    def test_sort_lines_line_range(self, mock_prompt_input):
        # Arrange
        self.editor.lines = ["z", "c", "a", "b", "y"]
        mock_prompt_input.side_effect = ['l', '2', '4']

        # Act
        self.editor._sort_lines()

        # Assert
        self.assertEqual(self.editor.lines, ["z", "a", "b", "c", "y"])
        self.assertTrue(self.editor.modified)
        self.editor._set_status_message.assert_called_with("Lignes 2 à 4 ordonnées")

    @patch('ygreg.editor.prompt_input')
    def test_sort_lines_invalid_range(self, mock_prompt_input):
        # Arrange
        self.editor.lines = ["z", "c", "a", "b", "y"]
        self.editor.modified = False
        mock_prompt_input.side_effect = ['l', '10', '20']

        # Act
        self.editor._sort_lines()

        # Assert
        self.assertEqual(self.editor.lines, ["z", "c", "a", "b", "y"]) # unchanged
        self.assertFalse(self.editor.modified)
        self.editor._set_status_message.assert_called_with("Plage de lignes invalide")

    @patch('ygreg.editor.prompt_input')
    def test_sort_lines_case_insensitive(self, mock_prompt_input):
        # Arrange
        self.editor.lines = ["C", "a", "b"]
        mock_prompt_input.return_value = 't'

        # Act
        self.editor._sort_lines()

        # Assert
        self.assertEqual(self.editor.lines, ["a", "b", "C"])
        self.assertTrue(self.editor.modified)
        self.editor._set_status_message.assert_called_with("Document ordonné")

if __name__ == '__main__':
    unittest.main()
