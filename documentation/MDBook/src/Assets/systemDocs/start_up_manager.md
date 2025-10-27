# start_up_manager.py

**Role:** Notebook bootstrap — city selection UI and config loading.

## Key Concepts
- Scans `data/` for city folders.
- Shows a `city_selector` (ipywidgets).
- Loads the selected city's `config.py` via `data_manager.load_city_config`.
- Returns `config` object to drive all other cells.

## Public API
- `get_available_cities() -> list[str]`
- `city_selector: Dropdown`
- `choose_city() -> str | None`
- `load_city_config() -> ModuleType | None`
- `build_ui() -> VBox`
- `initialize_notebook() -> ModuleType | None`  # displays UI + loads default config

## Dependencies
- `data_manager.load_city_config`
- `ipywidgets`, `IPython.display.display`

## Notes
- `DATA_FOLDER_PATH` defaults to `data/`. Keep city folder names simple (no spaces).
- The notebook usually attaches `.observe(...)` to `city_selector` to auto-reload config.
