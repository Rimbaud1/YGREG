# -- coding: utf-8 --

import curses

def prompt_input(stdscr, prompt):
    """Affiche un prompt en bas de l'écran et retourne l'entrée de l'utilisateur."""
    try:
        height, width = stdscr.getmaxyx()
        stdscr.attron(curses.color_pair(1))
        prompt_line = prompt.ljust(width - 1)
        stdscr.addstr(height - 1, 0, prompt_line)
        stdscr.attroff(curses.color_pair(1))
        
        # Activer le curseur et l'écho pour la saisie
        curses.curs_set(1)
        curses.echo()
        stdscr.keypad(False)
        stdscr.nodelay(False)
        
        input_str = stdscr.getstr(height - 1, len(prompt)).decode('utf-8')
        
        # Rétablir les paramètres normaux
        stdscr.nodelay(True)
        stdscr.keypad(True)
        curses.noecho()
        curses.curs_set(0)
        
        return input_str
    except curses.error:
        return ""