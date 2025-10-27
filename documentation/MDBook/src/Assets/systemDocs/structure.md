## 📁 Notebook Structure
```notebook.ipynb
│
├─ data/
│ └─ <CityName>/
│ ├─ CSVs/
│ ├─ pycache/
│ ├─ routes/
│ └─ config.py
├─ pythonScripts/
├─ exports/
└─ documentation/
```

### data/
Holds the city dataset the notebook will work on. Each city has its own folder (`data/<CityName>/`) to keep paths isolated.

Inside each city folder:
- `CSVs/` – raw/cleaned CSV files (postcodes, boundaries if CSV, traffic, businesses, etc.).
- `routes/` – precomputed or exported route CSVs (e.g., `shopping_district_routes.csv`, `city_centre_routes.csv`).
- `config.py` – the **single source of truth** for file paths (postcodes, boundaries, routes, CCTV, etc.).
- `__pycache__/` – Python bytecode (safe to ignore in version control).

### pythonScripts/
All reusable modules the notebook calls. Typical files include:
- `cell_manager.py` (orchestrates cells)
- `start_up_manager.py` (city selection, config loading)
- `data_manager.py` (load/clean data, boundaries, affluence, routes I/O)
- `map_renderer.py` (folium maps, overlays, heatmaps, legends)
- `routing_manager.py` (walk/cycle/car routes; helpers)
- `postcode_map_manager.py` (postcode map/search utilities)
- `marker_manager.py` (interactive markers)
- `cctv_manager.py` (CCTV & vehicle classification loading/plots/maps)
- `ui_manager.py` (widgets + small export wrappers)
- `export_saver.py` (save visible data to CSV)

### exports/
Where **manual export requests** from cells are saved (CSV).  
Defaults can be changed per call (see `export_saver.save_dataframe_snapshot`), but the conventional folder is `exports/map_views/`.

> Exports contain **only the user-visible columns** (e.g., what popups/legends show), not entire source datasets.

### documentation/
Your mdBook source (`src/*.md`) and any supporting assets (images/css).  
This guide and the function-flow diagrams live here.
