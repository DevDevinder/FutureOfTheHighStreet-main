# map_renderer.py

**Role:** All Folium-based map building and overlay helpers (boundaries, markers, heatmaps, legend, routes, BusNet4 rendering).

## Public API (Selected)
- `generate_base_map(config) -> folium.Map`
- `add_boundaries(map_object, config) -> folium.Map`
- `add_selected_boundary(map_object, config, boundary_type) -> folium.Map`
- `add_postcode_markers(map_object, df) -> folium.Map`
- `combine_map_layers(config, *layer_functions) -> folium.Map`
- `add_dynamic_heatmap(map_object, df, column_name, label) -> folium.Map`
- `add_dynamic_markers(map_object, df, column_name) -> folium.Map`
- `add_color_legend(map_object, min_value, max_value, label="Legend") -> folium.Map`
- `display_routes_on_map(map_object, routes: dict) -> folium.Map`
- `add_route_legend(map_object) -> None`
- `show_closest_routes_only(config, map_object, route_df) -> folium.Map`
- `add_red_green_closest_zone_markers(map_object, df_city, df_shop, selected_area_type, selected_mode) -> folium.Map`
- `display_busnet_route_on_map(map_object, route_summary, gStops, start_coords=None, end_coords=None) -> folium.Map`

## View Builders (trimmed CSV “what you see is what you export”)
- `get_boundary_postcodes_view(df) -> pd.DataFrame`
- `get_heatmap_view(df, metric_col) -> pd.DataFrame`
- `build_boundary_postcodes_view(df) -> pd.DataFrame`
- `build_heatmap_marker_view(df, metric_col) -> pd.DataFrame`
- `add_dynamic_markers_with_view(m, df, metric_col) -> tuple[folium.Map, pd.DataFrame]`

## Inputs / Expected Columns
- Postcode DF: `["Postcode","Latitude","Longitude","Population","Households","Index of Multiple Deprivation","In Use?"]`
- Route CSVs: `"Start Postcode","Mode","Distance (miles)","Route Coordinates"`

## Notes
- Color mapping uses a custom `LinearSegmentedColormap`.
- Boundary labels are extracted from GeoJSON feature properties (`AreaName`/`PolicyRef`/`RefNo`).
- BusNet4 rendering draws: start/end markers, walking links to/from stops, stop markers, and orange bus segments.
