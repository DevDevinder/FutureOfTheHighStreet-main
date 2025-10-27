# routing_manager.py

**Role:** Point-to-point routing for walking/cycling/driving (and helpers for distance calculation). Bus routes via BusNet4 are rendered by `map_renderer.display_busnet_route_on_map`.

## Referenced Functions (from flow)
- `initialize_router(mode: str) -> CustomRouter`  # creates router for 'foot', 'cycle', 'car'
- `calculate_distances_and_routes(start_coord, destinations_df, routers) -> dict`  
  - Computes distance for each mode and returns `{"Walking": miles, "Cycling": miles, "Driving": miles}` and polyline coords per mode.
- `find_nearest_destination(start_coord, destinations_df) -> row/index`

## Expected Behavior
- Wraps a routing engine (e.g., pyroutelib3 / OSRM / custom) behind a simple interface.
- `CustomRouter.route(start, end)` returns a list of coordinates.
- Distances returned in miles; coordinates suitable for Folium polylines.

## Notes
- Ensure proper handling when no route is found (return `None` and don’t crash maps).
