# ui_manager.py

**Role:** Notebook UI widgets, selectors, and small orchestration wrappers around exports.

## Known / Referenced UI Hooks
- Boundary + accept controls: `display_boundary_dropdown`, `display_accept_button`, `display_toggle`
- Heatmap selector: `display_ui_for_heatmap`
- CCTV: `display_cctv_dataset_selector`, `display_cctv_controls`, `display_cctv_map_with_export`
- Vehicle: `display_vehicle_dataset_selector`, `display_vehicle_controls`, `display_vehicle_map_with_export`
- Export: `show_export_button(view_df, prefix)`

## Behavior
- Returns or displays `ipywidgets` controls and wires callbacks to re-render maps.
- Export wrappers typically:
  - build a trimmed “view” DataFrame (from `map_renderer.get_*_view`)
  - pass it into `export_saver.save_dataframe_snapshot()`.

## Notes 
- If `display_cctv_map_with_export` / `display_vehicle_map_with_export` are missing, implement small wrappers that:
  1) render the map using the relevant manager,
  2) compute the view DataFrame,
  3) call `show_export_button(view_df, prefix)`.
