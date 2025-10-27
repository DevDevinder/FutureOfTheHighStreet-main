# export_saver.py

**Role:** Save trimmed, user-visible DataFrames to CSV and show a link in the notebook.

## Public API
- `save_dataframe_snapshot(df, prefix, folder="exports/map_views", add_timestamp=True, show_link=True, encoding="utf-8-sig") -> str | None`

## Behavior
- Sanitizes filename components.
- Optional UTC timestamp `YYYYMMDD_HHMMSS`.
- Displays a clickable link via `IPython.display.FileLink`.

## Notes
- Returns full file path or `None` (if df empty).
