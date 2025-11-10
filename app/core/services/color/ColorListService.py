import csv
import pickle
from pathlib import Path
from typing import List, Dict, Any, Tuple


def _app_root() -> Path:
    # This file lives in app/core/services → go up two levels to app/
    return Path(__file__).resolve().parents[3]


def _pkl_path() -> Path:
    return _app_root() / "colors.pkl"


def _csv_path() -> Path:
    return _app_root() / "colors.csv"


def get_predefined_colors() -> List[Dict[str, Any]]:
    """
    Load predefined colors from colors.pkl (preferred). If not present,
    load from colors.csv. No on-the-fly writes are performed here.
    Returns a list of dicts with keys: name, rgb(tuple), uses.
    """
    pkl = _pkl_path()
    if pkl.exists():
        with pkl.open("rb") as f:
            data = pickle.load(f)
        return data if isinstance(data, list) else []

    csv_path = _csv_path()
    if csv_path.exists():
        rows: List[Dict[str, Any]] = []
        with csv_path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    r = int(row.get("r", "0"))
                    g = int(row.get("g", "0"))
                    b = int(row.get("b", "0"))
                    name = row.get("name", "")
                    uses = row.get("uses", "")
                    rows.append({"name": name, "rgb": (r, g, b), "uses": uses})
                except Exception:
                    continue
        return rows

    # Nothing available
    return []


