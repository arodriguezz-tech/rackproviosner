import configparser
from .paths import SETTINGS

class SettingsService:
    def load(self):
        c=configparser.ConfigParser(); c.read(SETTINGS,encoding="utf-8"); return c
    def save(self,c):
        with SETTINGS.open("w",encoding="utf-8") as f: c.write(f)
    def get_bool(self,section,key,default=False): return self.load().getboolean(section,key,fallback=default)
    def get(self,section,key,default=""): return self.load().get(section,key,fallback=default)
