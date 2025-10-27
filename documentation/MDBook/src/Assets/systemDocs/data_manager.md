# data_manager.py

**Role:** Data access layer (load configs, CSV/JSON, filter by boundary, compute derived columns, save routes).

## Public API
- `load_city_config(city: str) -> ModuleType | None`  # loads `data/{city}/config.py`
- `load_csv(path: str) -> pd.DataFrame | None`
- `load_json(path: str, city: str, description="JSON Data") -> dict | None`
- `load_postcodes(config) -> pd.DataFrame | None`  #  lat/lon numeric; drops invalids
- `load_filtered_postcodes(config, boundary_type: str) -> pd.DataFrame | None`
- `load_affluence_postcodes(config) -> pd.DataFrame | None`  # adds `Affluence Score`
- `getLatLonFromPCode(postcode: str, df_postcodes: pd.DataFrame) -> tuple[float,float] | None`
- `save_route_data(destination_type, start_postcode, distances: dict, routes: dict) -> None`  # de-duplicates (Start Postcode, Mode)
- `load_routes_csv(path: str) -> pd.DataFrame`  # parses Route Coordinates to lists

## Behavior / Side Effects
- Writes route CSVs under `data/dundee/routes/` (TODO: move to `config` path).
- Dedupe key: `(Start Postcode, Mode)` to prevent append duplicates.
- Boundary filtering uses Shapely, supports multi-feature GeoJSON.

## Notes

- `load_affluence_postcodes` removes rows with `Population <= 0` or `"In Use?" == "No"`.
- `load_routes_csv` uses `ast.literal_eval` to parse coordinate strings.
