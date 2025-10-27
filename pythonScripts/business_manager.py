import pandas as pd
import folium
from folium.plugins import MarkerCluster
from ipywidgets import Dropdown, SelectMultiple, VBox, Output, FloatSlider, RadioButtons
from IPython.display import display
from pythonScripts import BusNet4
from shapely.geometry import Point
from shapely.ops import nearest_points

business_df = None
category_col = "category"
lat_col = "lattitude"
lon_col = "longitude"

def load_business_data(csv_path):
    global business_df
    business_df = pd.read_csv(csv_path)
    business_df[lat_col] = pd.to_numeric(business_df[lat_col], errors='coerce')
    business_df[lon_col] = pd.to_numeric(business_df[lon_col], errors='coerce')
    print(f"Business data loaded: {len(business_df)} rows")

def display_business_map():
    """
    Display businesses + nearby bus stops on a folium map and provide a one-click CSV export.
    Export OVERWRITES (no append) to: exports/business_bus_stops.csv

    CSV always includes:
      business_name, category, business_lat, business_lon,
      stop_id, stop_name, stop_lat, stop_lon, distance_m

    In addition, any fields chosen in the "Popup Fields" selector (i.e., sub-categories or other columns)
    are INCLUDED AS EXTRA COLUMNS in the CSV.
    """
    import os
    import pandas as pd
    import folium
    from folium.plugins import MarkerCluster
    from shapely.geometry import Point
    from ipywidgets import Dropdown, SelectMultiple, VBox, HBox, Output, FloatSlider, RadioButtons, Button, HTML, Layout
    from IPython.display import display
    from pythonScripts import BusNet4

    # Expect that load_business_data(...) has been called already
    global business_df, category_col, lat_col, lon_col
    if business_df is None or business_df.empty:
        print("Business data not loaded. Call load_business_data(...) first.")
        return

    # --- UI ---
    categories = sorted(business_df[category_col].dropna().unique().tolist())
    all_fields = [c for c in business_df.columns if c not in [category_col, lat_col, lon_col]]

    category_dd = Dropdown(options=categories, description="Category:", layout=Layout(width="260px"))
    fields_sel = SelectMultiple(options=all_fields, description="Popup Fields:", layout=Layout(width="360px", height="140px"))
    radius_slider = FloatSlider(value=300, min=100, max=2000, step=100, description="Radius (m)")
    draw_mode = RadioButtons(options=["Circles", "Lines"], value="Circles", description="Draw:")
    export_btn = Button(description="Export CSV (overwrite)", button_style="success", icon="save")
    export_note = HTML(value="<span style='color:#666'>Saves to <b>exports/business_bus_stops.csv</b></span>")

    out_map = Output()
    out_status = Output()

    # Load bus stops (points)
    try:
        gdf_stops = BusNet4.getStops()
        stop_points = gdf_stops[gdf_stops.geometry.notnull() & gdf_stops.geometry.apply(lambda g: g.geom_type == "Point")]
    except Exception as e:
        print(f"Could not load bus stops from BusNet4: {e}")
        return

    M_PER_DEG = 111000.0  # rough conversion for short distances

    def _current_businesses():
        df = business_df.dropna(subset=[lat_col, lon_col]).copy()
        df = df[(df[lat_col] != 0) & (df[lon_col] != 0)]
        if category_dd.value is not None:
            df = df[df[category_col] == category_dd.value]
        return df

    def _rows_for_export(df_filtered, radius_m, selected_extra_fields):
        """
        Build rows for CSV. Alongside the fixed columns, include any user-selected extra fields
        (sub-categories etc.) from the business record.
        """
        rows = []
        if df_filtered.empty or stop_points.empty:
            return rows

        for _, brow in df_filtered.iterrows():
            b_lat = float(brow[lat_col])
            b_lon = float(brow[lon_col])
            b_name = str(brow.get("name", "Unnamed Business"))
            cat = str(brow.get(category_col, ""))

            b_point = Point(b_lon, b_lat)
            nearby = stop_points[stop_points.geometry.distance(b_point) * M_PER_DEG <= radius_m]

            # Prepare extra field values once per business row
            extra_values = {}
            for f in selected_extra_fields:
                try:
                    extra_values[f] = brow.get(f, "")
                except Exception:
                    extra_values[f] = ""

            for _, s in nearby.iterrows():
                geom = s.geometry
                s_lat, s_lon = float(geom.y), float(geom.x)
                s_name = s.get("stop_name", "Unnamed Stop")
                s_id = s.get("stop_id", "")

                dist_m = int(round(b_point.distance(geom) * M_PER_DEG))

                base = {
                    "business_name": b_name,
                    "category": cat,
                    "business_lat": b_lat,
                    "business_lon": b_lon,
                    "stop_id": s_id,
                    "stop_name": s_name,
                    "stop_lat": s_lat,
                    "stop_lon": s_lon,
                    "distance_m": dist_m
                }
                base.update(extra_values)  # <-- include selected sub-category/extra fields
                rows.append(base)
        return rows

    def _render_map():
        out_map.clear_output()
        df_f = _current_businesses()
        if df_f.empty:
            with out_map:
                print("No businesses found for the current selection.")
            return

        # Center map near the first business
        m = folium.Map(location=[df_f.iloc[0][lat_col], df_f.iloc[0][lon_col]], zoom_start=13)

        # Businesses layer
        business_layer = folium.FeatureGroup(name="Businesses")
        business_cluster = MarkerCluster()
        business_layer.add_child(business_cluster)

        for _, r in df_f.iterrows():
            lat, lon = r[lat_col], r[lon_col]
            b_name = r.get("name", "Unnamed Business")
            popup_items = [f"<b>{c}</b>: {r[c]}" for c in fields_sel.value if c in r and pd.notnull(r[c])]
            popup_html = "<br>".join(popup_items) if popup_items else b_name

            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=400),
                icon=folium.Icon(color="blue", icon="briefcase", prefix="fa")
            ).add_to(business_cluster)

            if draw_mode.value == "Circles":
                folium.Circle(location=[lat, lon], radius=radius_slider.value, color='blue', fill=True, fill_opacity=0.1).add_to(business_layer)
            else:
                # draw simple lines from business to nearby stops within the radius
                b_point = Point(lon, lat)
                nearby_stops = stop_points[stop_points.geometry.distance(b_point) * M_PER_DEG <= radius_slider.value]
                for _, s in nearby_stops.iterrows():
                    s_lat, s_lon = s.geometry.y, s.geometry.x
                    folium.PolyLine(locations=[(lat, lon), (s_lat, s_lon)], color='blue', weight=4, opacity=0.7).add_to(business_layer)

        m.add_child(business_layer)

        # Stops layer
        stop_layer = folium.FeatureGroup(name="Bus Stops")
        stop_cluster = MarkerCluster()
        stop_layer.add_child(stop_cluster)

        for _, s in stop_points.iterrows():
            s_lat, s_lon = s.geometry.y, s.geometry.x
            s_name = s.get("stop_name", "Unnamed Stop")
            folium.Marker(location=(s_lat, s_lon), popup=s_name, icon=folium.Icon(color="green", icon="bus", prefix="fa")).add_to(stop_cluster)

        m.add_child(stop_layer)
        m.add_child(folium.LayerControl())

        with out_map:
            display(m)

    def _on_any_change(_):
        _render_map()

    def _on_export(_):
        out_status.clear_output()
        df_f = _current_businesses()
        selected_fields = list(fields_sel.value)  # sub-category/extra columns chosen by the user
        rows = _rows_for_export(df_f, radius_slider.value, selected_fields)

        if not rows:
            with out_status:
                print("Nothing to export for the current selection.")
            return

        # Ensure folder & write (OVERWRITE)
        os.makedirs("exports", exist_ok=True)
        path = os.path.join("exports", "business_bus_stops.csv")

        # Keep a stable, readable column order: base columns first, then the selected extra fields (in the same order as UI)
        base_cols = ["business_name", "category", "business_lat", "business_lon", "stop_id", "stop_name", "stop_lat", "stop_lon", "distance_m"]
        df_out = pd.DataFrame(rows)
        # Move any selected extra fields to the end in the same order as selected in UI
        ordered_cols = base_cols + [f for f in selected_fields if f in df_out.columns]
        # Also include any other columns that slipped in (rare), to avoid dropping data
        other_cols = [c for c in df_out.columns if c not in ordered_cols]
        df_out = df_out[ordered_cols + other_cols]

        try:
            df_out.to_csv(path, index=False)  # OVERWRITE
            with out_status:
                print(f"✅ Exported {len(df_out)} rows to {path}")
        except Exception as e:
            with out_status:
                print(f"⚠ Failed to export CSV: {e}")

    # Wire up
    category_dd.observe(_on_any_change, names="value")
    fields_sel.observe(_on_any_change, names="value")
    radius_slider.observe(_on_any_change, names="value")
    draw_mode.observe(_on_any_change, names="value")
    export_btn.on_click(_on_export)

    # Layout
    controls = VBox([
        HBox([category_dd, draw_mode, radius_slider]),
        fields_sel,
        HBox([export_btn, export_note]),
        out_status,
        out_map
    ])
    display(controls)

    # Initial render
    _render_map()
