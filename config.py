from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DB_PATH = DATA / "sg_rate.db"
PUBLISHED_PATH = DATA / "published_rates.json"
MASTER_PATH = DATA / "brand_master.csv"
SHEET_NAME = "①SG点数表"
S_EVENT_SHEET_NAME = "③S活动"
