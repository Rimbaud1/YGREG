# -- coding: utf-8 --

import json
from .constants import CONFIG_FILE

class Settings:
    def __init__(self):
        self.defaults = {
            "theme": "dark",
            "autosave_threshold": 25,
            "show_syntax_highlighting": True,
            "tab_size": 4
        }
        self.settings = self.defaults.copy()
        self.load()

    def load(self):
        try:
            with open(CONFIG_FILE, 'r') as f:
                self.settings.update(json.load(f))
        except (FileNotFoundError, json.JSONDecodeError):
            self.save()

    def save(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def get(self, key):
        return self.settings.get(key, self.defaults.get(key))

    def set(self, key, value):
        self.settings[key] = value
        self.save()