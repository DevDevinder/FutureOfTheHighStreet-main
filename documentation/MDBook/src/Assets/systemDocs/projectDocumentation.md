# System Overview

This guide explains the **structure**, **purpose**, and **usage** of the interactive city data notebook.  
It is written for developers and maintainers working in **VSCode + GitHub**.


The notebook (`.ipynb`) provides an interactive interface for exploring **city datasets** such as:

- Postcodes  
- Transport (walking, cycling, driving, buses)  
- CCTV traffic counts  
- Businesses  

It uses **ipywidgets** for interactive controls and **folium/ipyleaflet** for map visualisation.

All heavy logic lives in **modular Python scripts** (`pythonScripts/`), while the notebook itself simply orchestrates them and displays the output, acting as the user interface.


## 🏗️ 1. Architecture

```text
notebook.ipynb
│
├─ cell_manager.py        # Orchestrates notebook cells (thin wrappers used only to remove clutter out of notebook)
├─ start_up_manager.py    # Notebook setup, city selector, config loading
├─ data_manager.py        # Data loading/cleaning (CSV, JSON, postcodes, routes)
├─ map_renderer.py        # Map rendering (base maps, heatmaps, routes, legends)
├─ routing_manager.py     # Walking, cycling, driving routes (pyroutelib3)
├─ postcode_map_manager.py# Postcode search and map display
├─ marker_manager.py      # Interactive marker placement/removal
├─ ui_manager.py          # Widgets, dropdowns, buttons, export logic
├─ export_saver.py        # Save map views to CSV
├─ cctv_manager.py        # CCTV datasets, charts, and camera map views
└─ business_manager.py    # Business mapping (bus stops + businesses)
```

> **Key Principles**
>
> - Keep `cell_manager.py` thin — it only calls into other managers.
> - Put logic in the relevant manager file.
> - Put widgets/UI in `ui_manager.py`.
> - All CSV exports go through `export_saver.py`.


---

### Running
#
## ▶️ 2. Running the Notebook

1. Open the `.ipynb` file in **VSCode** (ensure Jupyter extension installed).  
2. Run **Cell 1** to initialise environment and load city config.  
3. After Cell 1, any other cell can be executed independently.  
4. Data exports will appear in the `exports/` folder.  


## 📑 3. Cell-by-Cell Reference

### ⚙️ Cell 1 — Setup
<a href="../Assets/pics/diagrams/cell1_flow.png" target="_blank">
    <img src="../Assets/pics/diagrams/cell1_flow.png" alt="Cell 1 Flow Diagram" style="max-width: 100%; height: auto; cursor: zoom-in;" />
</a>

Initialises the notebook environment:
- Loads available cities (`start_up_manager.get_available_cities`).  
- Displays city dropdown.  
- Loads config (`data_manager.load_city_config`). 



### 🗺️ Cell 2 — Base Map
<a href="../Assets/pics/diagrams/cell2_flow.png" target="_blank">
    <img src="../Assets/pics/diagrams/cell2_flow.png" alt="Cell 2 Flow Diagram" style="max-width: 100%; height: auto; cursor: zoom-in;" />
</a>

- Displays base map with all boundaries.  
- Uses `map_renderer.combine_map_layers` + `map_renderer.add_boundaries`. 
- Good for confirming correct city data loaded 

### 📍 Cell 3 — Postcodes within Boundaries
<a href="../Assets/pics/diagrams/cell3_flow.png" target="_blank">
    <img src="../Assets/pics/diagrams/cell3_flow.png" alt="Cell 3 Flow Diagram" style="max-width: 100%; height: auto; cursor: zoom-in;" />
</a>

- Boundary selector for postcode filtering.  
- Shows postcode markers on map(within selected geojson drawn boundaries).  
- Exports selected postcodes to CSV.  

### 🔥 Cell 4 — Heatmap
<a href="../Assets/pics/diagrams/cell4_flow.png" target="_blank">
    <img src="../Assets/pics/diagrams/cell4_flow.png" alt="Cell 4 Flow Diagram" style="max-width: 100%; height: auto; cursor: zoom-in;" />
</a>

- Heatmap of **Affluence, Population, or Households**.  
- Optional boundary overlay.  
- Export of visible values.  


### 🚌 Cell 5 — Initialise BusNet4
<a href="../Assets/pics/diagrams/cell5_flow.png" target="_blank">
    <img src="../Assets/pics/diagrams/cell5_flow.png" alt="Cell 5 Flow Diagram" style="max-width: 100%; height: auto; cursor: zoom-in;" />
</a>

- Sets up BusNet4 bus network within city boundary.  
- Must be run before any bus routing cells.  

### 🚏 Cell 6 — Closest Postcodes to Commercial Zones
<a href="../Assets/pics/diagrams/cell6_flow.png" target="_blank">
    <img src="../Assets/pics/diagrams/cell6_flow.png" alt="Cell 6 Flow Diagram" style="max-width: 100%; height: auto; cursor: zoom-in;" />
</a>

- Compares **City Centre** vs **Shopping Districts**.  
- Shows only postcodes where selected zone is closer.  
- Draws walking/cycling/driving routes.  
- Saves route data via `data_manager.save_route_data`, for building new data for future analysis in "data/<cityName>/routes"

### 🟢🔴 Cell 7 — Red/Green Zone Visualisation
<a href="../Assets/pics/diagrams/cell7_flow.png" target="_blank">
    <img src="../Assets/pics/diagrams/cell7_flow.png" alt="Cell 7 Flow Diagram" style="max-width: 100%; height: auto; cursor: zoom-in;" />
</a>

- Adds markers showing proximity:  
  - **Green** = closer to selected zone.  
  - **Red** = closer to otherzones.  

### 🔄 Cell 8 — Backup BusNet4 Init
![Cell 1 Flow Diagram](../Assets/pics/diagrams/cell8_flow.png)
- Runs `initialise_busnetfour()` if Cell 5 was skipped.  

### 🚍 Cell 9 — Bus Route to Boundary
![Cell 1 Flow Diagram](../Assets/pics/diagrams/cell9_flow.png)
- Draws route from a fixed start point to a city-centre polygon.  

### 📮 Cell 10 — Bus Route Between Postcodes
![Cell 1 Flow Diagram](../Assets/pics/diagrams/cell10_flow.png)
- Select two postcodes → shows BusNet4 route.  


### 🎥 Cell 11 — CCTV Dataset Selector
![Cell 1 Flow Diagram](../Assets/pics/diagrams/cell11_flow.png)
- Multi-select CCTV datasets.  
- Returns merged DataFrame proxy.  

### 📊 Cell 12 — CCTV Traffic Analysis
![Cell 1 Flow Diagram](../Assets/pics/diagrams/cell12_flow.png)
- Traffic volume charts (line, bar, stacked).  
- Filter by date range and cameras. 

### 🗺️ Cell 13 — CCTV Camera Map
![Cell 1 Flow Diagram](../Assets/pics/diagrams/cell13_flow.png)
- Camera map with average/total counts.  
- Export to CSV supported.  

### 🚗 Cell 14 — Vehicle Dataset Selector
![Cell 1 Flow Diagram](../Assets/pics/diagrams/cell14_flow.png)
- Multi-select vehicle classification CSVs.  

### 📉 Cell 15 — Vehicle Classification Analysis
![Cell 1 Flow Diagram](../Assets/pics/diagrams/cell15_flow.png)
- Charts showing vehicle type trends.  

### 🗺️ Cell 16 — Vehicle Map
![Cell 1 Flow Diagram](../Assets/pics/diagrams/cell16_flow.png)
- Map showing aggregated vehicle types per camera.  

### 🚌🎥 Cell 17 — Bus Routes via CCTV Cameras
![Cell 1 Flow Diagram](../Assets/pics/diagrams/cell17_flow.png)
- Shows bus routes passing through CCTV-selected areas.  
- Prevents duplicate export.  

### 🏪 Cell 18 — Businesses + Bus Stops
![Cell 1 Flow Diagram](../Assets/pics/diagrams/cell18_flow.png)
- Displays businesses with bus stop data.
- allows for selecting data columns to display on marker labels.  

### 📍 Cell 19 — Postcode Dataset Map
![Cell 1 Flow Diagram](../Assets/pics/diagrams/cell19_flow.png)
- Shows postcode datasets together.  
- Manual postcode search supported.  


## 🔄 4. typical Data Flows

```text
City selection (start_up_manager)
    ↓
Data loading (data_manager)
    ↓
Processing logic (routing_manager, cctv_manager, business_manager, etc.)
    ↓
Rendering (map_renderer + folium)
    ↓
UI controls (ui_manager)
    ↓
Exports (export_saver)

```

## 🛠️ 5. Maintenance Notes

- Keep **orchestration** in `cell_manager.py`.  
- Put **appropriate logic** in a dedicated manager file.  
- Put **UI widgets** in `ui_manager.py`.  
- Use `export_saver.py` for all personal CSV exports.  
- Config file naming conventions:  
  - `b_` → boundaries  
  - `pc_` → postcodes  
  - `r_` → routes  

This notebook is designed to be highly flexible, modular, and reusable, enabling efficient analysis and processing of various datasets from different cities without needing to modifiy the codebase. 
```
Note:
- The primary aim of the system design is to maintain adaptability and modularity, allowing for easy extension and reuse across diverse urban datasets without needing to modify existing code.
- Over time, some aspects of the codebase may have lost a degree of modularity and flexibility as it has grown for newer needs.
- Recomended Future work first steps would be to make further improvements to the system structure that enhance these core aims.
```

