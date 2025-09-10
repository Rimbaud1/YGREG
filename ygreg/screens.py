# -- coding: utf-8 --

import curses
from .themes import set_theme_colors

class SettingsScreen:
    def __init__(self, stdscr, settings):
        self.stdscr, self.settings = stdscr, settings
        self.options = [
            {"key": "theme", "label": "Thème de couleurs", "values": ["dark", "light", "ocean", "synthwave"]},
            {"key": "autosave_threshold", "label": "Autosave (0=désactivé)", "values": [0, 10, 25, 50, 100]},
            {"key": "show_syntax_highlighting", "label": "Coloration syntaxique", "values": [True, False]},
            {"key": "tab_size", "label": "Taille tabulation", "values": [2, 4, 8]}
        ]
        self.selected_option = 0

    def run(self):
        curses.curs_set(0)
        while True:
            try:
                set_theme_colors(self.settings.get("theme"))
                self.stdscr.erase()
                self._draw()
                self.stdscr.refresh()
            except curses.error: pass

            key = self.stdscr.getch()
            if key == ord('q'): break
            elif key == curses.KEY_UP: self.selected_option = max(0, self.selected_option - 1)
            elif key == curses.KEY_DOWN: self.selected_option = min(len(self.options) - 1, self.selected_option + 1)
            elif key in [curses.KEY_RIGHT, curses.KEY_LEFT, 10, 13]:
                opt = self.options[self.selected_option]
                current_val = self.settings.get(opt['key'])
                try:
                    idx = opt['values'].index(current_val)
                    direction = 1 if key in [curses.KEY_RIGHT, 10, 13] else -1
                    new_idx = (idx + direction) % len(opt['values'])
                    self.settings.set(opt['key'], opt['values'][new_idx])
                except ValueError: pass

    def _draw(self):
        h, w = self.stdscr.getmaxyx()
        self.stdscr.attron(curses.color_pair(3)); self.stdscr.box(); self.stdscr.attroff(curses.color_pair(3))
        title = " YGREG - Paramètres "
        self.stdscr.addstr(0, (w-len(title))//2, title, curses.A_BOLD)

        for i, opt in enumerate(self.options):
            val = self.settings.get(opt['key'])
            val_str = f"< {str(val):^7} >"
            line_str = f"{opt['label'].ljust(30)} {val_str}"
            attr = curses.A_REVERSE if i == self.selected_option else curses.A_NORMAL
            self.stdscr.addstr(i + 4, (w - len(line_str))//2, line_str, attr)
        
        help_text = "Q: Retour | ↑↓: Naviguer | ←→/Entrée: Changer"
        self.stdscr.addstr(h-1, (w-len(help_text))//2, help_text, curses.color_pair(2))

class HelpScreen:
    def __init__(self, stdscr):
        self.stdscr = stdscr

    def run(self):
        curses.curs_set(0)
        while True:
            try:
                self.stdscr.erase()
                self._draw()
                self.stdscr.refresh()
            except curses.error: pass
            if self.stdscr.getch() in [ord('q'), 10, 13]:
                break

    def _draw(self):
        h, w = self.stdscr.getmaxyx()
        self.stdscr.attron(curses.color_pair(3)); self.stdscr.box(); self.stdscr.attroff(curses.color_pair(3))
        self.stdscr.addstr(0, (w-16)//2, " YGREG - Aide ", curses.A_BOLD)
        
        # MODIFIÉ: Mise à jour du contenu de l'aide
        help_content = [
            ("--- Navigation & Commandes (Tab > Touche) ---", ""),
            ("s: Sauvegarder",         "q: Quitter"),
            ("h: Afficher cette aide", "p: Paramètres"),
            ("f: Rechercher",          "r: Remplacer"),
            ("g: Aller à la ligne",    ""),
            ("", ""),
            ("--- Édition & Sélection ---", ""),
            ("Shift+Flèches: Sélectionner",     "x/c/v: Couper/Copier/Coller"),
            ("Entrée sur sélection: Casser la ligne", "Tab/Shift+Tab: Indenter/Désindenter"),
            ("d: Dupliquer ligne/sélection", "j: Joindre avec la ligne suivante"),
            ("o: Ordonner la sélection", ""), # MODIFIÉ: 's' devient 'o'
            ("", ""),
            ("--- Générateurs & Outils (Taper mot + Tab) ---", ""),
            ("=' (ex: 5*sin(pi/2)=)", "Calcule le résultat de l'expression"),
            ("date / heure", "Insère la date / l'heure actuelle"),
            ("uuid", "Insère un identifiant unique"),
            ("lorem<N>", "Insère N mots de Lorem Ipsum (ex: lorem20)"),
            ("t (via Tab>t)", "Insère un modèle de tableau"),
        ]

        y = 2
        for item in help_content:
            if y >= h - 2: break
            if isinstance(item, str):
                self.stdscr.addstr(y, 4, item, curses.A_BOLD)
            else:
                col1, col2 = item
                self.stdscr.addstr(y, 4, col1)
                if col2: self.stdscr.addstr(y, w//2, col2)
            y += 1
            
        self.stdscr.addstr(h-1, (w-39)//2, "Appuyez sur Q ou Entrée pour retourner", curses.color_pair(2))