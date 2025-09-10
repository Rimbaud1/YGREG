# -- coding: utf-8 --

import curses
import re
from .constants import PYTHON_KEYWORDS, JS_KEYWORDS, CSS_PROPERTIES, OPERATORS

def highlight_python(line):
    """Retourne une liste de (token, color_pair, attribute) pour une ligne Python."""
    tokens = re.split(f'({OPERATORS}|\\s+|\\b\\d+\\b|\'.*?\'|".*?"|#.*)', line)
    result = []
    for token in filter(None, tokens):
        attr = curses.A_NORMAL
        color_pair_num = 0
        if token.startswith("'") or token.startswith('"'): color_pair_num = 4
        elif token.startswith('#'): color_pair_num = 5
        elif token in PYTHON_KEYWORDS: color_pair_num = 6; attr = curses.A_BOLD
        elif token.isdigit(): color_pair_num = 8
        elif re.match(OPERATORS, token): color_pair_num = 7
        result.append((token, color_pair_num, attr))
    return result

def highlight_js(line):
    """Retourne une liste de (token, color_pair, attribute) pour une ligne JavaScript."""
    tokens = re.split(f'({OPERATORS}|\\s+|\\b\\d+\\b|\'.*?\'|".*?"|//.*|/\\*.*?\\*/)', line)
    result = []
    for token in filter(None, tokens):
        attr = curses.A_NORMAL
        color_pair_num = 0
        if token.startswith("'") or token.startswith('"'): color_pair_num = 4
        elif token.startswith('//') or token.startswith('/*'): color_pair_num = 5
        elif token in JS_KEYWORDS: color_pair_num = 15; attr = curses.A_BOLD
        elif token.isdigit(): color_pair_num = 8
        elif re.match(OPERATORS, token): color_pair_num = 7
        result.append((token, color_pair_num, attr))
    return result

def highlight_html(line):
    """Retourne une liste de (token, color_pair, attribute) pour une ligne HTML."""
    tokens = re.split(r'(<[^>]+>|&[a-zA-Z0-9]+;)', line)
    result = []
    for token in filter(None, tokens):
        color_pair_num = 0
        if token.startswith('<'):
            if token.startswith(('<!--', '<!DOCTYPE')): color_pair_num = 5
            else: color_pair_num = 13
        elif token.startswith('&'): color_pair_num = 8
        result.append((token, color_pair_num, curses.A_NORMAL))
    return result
    
def highlight_css(line):
    """Retourne une liste de (token, color_pair, attribute) pour une ligne CSS."""
    # Note: L'état est difficile à gérer ligne par ligne, c'est une simplification.
    tokens = re.split(r'([{}\[\]:;,\s+]|\d+\w*|".*?"|/\*.*?\*/)', line)
    result = []
    state = 'selector' # Simplification
    for token in filter(None, tokens):
        attr = curses.A_NORMAL
        color_pair_num = 0
        if token in CSS_PROPERTIES and state == 'property': color_pair_num = 16
        elif token.startswith('/*'): color_pair_num = 5
        elif token.isdigit() or token.startswith('#'): color_pair_num = 8
        elif token.startswith('"'): color_pair_num = 4
        elif state == 'selector' and token.strip() and token not in '{};:': color_pair_num = 6
        if token == '{': state = 'property'
        elif token == '}': state = 'selector'
        elif token == ':': state = 'value'
        elif token == ';': state = 'property'
        result.append((token, color_pair_num, attr))
    return result

def highlight_json(line):
    """Retourne une liste de (token, color_pair, attribute) pour une ligne JSON."""
    tokens = re.split(r'("[^"]*"\s*:|"[^"]*"|\btrue\b|\bfalse\b|\bnull\b|\d+(?:\.\d*)?|[{}\[\]:,])', line)
    result = []
    for token in filter(None, tokens):
        attr = curses.A_NORMAL
        color_pair_num = 0
        if token.strip().endswith(':'): color_pair_num = 16
        elif token.startswith('"'): color_pair_num = 4
        elif token in ('true', 'false', 'null'): color_pair_num = 15
        elif token.strip().isdigit() or '.' in token.strip(): color_pair_num = 8
        elif token in '{}[],:': color_pair_num = 7
        result.append((token, color_pair_num, attr))
    return result