# -- coding: utf-8 --

import curses
import os
import shutil
from datetime import datetime
from math import log, floor

from .constants import FILE_ICON_MAP
from .utils import prompt_input

class FileSelector:
    def __init__(self, stdscr, settings):
        self.stdscr = stdscr
        self.settings = settings
        self.current_path = os.getcwd()
        self.selected_row, self.top_row = 0, 0

    def _get_item_display(self, item_name, full_path):
        icon, color = ("📁", 7) if os.path.isdir(full_path) else ("📄", 0)
        if not os.path.isdir(full_path):
            ext = os.path.splitext(item_name)[1].lower()
            if ext in FILE_ICON_MAP: icon, color = FILE_ICON_MAP[ext]
        display_name = f"{icon} {item_name}"
        
        size_str, date_str = "", ""
        try:
            stat = os.stat(full_path)
            date_str = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
            if not os.path.isdir(full_path):
                size = stat.st_size
                if size == 0: size_str = "0B"
                else:
                    i = int(floor(log(size, 1024))); p = pow(1024, i)
                    size_str = f"{round(size / p, 2)} {('B', 'KB', 'MB', 'GB')[i]}"
        except OSError: pass
        return display_name, size_str, date_str, color

    def _draw(self, items):
        h, w = self.stdscr.getmaxyx(); selector_h = h - 2
        self.stdscr.attron(curses.color_pair(3)); self.stdscr.box(); self.stdscr.attroff(curses.color_pair(3))
        self.stdscr.addstr(0, (w - 31) // 2, " YGREG - Explorateur de Fichiers ", curses.A_BOLD)
        path_display = self.current_path if len(self.current_path) <= w-4 else f"...{self.current_path[-(w-7):]}"
        self.stdscr.addstr(1, 2, f"Dossier: {path_display}", curses.A_DIM)

        if self.selected_row < self.top_row: self.top_row = self.selected_row
        if self.selected_row >= self.top_row + selector_h - 1: self.top_row = self.selected_row - selector_h + 2
        
        for i in range(selector_h - 1):
            list_idx = self.top_row + i
            if list_idx >= len(items): break
            item_name = items[list_idx]
            display_name, size, date, color = self._get_item_display(item_name, os.path.join(self.current_path, item_name))
            line = f"{display_name:<{w-30}} {date:<17} {size:>8}"[:w-4]
            style = curses.color_pair(2) | curses.A_BOLD if list_idx == self.selected_row else curses.color_pair(color)
            self.stdscr.addstr(i + 2, 2, line.ljust(w - 4), style)
        
        self.stdscr.addstr(h - 1, (w - 53) // 2, "Entrée: Ouvrir | Q: Quitter | Suppr: Effacer | Tab > Cmds", curses.color_pair(2))

    def run(self):
        curses.curs_set(0)
        while True:
            try:
                items = sorted(os.listdir(self.current_path), key=lambda x: (not os.path.isdir(os.path.join(self.current_path, x)), x.lower()))
                if os.path.abspath(self.current_path) != '/': items.insert(0, "..")
                self.stdscr.erase(); self._draw(items); self.stdscr.refresh()
            except curses.error: pass

            key = self.stdscr.getch()
            if key == curses.KEY_UP: self.selected_row = max(0, self.selected_row - 1)
            elif key == curses.KEY_DOWN: self.selected_row = min(len(items) - 1, self.selected_row + 1)
            elif key == ord('q'): return None
            elif key in [curses.KEY_ENTER, 10, 13]:
                if not items: continue
                selected_path = os.path.abspath(os.path.join(self.current_path, items[self.selected_row]))
                if os.path.isdir(selected_path): 
                    self.current_path, self.selected_row = selected_path, 0
                    os.chdir(self.current_path)
                else: return selected_path
            elif key == curses.KEY_DC:
                path_to_delete = os.path.join(self.current_path, items[self.selected_row])
                if prompt_input(self.stdscr, f"Effacer '{items[self.selected_row]}'? (o/n): ").lower() == 'o':
                    try:
                        if os.path.isdir(path_to_delete): shutil.rmtree(path_to_delete)
                        else: os.remove(path_to_delete)
                        self.selected_row = max(0, self.selected_row - 1)
                    except OSError as e: prompt_input(self.stdscr, f"Erreur: {e}...")
            elif key == ord('\t'):
                name_prompt = {"n": "Nom du nouveau fichier: ", "d": "Nom du nouveau dossier: "}
                cmd = prompt_input(self.stdscr, "Commande: (n)ouveau fichier, (d)ossier: ")
                if cmd in name_prompt:
                    name = prompt_input(self.stdscr, name_prompt[cmd])
                    if name:
                        if cmd == 'n': open(os.path.join(self.current_path, name), 'a').close()
                        else: os.makedirs(os.path.join(self.current_path, name), exist_ok=True)