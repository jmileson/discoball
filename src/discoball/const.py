from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent.resolve()
OLIST_DIR = ROOT_DIR / "olist"
DB = ROOT_DIR / ".data" / "dev.duckdb"
