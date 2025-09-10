# -- coding: utf-8 --

import curses
import os
import re
import time
import math
import uuid
from datetime import datetime

from .utils import prompt_input
from .constants import LOREM_IPSUM, GROUPED_COMMANDS
from . import syntax # Import du module de coloration

class Editor:
    def __init__(self, stdscr, file_path, settings):
        self.stdscr = stdscr
        self.file_path = file_path
        self.settings = settings
        self.lines = [""]
        self.cursor_y, self.cursor_x = 0, 0
        self.top_line, self.left_col = 0, 0
        self.modified_counter = 0
        self.status_message, self.status_message_time = "", 0
        self.search_term = ""
        self.clipboard = []
        self.selecting = False
        self.selection_anchor_y, self.selection_anchor_x = -1, -1
        self.read_only = False
        self.color_preview_active = False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.lines = [line.rstrip('\n') for line in f.readlines()]
            if not self.lines: self.lines = [""]
        except (IOError, UnicodeDecodeError) as e:
            self.lines = ["", f" ERREUR: Impossible d'ouvrir le fichier : {e}", " Le fichier est en lecture seule.", ""]
            self.read_only = True
        except FileNotFoundError:
            self._set_status_message(f"Nouveau fichier : {os.path.basename(file_path)}")
        
        self._modified_flag = False

    @property
    def modified(self): return self._modified_flag

    @modified.setter
    def modified(self, value):
        if self.read_only: self._modified_flag = False; return
        self._modified_flag = value
        if value:
            self.modified_counter += 1
            threshold = self.settings.get("autosave_threshold")
            if threshold > 0 and self.modified_counter >= threshold:
                if self._save_file(autosave=True):
                    self._set_status_message("Sauvegarde automatique")
                    self.modified_counter = 0
        else: self.modified_counter = 0

    def _set_status_message(self, msg):
        self.status_message, self.status_message_time = msg, time.time()

    def _get_screen_size(self): return self.stdscr.getmaxyx()

    def _draw_ui(self):
        height, width = self._get_screen_size()
        self.stdscr.attron(curses.color_pair(3)); self.stdscr.box(); self.stdscr.attroff(curses.color_pair(3))
        
        time_str = datetime.now().strftime('%H:%M:%S')
        title_extra = " [LECTURE SEULE]" if self.read_only else ""
        title = f" YGREG - {os.path.basename(self.file_path)}{title_extra} "
        
        full_title = f"{time_str} {title}"
        if len(full_title) < width: self.stdscr.addstr(0, (width - len(title)) // 2 - len(time_str), full_title, curses.A_BOLD)
        else: self.stdscr.addstr(0, 2, title[:width-4], curses.A_BOLD)

        status_bar_pair = 17 if self.color_preview_active else 2
        
        if self.status_message and time.time() - self.status_message_time < 2.5:
            self.stdscr.attron(curses.color_pair(1))
            self.stdscr.addstr(height - 1, 1, self.status_message.ljust(width - 2))
            self.stdscr.attroff(curses.color_pair(1))
        else:
            self.status_message = ""
            modified_char = '[+]' if self.modified else ''
            status_text = f" {len(self.lines)} Lignes {modified_char}"
            pos_text = f"L:{self.cursor_y + 1}, C:{self.cursor_x + 1} "
            
            self.stdscr.attron(curses.color_pair(status_bar_pair))
            status_bar_content = status_text.ljust(width - len(pos_text) - 2) + pos_text
            self.stdscr.addstr(height - 1, 1, status_bar_content[:width - 2])
            self.stdscr.attroff(curses.color_pair(status_bar_pair))
        
        self.stdscr.addstr(0, 3, "Tab > Commandes", curses.A_REVERSE)

    def _get_word_under_cursor(self):
        if self.cursor_y >= len(self.lines): return ""
        line = self.lines[self.cursor_y]
        words = re.finditer(r'(#[0-9a-fA-F]{3,6}\b|\w+)', line)
        for match in words:
            if match.start() <= self.cursor_x <= match.end():
                return match.group(0)
        return ""

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3: hex_color = "".join(c * 2 for c in hex_color)
        if len(hex_color) != 6: return None
        try: return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except ValueError: return None
    
    def _color_distance(self, c1, c2):
        r1, g1, b1 = c1; r2, g2, b2 = c2
        return math.sqrt((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2)

    def _rgb_to_curses_color(self, r, g, b):
        if curses.COLORS < 256: return -1
        colors = [(0,0,0)] * 16
        levels = [0, 95, 135, 175, 215, 255]
        for i in range(216):
            r_ = levels[(i // 36) % 6]; g_ = levels[(i // 6) % 6]; b_ = levels[i % 6]
            colors.append((r_, g_, b_))
        for i in range(24): l = 8 + i * 10; colors.append((l, l, l))
        
        closest_color_idx = -1; min_dist = float('inf')
        for idx, c in enumerate(colors):
            dist = self._color_distance((r,g,b), c)
            if dist < min_dist: min_dist = dist; closest_color_idx = idx
        return closest_color_idx
    
    def _update_color_preview(self):
        word = self._get_word_under_cursor()
        rgb = self._hex_to_rgb(word) if word.startswith('#') else None
        if rgb:
            curses_color = self._rgb_to_curses_color(*rgb)
            if curses_color != -1:
                curses.init_pair(17, curses.COLOR_WHITE, curses_color)
                self.color_preview_active = True
                return
        self.color_preview_active = False
        
    def _draw_lines(self):
        height, width = self._get_screen_size()
        editor_height = height - 2
        self.line_num_width_ref = len(str(len(self.lines))) + 2
        for y_idx in range(editor_height):
            file_line_idx = self.top_line + y_idx
            if file_line_idx >= len(self.lines): break
            line_num_str = str(file_line_idx + 1).rjust(self.line_num_width_ref - 2) + " "
            self.stdscr.addstr(y_idx + 1, 1, line_num_str, curses.color_pair(3) | curses.A_DIM)
            self._draw_highlighted_line(y_idx + 1, self.line_num_width_ref, file_line_idx, self.lines[file_line_idx])
        self._draw_scrollbar()

    def _render_token(self, y, line_idx, token_text, color_attr, token_start_col_abs):
        height, width = self._get_screen_size()
        content_width = width - self.line_num_width_ref - 2
        overlap_start = max(token_start_col_abs, self.left_col)
        overlap_end = min(token_start_col_abs + len(token_text), self.left_col + content_width)
        if overlap_start >= overlap_end: return
        text_to_draw = token_text[overlap_start - token_start_col_abs : overlap_end - token_start_col_abs]
        screen_x = self.line_num_width_ref + (overlap_start - self.left_col)
        for i, char in enumerate(text_to_draw):
            char_abs_x = overlap_start + i
            selection_attr = curses.A_REVERSE if self._is_selected(line_idx, char_abs_x) else curses.A_NORMAL
            try: self.stdscr.addstr(y, screen_x + i, char, color_attr | selection_attr)
            except curses.error: pass

    def _is_selected(self, y, x):
        if not self.selecting: return False
        (start_y, start_x), (end_y, end_x) = self._get_selection_bounds()
        return start_y <= y <= end_y and not (y == start_y and x < start_x) and not (y == end_y and x >= end_x)
    
    def _draw_scrollbar(self):
        height, width = self._get_screen_size()
        editor_height = height - 2
        if len(self.lines) > editor_height:
            thumb_size = max(1, int(editor_height * editor_height / len(self.lines)))
            thumb_pos = int(self.top_line / (len(self.lines) - editor_height) * (editor_height - thumb_size)) if len(self.lines) > editor_height else 0
            for i in range(editor_height):
                char = "█" if thumb_pos <= i < thumb_pos + thumb_size else "░"
                attr = curses.color_pair(3) | (curses.A_NORMAL if thumb_pos <= i < thumb_pos + thumb_size else curses.A_DIM)
                self.stdscr.addstr(i + 1, width - 2, char, attr)
                
    def _draw_highlighted_line(self, y, x_offset, line_idx, line):
        ext = os.path.splitext(self.file_path)[1].lower() if not self.read_only else ""
        highlighter = None
        if self.settings.get("show_syntax_highlighting"):
            if ext == '.py': highlighter = syntax.highlight_python
            elif ext == '.js': highlighter = syntax.highlight_js
            elif ext == '.html': highlighter = syntax.highlight_html
            elif ext == '.css': highlighter = syntax.highlight_css
            elif ext == '.json': highlighter = syntax.highlight_json
        
        if highlighter:
            tokens = highlighter(line)
            current_col = 0
            for token_text, color_pair_num, attr in tokens:
                color = curses.color_pair(color_pair_num) | attr
                self._render_token(y, line_idx, token_text, color, current_col)
                current_col += len(token_text)
        else:
            self._render_token(y, line_idx, line, curses.color_pair(0), 0)

    def _scroll(self):
        height, width = self._get_screen_size()
        editor_height = height - 2
        line_number_width = len(str(len(self.lines))) + 2
        content_width = width - line_number_width - 2
        if self.cursor_y < self.top_line: self.top_line = self.cursor_y
        if self.cursor_y >= self.top_line + editor_height: self.top_line = self.cursor_y - editor_height + 1
        if self.cursor_x < self.left_col: self.left_col = self.cursor_x
        if self.cursor_x >= self.left_col + content_width: self.left_col = self.cursor_x - content_width + 1

    def run(self):
        while True:
            height, width = self._get_screen_size()
            if height < 5 or width < 20:
                self.stdscr.erase()
                self.stdscr.addstr(0, 0, "Terminal trop petit. Redimensionnez.")
                self.stdscr.refresh()
                try:
                    self.stdscr.get_wch()
                except curses.error:
                    pass
                continue

            self._update_color_preview()
            try:
                self.stdscr.erase()
                self._scroll()
                self._draw_ui(); self._draw_lines()
                line_number_width = len(str(len(self.lines))) + 2
                self.stdscr.move(self.cursor_y - self.top_line + 1, self.cursor_x - self.left_col + line_number_width)
                curses.curs_set(1)
                self.stdscr.refresh()
            except curses.error: pass

            action = self._handle_input()
            if action in ["quit", "settings", "help"]:
                if action == "quit" and self.modified:
                    if prompt_input(self.stdscr, "Quitter sans sauvegarder? (o/n) ").lower() != 'o': continue
                return action

    def _get_selection_bounds(self):
        return min((self.selection_anchor_y, self.selection_anchor_x), (self.cursor_y, self.cursor_x)), \
               max((self.selection_anchor_y, self.selection_anchor_x), (self.cursor_y, self.cursor_x))

    def _handle_auto_expansion(self):
        line = self.lines[self.cursor_y]
        word_match = re.search(r'(\S+)$', line[:self.cursor_x])
        if not word_match: return False
        
        word = word_match.group(1)
        replacement, cursor_offset = None, None

        if word == "date": replacement = datetime.now().strftime('%Y-%m-%d')
        elif word == "heure": replacement = datetime.now().strftime('%H:%M:%S')
        elif word == "now": replacement = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        elif word == "uuid": replacement = str(uuid.uuid4())
        elif word == "link": replacement, cursor_offset = "[](url)", 1
        elif word == "img": replacement, cursor_offset = "![]()", 2
        elif word.startswith("lorem"):
            try:
                num_words = int(word[5:])
                replacement = " ".join(LOREM_IPSUM.split()[:num_words])
            except (ValueError, IndexError): pass
        
        if replacement:
            start_pos = word_match.start(1)
            self.lines[self.cursor_y] = line[:start_pos] + replacement + line[self.cursor_x:]
            self.cursor_x = start_pos + cursor_offset if cursor_offset is not None else start_pos + len(replacement)
            self.modified = True
            return True
        return False
    
    def _calculate_line(self):
        line = self.lines[self.cursor_y].split('=')[0].strip()
        if not self.lines[self.cursor_y].strip().endswith('=') or not line: return False
        try:
            safe_env = {k: v for k, v in math.__dict__.items() if not k.startswith('_')}
            result = eval(line, {"__builtins__": {}}, safe_env)
            result_str = str(int(result) if isinstance(result, float) and result.is_integer() else f"{result:.4f}")
            self.lines[self.cursor_y] += f" {result_str}"
            self.cursor_x = len(self.lines[self.cursor_y])
            self.modified = True
        except Exception as e: self._set_status_message(f"Erreur de calcul: {e}")
        return True

    def _duplicate_line_or_selection(self):
        if self.selecting:
            (start_y, _), (end_y, end_x) = self._get_selection_bounds()
            to_duplicate = self._get_selection_text()
            last_line_part = self.lines[end_y][end_x:]
            self.lines[end_y] = self.lines[end_y][:end_x] + "".join(to_duplicate) + last_line_part
        else:
            self.lines.insert(self.cursor_y + 1, self.lines[self.cursor_y])
        self.modified = True; self._set_status_message("Dupliqué")

    def _join_lines(self):
        if self.cursor_y < len(self.lines) - 1:
            next_line = self.lines.pop(self.cursor_y + 1).lstrip()
            self.lines[self.cursor_y] = self.lines[self.cursor_y].rstrip() + " " + next_line
            self.modified = True

    def _sort_lines(self):
        choice = prompt_input(self.stdscr, "Ordonner: ligne (a)ctuelle, (t)out le document, selection de (l)ignes ? ")
        if not choice: return

        if choice == 'a':
            words = self.lines[self.cursor_y].split()
            words.sort(key=str.lower)
            self.lines[self.cursor_y] = " ".join(words)
            self.modified = True
            self._set_status_message("Ligne actuelle ordonnée")
        elif choice == 't':
            self.lines.sort(key=str.lower)
            self.modified = True
            self._set_status_message("Document ordonné")
        elif choice == 'l':
            start_str = prompt_input(self.stdscr, "Ligne de départ: ")
            end_str = prompt_input(self.stdscr, "Ligne de fin: ")
            if start_str.isdigit() and end_str.isdigit():
                start = int(start_str) - 1
                end = int(end_str)
                if 0 <= start < end <= len(self.lines):
                    lines_to_sort = self.lines[start:end]
                    lines_to_sort.sort(key=str.lower)
                    self.lines[start:end] = lines_to_sort
                    self.modified = True
                    self._set_status_message(f"Lignes {start+1} à {end} ordonnées")
                else:
                    self._set_status_message("Plage de lignes invalide")
            else:
                self._set_status_message("Entrée invalide")

    def _insert_table(self):
        cols_str = prompt_input(self.stdscr, "Nombre de colonnes: ")
        rows_str = prompt_input(self.stdscr, "Nombre de lignes: ")
        if not (cols_str.isdigit() and rows_str.isdigit()):
            self._set_status_message("Entrée invalide"); return
        cols, rows = int(cols_str), int(rows_str); col_width = 15
        
        sep = '+' + ('-' * col_width + '+') * cols
        content_row = '|' + (' ' * col_width + '|') * cols
        table = [sep]
        for i in range(rows): table.extend([content_row, sep])
        
        self.lines[self.cursor_y+1:self.cursor_y+1] = table; self.modified = True

    def _handle_input(self):
        try: key = self.stdscr.get_wch()
        except (curses.error, KeyboardInterrupt): return "continue"
        
        is_shift_move = isinstance(key, int) and key in [curses.KEY_SLEFT, curses.KEY_SRIGHT, curses.KEY_SR, curses.KEY_SF]
        if is_shift_move and not self.selecting:
            self.selecting = True
            self.selection_anchor_y, self.selection_anchor_x = self.cursor_y, self.cursor_x

        if self.selecting and isinstance(key, str) and key not in ['\t']: self._delete_selection()

        # MODIFIÉ: Ajout de 'or key == "\n"' pour gérer le cas où get_wch() retourne une chaîne
        if key in [curses.KEY_ENTER, 10, 13] or key == '\n':
            if self.read_only: return "continue"
            if self.selecting:
                (start_y, start_x), (end_y, end_x) = self._get_selection_bounds()
                if start_y == end_y:
                    line = self.lines[start_y]
                    self.lines[start_y] = line[:start_x]
                    self.lines.insert(start_y + 1, line[start_x:])
                    self.cursor_y += 1; self.cursor_x = 0
                    self.modified = True; self.selecting = False
                    return "continue"
            line = self.lines[self.cursor_y]
            self.lines.insert(self.cursor_y + 1, line[self.cursor_x:])
            self.lines[self.cursor_y] = line[:self.cursor_x]
            self.cursor_y += 1; self.cursor_x = 0; self.modified = True

        elif key == '\t':
            if self.settings.get("smart_tab"):
                if self._handle_auto_expansion(): pass
                elif self._calculate_line(): pass
                elif self.selecting: self._indent_selection()
                else: return self._handle_command_mode()
            else:
                if self.selecting: self._indent_selection()
                else: return self._handle_command_mode()

        elif key == curses.KEY_BTAB:
            if self.selecting: self._unindent_selection()

        elif isinstance(key, int):
            if key == curses.KEY_UP or key == curses.KEY_SR: self.cursor_y = max(0, self.cursor_y - 1)
            elif key == curses.KEY_DOWN or key == curses.KEY_SF: self.cursor_y = min(len(self.lines) - 1, self.cursor_y + 1)
            elif key == curses.KEY_LEFT or key == curses.KEY_SLEFT: self.cursor_x = max(0, self.cursor_x - 1)
            elif key == curses.KEY_RIGHT or key == curses.KEY_SRIGHT: self.cursor_x = min(len(self.lines[self.cursor_y]), self.cursor_x + 1)
            elif key in [curses.KEY_BACKSPACE, 127, 8]:
                if self.read_only: return "continue"
                if self.selecting: self._delete_selection(); self.selecting = False
                elif self.cursor_x > 0:
                    self.lines[self.cursor_y] = self.lines[self.cursor_y][:self.cursor_x-1] + self.lines[self.cursor_y][self.cursor_x:]
                    self.cursor_x -= 1; self.modified = True
                elif self.cursor_y > 0:
                    prev_len = len(self.lines[self.cursor_y - 1])
                    self.lines[self.cursor_y - 1] += self.lines.pop(self.cursor_y)
                    self.cursor_y -= 1; self.cursor_x = prev_len; self.modified = True
        elif isinstance(key, str):
            if self.read_only: return "continue"
            self.lines[self.cursor_y] = self.lines[self.cursor_y][:self.cursor_x] + key + self.lines[self.cursor_y][self.cursor_x:]
            self.cursor_x += len(key); self.modified = True

        if not is_shift_move: self.selecting = False
        if self.cursor_y >= len(self.lines): self.cursor_y = len(self.lines) - 1
        self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))
        return "continue"
    
    def _handle_command_mode(self):
        page_index = 0
        all_command_keys = {cmd[0] for _, cmds in GROUPED_COMMANDS for cmd in cmds}

        while True:
            group_name, commands = GROUPED_COMMANDS[page_index]

            prompt_parts = [f"({key}){desc.split()[0]}" for key, desc in commands]
            prompt = f"CMD {group_name}: {' '.join(prompt_parts)} | Tab: plus, Esc: annuler"

            h, w = self._get_screen_size()
            self.stdscr.attron(curses.color_pair(1))
            self.stdscr.addstr(h - 1, 1, prompt.ljust(w - 2)[:w-2])
            self.stdscr.attroff(curses.color_pair(1))
            self.stdscr.refresh()

            try:
                key = self.stdscr.get_wch()
            except (curses.error, KeyboardInterrupt):
                return "continue"

            if key == '\t':
                page_index = (page_index + 1) % len(GROUPED_COMMANDS)
                continue

            if isinstance(key, str) and key in all_command_keys:
                cmd = key
                if cmd == 's': self._save_file()
                elif cmd == 'q': return "quit"
                elif cmd == 'h': return "help"
                elif cmd == 'p': return "settings"
                elif cmd == 'f': self._search()
                elif cmd == 'r': self._search_and_replace()
                elif cmd == 'g': self._goto_line()
                elif cmd == 'd': self._duplicate_line_or_selection()
                elif cmd == 'j': self._join_lines()
                elif cmd == 'o': self._sort_lines()
                elif cmd == 't': self._insert_table()
                elif cmd == 'x': self._copy_selection(); self._delete_selection()
                elif cmd == 'c': self._copy_selection()
                elif cmd == 'v': self._paste()

            # Quitte le mode commande sur Esc ou toute autre touche
            break

        # Redessine l'interface normale pour effacer le prompt
        return "continue"
    
    def _get_selection_text(self):
        if not self.selecting: return []
        (start_y, start_x), (end_y, end_x) = self._get_selection_bounds()
        if start_y == end_y: return [self.lines[start_y][start_x:end_x]]
        lines = [self.lines[start_y][start_x:]]
        lines.extend(self.lines[start_y + 1:end_y])
        lines.append(self.lines[end_y][:end_x])
        return lines
        
    def _delete_selection(self):
        if not self.selecting: return
        (start_y, start_x), (end_y, end_x) = self._get_selection_bounds()
        first_line_part = self.lines[start_y][:start_x]
        last_line_part = self.lines[end_y][end_x:]
        if start_y == end_y:
            self.lines[start_y] = first_line_part + last_line_part
        else:
            self.lines[start_y] = first_line_part + last_line_part
            del self.lines[start_y + 1 : end_y + 1]
        self.cursor_y, self.cursor_x = start_y, start_x
        self.selecting = False; self.modified = True
        
    def _copy_selection(self):
        self.clipboard = self._get_selection_text()
        
    def _paste(self):
        if self.read_only or not self.clipboard: return
        if self.selecting: self._delete_selection()
        if len(self.clipboard) == 1:
            line = self.lines[self.cursor_y]
            self.lines[self.cursor_y] = line[:self.cursor_x] + self.clipboard[0] + line[self.cursor_x:]
            self.cursor_x += len(self.clipboard[0])
        else:
            line_end = self.lines[self.cursor_y][self.cursor_x:]
            self.lines[self.cursor_y] = self.lines[self.cursor_y][:self.cursor_x] + self.clipboard[0]
            for i, clip_line in enumerate(self.clipboard[1:]):
                self.lines.insert(self.cursor_y + i + 1, clip_line)
            self.lines[self.cursor_y + len(self.clipboard) - 1] += line_end
            self.cursor_y += len(self.clipboard) - 1
            self.cursor_x = len(self.clipboard[-1])
        self.modified = True
        
    def _indent_selection(self, unindent=False):
        if self.read_only or not self.selecting: return
        (start_y, _), (end_y, _) = self._get_selection_bounds()
        tab_str = " " * self.settings.get("tab_size")
        for i in range(start_y, end_y + 1):
            if unindent:
                if self.lines[i].startswith(tab_str): self.lines[i] = self.lines[i][len(tab_str):]
            else: self.lines[i] = tab_str + self.lines[i]
        self.modified = True
        
    def _unindent_selection(self): self._indent_selection(unindent=True)
    
    def _save_file(self, autosave=False):
        if self.read_only:
            if not autosave: self._set_status_message("Fichier non modifiable")
            return False
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f: f.write('\n'.join(self.lines))
            self.modified = False
            if not autosave: self._set_status_message("Fichier sauvegardé !")
            return True
        except Exception as e:
            if not autosave: self._set_status_message(f"Erreur de sauvegarde: {e}")
            return False
            
    def _goto_line(self):
        line_num_str = prompt_input(self.stdscr, "Aller à la ligne: ")
        if line_num_str.isdigit():
            line_num = int(line_num_str)
            if 1 <= line_num <= len(self.lines): self.cursor_y, self.cursor_x = line_num - 1, 0
            
    def _search(self):
        search_term = prompt_input(self.stdscr, "Rechercher: ")
        if search_term: self.search_term = search_term; self._find_next()
        
    def _find_next(self):
        if not self.search_term: return
        start_y, start_x = self.cursor_y, self.cursor_x + 1
        for y in range(start_y, len(self.lines)):
            x = self.lines[y].find(self.search_term, start_x if y == start_y else 0)
            if x != -1: self.cursor_y, self.cursor_x = y, x; return
        for y in range(start_y):
            x = self.lines[y].find(self.search_term)
            if x != -1: self.cursor_y, self.cursor_x = y, x; return
        self._set_status_message(f"'{self.search_term}' non trouvé")
        
    def _search_and_replace(self):
        if self.read_only: self._set_status_message("Lecture seule"); return
        find_str = prompt_input(self.stdscr, "Remplacer: ")
        if not find_str: return
        replace_str = prompt_input(self.stdscr, f"Remplacer '{find_str}' par: ")
        replace_all = prompt_input(self.stdscr, "Remplacer tout? (o/n): ").lower() == 'o'
        count = 0
        if replace_all:
            for i, line in enumerate(self.lines):
                new_line, num = re.subn(find_str, replace_str, line)
                if num > 0: self.lines[i], count = new_line, count + num
        else:
            line = self.lines[self.cursor_y]
            if find_str in line:
                self.lines[self.cursor_y] = line.replace(find_str, replace_str, 1)
                count = 1
        if count > 0: self.modified = True; self._set_status_message(f"{count} remplacement(s)")
        else: self._set_status_message("Non trouvé")