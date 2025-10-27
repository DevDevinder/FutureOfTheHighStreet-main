import pandas as pd
import folium
from shapely.geometry import Point
from ipywidgets import widgets, VBox, Output, HBox, Label, Text
from IPython.display import display
import geopandas as gpd
import os
import itertools

def render_postcode_search_map(csv_paths, boundary_paths):
    datasets = []
    color_cycle = itertools.cycle(['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightblue', 'darkgreen'])

    # Load datasets and normalize
    for path in csv_paths:
        if not os.path.exists(path):
            print(f"File not found: {path}")
            continue
        try:
            df = pd.read_csv(path)
            df.columns = [col.lower().strip() for col in df.columns]
            lat_col = next((col for col in df.columns if 'lat' in col), None)
            lon_col = next((col for col in df.columns if 'lon' in col), None)
            postcode_col = next((col for col in df.columns if 'postcode' in col), None)

            if lat_col and lon_col and postcode_col:
                df = df.rename(columns={
                    lat_col: 'latitude',
                    lon_col: 'longitude',
                    postcode_col: 'postcode'
                })
                df = df.dropna(subset=['latitude', 'longitude', 'postcode'])
                df['postcode'] = df['postcode'].astype(str).str.strip().str.upper()
                datasets.append({
                    'name': os.path.basename(path),
                    'df': df,
                    'color': next(color_cycle)
                })
        except Exception as e:
            print(f"Failed to load {path}: {e}")

    if not datasets:
        print("No valid postcode data found.")
        return

    all_postcodes = sorted(set(code for d in datasets for code in d['df']['postcode'].dropna().unique()))

    # Widgets
    postcode_multi = widgets.SelectMultiple(options=all_postcodes, description="Postcodes:", rows=8)
    postcode_manual = widgets.Text(description="+ Manual:", placeholder="Optional extra postcode")
    out = Output()
    field_selectors = {}

    # Field selectors per dataset
    for dataset in datasets:
        df = dataset['df']
        name = dataset['name']
        fields = [col for col in df.columns if col not in ['latitude', 'longitude', 'postcode']]
        selector = widgets.SelectMultiple(
            options=fields,
            value=fields[:1] if fields else [],
            description=name[:15],
            rows=6
        )
        field_selectors[name] = selector

    controls = VBox([postcode_multi, postcode_manual] + list(field_selectors.values()) + [out])

    def render_map():
        out.clear_output()
        selected_postcodes = list(postcode_multi.value)
        manual_code = postcode_manual.value.strip().upper()
        if manual_code:
            selected_postcodes.append(manual_code)

        if not selected_postcodes:
            with out:
                print("Please select or enter at least one postcode.")
            return

        # Initial map center
        for dataset in datasets:
            match = dataset['df'][dataset['df']['postcode'].isin(selected_postcodes)]
            if not match.empty:
                first = match.iloc[0]
                m = folium.Map(location=[first["latitude"], first["longitude"]], zoom_start=14)
                break
        else:
            with out:
                print("No data found for selected postcodes.")
            return

        # Add boundaries
        for b_path in boundary_paths:
            if not os.path.exists(b_path):
                continue
            try:
                gdf = gpd.read_file(b_path)
                folium.GeoJson(gdf, name=os.path.basename(b_path)).add_to(m)
            except Exception as e:
                print(f"Failed to load boundary {b_path}: {e}")

        # Add markers
        for dataset in datasets:
            df = dataset['df']
            name = dataset['name']
            color = dataset['color']
            selected_fields = field_selectors[name].value

            df_filtered = df[df['postcode'].isin(selected_postcodes)]
            for _, row in df_filtered.iterrows():
                popup = "<br>".join(f"<b>{col}</b>: {row[col]}" for col in selected_fields if col in row and pd.notnull(row[col]))
                folium.Marker(
                    location=(row["latitude"], row["longitude"]),
                    popup=folium.Popup(popup or f"{name}", max_width=300),
                    icon=folium.Icon(color=color, icon="info-sign")
                ).add_to(m)

        # Add legend
        legend_html = """
        <div style='position: fixed; bottom: 30px; left: 30px; z-index:9999;
                    background-color:white; padding: 10px; border:1px solid grey;'>
            <b>Dataset Legend:</b><br>
        """
        for dataset in datasets:
            legend_html += f"<span style='color:{dataset['color']};'>&#9679;</span> {dataset['name']}<br>"
        legend_html += "</div>"
        m.get_root().html.add_child(folium.Element(legend_html))

        m.add_child(folium.LayerControl())
        with out:
            display(m)

    def trigger_render(change=None):
        render_map()

    postcode_multi.observe(trigger_render, names='value')
    postcode_manual.observe(trigger_render, names='value')
    for selector in field_selectors.values():
        selector.observe(trigger_render, names='value')

    render_map()
    display(controls)
