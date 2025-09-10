#!/usr/bin/env python3
# -- coding: utf-8 --

import curses
import sys
import locale

from ygreg.settings import Settings
from ygreg.file_selector import FileSelector
from ygreg.editor import Editor
from ygreg.screens import SettingsScreen, HelpScreen
from ygreg.themes import set_theme_colors

def main(stdscr):
    """Fonction principale qui orchestre l'application."""
    settings = Settings()
    current_screen = "file_selector"
    file_to_open = sys.argv[1] if len(sys.argv) > 1 else None

    while current_screen != "exit":
        set_theme_colors(settings.get("theme"))
        stdscr.bkgd(' ', curses.color_pair(0))
        
        if current_screen == "file_selector":
            if file_to_open:
                current_screen = "editor"
            else:
                file_to_open = FileSelector(stdscr, settings).run()
                current_screen = "editor" if file_to_open else "exit"

        elif current_screen == "editor":
            editor_instance = Editor(stdscr, file_to_open, settings)
            action = editor_instance.run()
            if action == "quit":
                file_to_open = None
                current_screen = "file_selector"
            else:
                current_screen = action

        elif current_screen == "settings":
            SettingsScreen(stdscr, settings).run()
            current_screen = "editor"

        elif current_screen == "help":
            HelpScreen(stdscr).run()
            current_screen = "editor"

if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, '')
    try:
        curses.wrapper(main)
    except curses.error as e:
        print(f"Erreur Curses: {e}\nVotre terminal n'est peut-être pas compatible, sa taille est trop petite, ou les couleurs 256 ne sont pas supportées.")
    except KeyboardInterrupt:
        print("\nSortie forcée.")