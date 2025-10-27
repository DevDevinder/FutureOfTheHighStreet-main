# cell_manager.py

**Role:** Orchestrator - each notebook cell calls a `cell_manager.*` function that wires UI + data + renderer.

## Typical Functions (Referenced)
- `run_boundary_postcode_selection(config)`
- `run_heatmap_with_boundaries(config)`
- `initialise_busnetfour()`
- `run_postcode_travel_time_search(config)`
- `run_closest_postcode_to_commercial_view(config)`
- `run_closest_zone_red_green_visualization(config)`
- `bus_route_to_boundary(config)`
- `run_postcode_route_between_selectable_points(config)`
- `run_cctv_dataset_selector(config) -> Proxy with .data`
- `run_cctv_analysis(df_or_proxy)`
- `run_cctv_map(df_or_proxy)`
- `run_vehicle_dataset_selector(config) -> Proxy with .data`
- `run_vehicle_analysis(vdf_or_proxy)`
- `run_vehicle_map(vdf_or_proxy)`
- `run_cctv_bus_routes(config, vehicle_df)`
- `run_business_mapping(config)`
- `display_postcode_data(config)`

## Pattern
- Collect UI state via `ui_manager.*`
- Load datasets via `data_manager.*`
- Build/augment map via `map_renderer.*`
- Provide export via `export_saver.save_dataframe_snapshot`

## Notes
- Keep this file **thin** as possible- goal is only direct calls to reduce notebook cell clutter; move logic to dedicated managers.
- Post adding export feature this file became slightly bulky due to data passing, work could be done to reduce this is possible.
