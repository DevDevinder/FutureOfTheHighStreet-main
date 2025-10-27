# postcode_map_manager.py

**Role:** Focused utilities for the “Postcode Dataset Map” feature (Cell 19) and postcode search.

## Referenced Entry Point
- `render_postcode_search_map(csv_paths, boundary_paths) -> folium.Map`

## Expected Behavior
- Load multiple postcode datasets.
- Filter by selected boundary (if provided).
- Render markers with labels (Postcode + coord).
- (Optional) Provide an export-ready trimmed view: `["Postcode","Latitude","Longitude"]`.

## Notes
- Confirm color/cluster rules and any dedupe across merged CSVs.
- Consider reusing `map_renderer.add_postcode_markers` and boundary helpers. 
