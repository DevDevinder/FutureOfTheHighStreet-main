# pythonScripts/export_saver.py
import os
import pandas as pd
import datetime as _dt
from IPython.display import display, FileLink

def _sanitize(text: str) -> str:
    if text is None:
        return "none"
    return "".join(ch if ch.isalnum() or ch in "-._" else "_" for ch in str(text)).strip("_")

def save_dataframe_snapshot(
    df: pd.DataFrame,
    prefix: str,
    folder: str = "exports/map_views",
    add_timestamp: bool = True,
    show_link: bool = True,
    encoding: str = "utf-8-sig",
) -> str | None:
    if df is None or df.empty:
        print("No rows to save.")
        return None
    os.makedirs(folder, exist_ok=True)
    ts = _dt.datetime.utcnow().strftime("%Y%m%d_%H%M%S") if add_timestamp else ""
    fname = f"{_sanitize(prefix)}_{ts}.csv" if ts else f"{_sanitize(prefix)}.csv"
    path = os.path.join(folder, fname)
    df.to_csv(path, index=False, encoding=encoding)
    if show_link:
        display(FileLink(path))
        print(f"Saved CSV to: {path}")
    return path
