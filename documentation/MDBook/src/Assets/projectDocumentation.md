# Notebook Guide

This guide explains the structure, purpose, and usage of the interactive city data notebook.  
It is intended for developers and maintainers working with the VSCode + GitHub environment.

---

## 1. Overview

The notebook (`.ipynb`) provides an interactive interface for exploring city datasets (postcodes, transport, CCTV, businesses).  
It uses **ipywidgets** for controls and **folium/ipyleaflet** for map visualisation.

All heavy logic is kept in **modular Python scripts** (`pythonScripts/`), while the notebook itself only orchestrates these scripts.

---

## 2. Architecture

notebook.ipynb
│
├─ cell_manager.py # Orchestrates notebook cells (thin wrappers only)
├─ start_up_manager.py # Notebook setup, city selector, config loading
├─ data_manager.py # Data loading/cleaning (CSV, JSON, postcodes, routes)
├─ map_renderer.py # Map rendering (base maps, heatmaps, routes, legends)
├─ routing_manager.py # Walking, cycling, driving routes (pyroutelib3)
├─ postcode_map_manager.py # Postcode search and map display
├─ marker_manager.py # Interactive marker placement/removal
├─ ui_manager.py # Widgets, dropdowns, buttons, export logic
├─ export_saver.py # Save map views to CSV
├─ cctv_manager.py # CCTV datasets, charts, and camera map views
└─ business_manager.py # Business mapping (bus stops + businesses)


**Key principle**:  
- `cell_manager.py` only calls into managers.  
- Processing logic belongs in the relevant manager file.  
- UI widgets live in `ui_manager.py`.  
- Exports go through `export_saver.py`.

---

## 3. Running the Notebook

1. Open the `.ipynb` file in **VSCode** (with Jupyter extension).  
2. Run **Cell 1** to set up the environment and load city config.  
3. Other cells can be executed independently afterwards.  
4. Data outputs and CSV exports will be saved to the `exports/` folder.  

---

## 4. Cell-by-Cell Reference

### Cell 1 — Setup
Initialises the notebook environment:
- Loads available cities (`start_up_manager.get_available_cities`).
- Displays a dropdown to select city.
- Loads city config (`data_manager.load_city_config`).
- Provides reactive city switching.

---

### Cell 2 — Base Map
Displays a base map with all city boundaries:
- Calls `map_renderer.combine_map_layers`  
- Layers boundaries via `map_renderer.add_boundaries`.


---

### Cell 3 — Postcodes within Boundaries
Interactive boundary selector:
- Filters postcodes inside the chosen boundary (`data_manager.load_filtered_postcodes`).  
- Displays postcode markers on map.  
- Exports filtered postcodes to CSV.  

---

### Cell 4 — Heatmap of Affluence/Population/Households
- Loads postcode dataset (`data_manager.load_affluence_postcodes`).  
- User chooses heatmap type (Affluence, Population, Households).  
- Overlays boundaries optionally.  
- Exports visible data to CSV.  

---

### Cell 5 — Initialise BusNet4
- Prepares BusNet4 routing graph within city boundaries.  
- Must be run before bus route features.  

---

### Cell 6 — Closest Postcodes to Commercial Zones
- Compares distances between **City Centre** vs **Shopping Districts**.  
- Displays only postcodes where the selected zone is closer.  
- Shows walking, cycling, and driving routes.  
- Saves computed routes to CSV (`data_manager.save_route_data`).  

---

### Cell 7 — Red/Green Zone Visualisation
- Adds markers to show which zone is closer:
  - **Green**: closer to selected area type.
  - **Red**: closer to the alternative.  

---

### Cell 8 — Backup BusNet4 Initialisation
- Re-runs `initialise_busnetfour()` if Cell 5 was skipped.  

---

### Cell 9 — Bus Route to a Boundary
- Draws a bus route from a fixed start point into a boundary polygon.  

---

### Cell 10 — Bus Route Between Two Postcodes
- User selects start and end postcodes.  
- Displays the BusNet4 route between them.  

---

### Cell 11 — CCTV Dataset Selector
- Lets users select one or more CCTV datasets from config folder.  
- Returns a merged DataFrame proxy.  

---

### Cell 12 — CCTV Traffic Analysis
- Visualises traffic counts for selected cameras.  
- Supports date range filtering, line/bar/stacked charts.  

---

### Cell 13 — CCTV Camera Map
- Displays cameras on map with average or total counts.  
- Supports CSV export of displayed values.  

---

### Cell 14 — Vehicle Classification Dataset Selector
- Multi-select for vehicle classification CSVs.  
- Returns merged DataFrame proxy.  

---

### Cell 15 — Vehicle Classification Analysis
- Charts showing classification trends over time.  

---

### Cell 16 — Vehicle Map
- Displays vehicle type summaries on map per camera.  

---

### Cell 17 — Bus Routes via CCTV Cameras
- Overlays bus routes that pass through selected cameras.  
- Optional CSV export (no duplicates).  

---

### Cell 18 — Bus Stops with Businesses
- Displays bus stops alongside business dataset points.  

---

### Cell 19 — Postcode Dataset Map
- Shows postcode data from all available datasets.  
- Allows manual postcode search and selection.  

---

## 5. Data Flow

1. **City selection**  
   → `start_up_manager` loads config  
2. **Data loading**  
   → `data_manager` retrieves postcodes, boundaries, CCTV, routes  
3. **Processing**  
   → Each manager handles its domain logic (routing, CCTV, business, etc.)  
4. **Rendering**  
   → `map_renderer` creates maps  
   → `ui_manager` adds widgets and export buttons  
5. **Export**  
   → `export_saver` saves user-visible data to CSV  

---

## 6. Maintenance Notes

- Keep `cell_manager.py` **thin** — only orchestrate calls.  
- Place all new logic in a **dedicated manager file**.  
- Use `ui_manager.py` for UI widgets (dropdowns, buttons).  
- Use `data_manager.py` for CSV/JSON loaders and preprocessing.  
- Use `export_saver.py` for all CSV exports.  
- Follow naming conventions (`b_` prefix for boundaries, `pc_` prefix for postcodes, `r_` prefix for routes).  

---

## 7. Exports

- Exports are saved in `exports/map_views` by default.  
- Filenames are prefixed with map type + timestamp (e.g. `heatmap_Affluence_CityCentre_20250326_120000.csv`).  
- Exports only contain the **data visible on the map popups**, not the full dataset.

---
