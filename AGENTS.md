# YGREG Project Documentation for Agents

## Project Overview

YGREG is a lightweight, console-based text editor written in Python using the `curses` library. It is designed to be simple, fast, and extensible. It includes a file explorer, syntax highlighting for several languages, and a variety of text editing features.

## Architecture

The project is structured into two main parts: the main script `ygreg_cli.py` and the `ygreg` package.

*   `ygreg_cli.py`: This is the main entry point of the application. It initializes the `curses` environment and manages the main application loop, which switches between different screens (file selector, editor, settings, help).

*   `ygreg/`: This is the main package containing all the application's logic.

    *   `__init__.py`: Makes the `ygreg` directory a Python package.
    *   `constants.py`: Contains all the constants used in the application, such as keywords, icons, and color maps.
    *   `editor.py`: This is the core of the text editor. The `Editor` class handles text manipulation, rendering, syntax highlighting, and user input.
    *   `file_selector.py`: Implements the `FileSelector` class, which provides a file explorer to browse, open, create, and delete files and directories.
    *   `screens.py`: Contains the classes for the secondary screens, such as the help screen (`HelpScreen`) and the settings screen (`SettingsScreen`).
    *   `settings.py`: The `Settings` class manages the application's settings, which are stored in a `config.json` file.
    *   `syntax.py`: This module contains the functions for syntax highlighting. Each supported language has its own highlighting function.
    *   `themes.py`: Manages the color themes for the application.
    *   `utils.py`: Contains utility functions shared across the application, such as the function to prompt for user input.

## How to Run the Application

To run the application, execute the `ygreg_cli.py` script from the root of the project:

```bash
python3 ygreg_cli.py
```

You can also open a file directly:

```bash
python3 ygreg_cli.py path/to/your/file.txt
```

## Main Features

### File Explorer

The file explorer is the default screen when the application starts. It allows you to navigate the file system, open files for editing, and perform basic file operations.

### Text Editor

The text editor supports a wide range of features, including:

*   **Syntax highlighting**: Automatically applied based on the file extension.
*   **Search and replace**: Accessible via the command mode (`Tab`).
*   **Clipboard**: Cut, copy, and paste functionality.
*   **Sorting**: Sort the current line, the entire document, or a range of lines.

### Command Mode

The command mode is accessed by pressing `Tab` in the editor. It provides a way to execute commands such as saving, quitting, searching, and more.

## Testing

The project uses the `unittest` framework for testing. To run the tests, use the following command from the root of the project:

```bash
python3 -m unittest discover tests
```

When adding new features, please add corresponding tests in the `tests` directory to ensure the code quality and prevent regressions.
