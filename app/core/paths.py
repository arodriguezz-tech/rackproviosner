from pathlib import Path
BASE = Path(__file__).resolve().parents[2]
DATA = BASE / "data"
ARCHIVE = BASE / "archive"
SETTINGS = BASE / "settings.ini"
DATA.mkdir(exist_ok=True)
ARCHIVE.mkdir(exist_ok=True)
