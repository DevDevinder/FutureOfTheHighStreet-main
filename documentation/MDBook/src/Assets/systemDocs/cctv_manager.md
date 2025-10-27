# cctv_manager.py

**Role:** CCTV and vehicle classification data loading, aggregation, charts, and map overlays.

## Public API (Selected)
- `load_cctv_data(csv_path) -> pd.DataFrame`
- `load_df_cctv_data(df) -> None`  # in-place parse for Date/HourStart
- `get_camera_list(df) -> list[str]`
- `plot_by_date(df, cameras, chart_type='Line', traffic_column='Combined') -> None`
- `plot_by_day(df, cameras, chart_type='Line', traffic_column='Combined') -> None`
- `plot_by_hour(df, cameras, chart_type='Line', traffic_column='Combined') -> None`
- `display_cctv_map(df, selected_cameras=None, date_min=None, date_max=None, agg_func='mean') -> folium.Map`
- `load_vehicle_classification_data(csv_path) -> pd.DataFrame`
- `display_bus_routes_through_cctv(busNet, cctv_df, map_obj) -> None`  *(ipyleaflet overlay usage noted)*
- `show_bus_routes_for_camera(config, busNet, gStops, cctv_df, router, max_dist=70) -> None`  # interactive UI + export

## Expected Columns
- CCTV: `["Date","Day","Hour","Source","Coordinates","F__of_Bicycles","F__of_People","F__of_Road_Vehicles"]`
- Vehicle classification: compatible columns for type-based grouping.

## Notes
- Charts use matplotlib; figure width adapts to data span.
- `show_bus_routes_for_camera` includes an export (no duplicate Camera+RouteID) → `export/cctv_bus_routes.csv` (typo: folder is `export`, not `exports`).
- Uses Shapely buffers to find routes near a camera; resolves full path via road router.
