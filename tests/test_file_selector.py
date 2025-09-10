import unittest
from unittest.mock import MagicMock, patch
from ygreg.file_selector import FileSelector
import curses

class TestFileSelector(unittest.TestCase):
    def setUp(self):
        self.mock_stdscr = MagicMock()
        self.mock_stdscr.getmaxyx.return_value = (24, 80)
        self.mock_settings = MagicMock()

        # Mock os functions to avoid actual filesystem access
        self.mock_listdir = patch('os.listdir', return_value=['file1.txt', 'dir1']).start()
        self.mock_isdir = patch('os.path.isdir', side_effect=lambda path: 'dir1' in path).start()
        self.mock_abspath = patch('os.path.abspath', side_effect=lambda path: path).start()
        self.mock_chdir = patch('os.chdir').start()
        self.mock_stat = patch('os.stat').start()

        self.addCleanup(patch.stopall)

        self.selector = FileSelector(self.mock_stdscr, self.mock_settings)
        self.selector._draw = MagicMock()

    @patch('curses.curs_set')
    def test_run_p_returns_settings(self, mock_curs_set):
        # Arrange
        self.mock_stdscr.getch.return_value = ord('p')

        # Act
        result = self.selector.run()

        # Assert
        self.assertEqual(result, "settings")

    @patch('curses.curs_set')
    def test_run_h_returns_help(self, mock_curs_set):
        # Arrange
        self.mock_stdscr.getch.return_value = ord('h')

        # Act
        result = self.selector.run()

        # Assert
        self.assertEqual(result, "help")

    @patch('curses.curs_set')
    def test_run_q_returns_none(self, mock_curs_set):
        # Arrange
        self.mock_stdscr.getch.return_value = ord('q')

        # Act
        result = self.selector.run()

        # Assert
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
