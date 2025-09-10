# -- coding: utf-8 --

import os

CONFIG_FILE = os.path.expanduser("~/.ygreg_cli_config.json")

LOREM_IPSUM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

PYTHON_KEYWORDS = {
    "def", "class", "if", "else", "elif", "for", "while", "return", "import",
    "from", "as", "with", "try", "except", "finally", "pass", "break",
    "continue", "in", "is", "not", "and", "or", "lambda", "yield", "True",
    "False", "None", "self", "async", "await"
}
JS_KEYWORDS = {
    "function", "var", "let", "const", "if", "else", "for", "while", "return",
    "import", "export", "from", "as", "with", "try", "catch", "finally",
    "switch", "case", "break", "continue", "in", "of", "new", "this",
    "true", "false", "null", "undefined", "async", "await", "class", "extends"
}
CSS_PROPERTIES = {
    "color", "background-color", "font-size", "font-family", "width", "height",
    "margin", "padding", "border", "display", "position", "top", "left",
    "right", "bottom", "flex", "grid", "align-items", "justify-content"
}
OPERATORS = r"[(){}[]=,.:;+\-*/%&|<>^@!]"

FILE_ICON_MAP = {
    ".py": ("🐍", 9), ".js": ("🟨", 9), ".html": ("🌐", 9), ".css": ("🎨", 9), ".json": ("🗃️", 9),
    ".c": ("🇨", 9), ".cpp": ("🇨", 9), ".java": ("☕", 9), ".sh": ("셸", 9), ".rb": ("💎", 9),
    ".php": ("🐘", 9), ".go": ("🐹", 9), ".rs": ("🦀", 9), ".swift": ("🐦", 9), ".ts": ("🔵", 9),
    ".csv": ("📊", 11), ".gitignore": ("🚫", 5), "dockerfile": ("🐳", 9), ".md": ("📝", 11),
    ".txt": ("📄", 11), ".pdf": ("📕", 11), ".doc": ("📃", 11), ".docx": ("📃", 11), ".xls": ("📈", 11),
    ".xlsx": ("📈", 11), ".ppt": ("📊", 11), ".pptx": ("📊", 11), ".png": ("🖼️", 10), ".jpg": ("🖼️", 10),
    ".jpeg": ("🖼️", 10), ".gif": ("🖼️", 10), ".svg": ("🖼️", 10), ".mp3": ("🎵", 10), ".wav": ("🎵", 10),
    ".mp4": ("🎬", 10), ".zip": ("📦", 12), ".tar": ("📦", 12), ".gz": ("📦", 12), ".rar": ("📦", 12),
    ".exe": ("⚙️", 12), ".bin": ("⚙️", 12), ".log": ("📜", 11),
}