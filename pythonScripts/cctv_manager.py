import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import folium


from ipywidgets import Dropdown, VBox, Output
from IPython.display import display

import math
def load_cctv_data(csv_path):
    df = pd.read_csv(csv_path)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['HourStart'] = df['Hour'].str.extract(r'(\d{1,2}):00')[0].astype('Int64')
    return df

def load_df_cctv_data(df):
    '''Load the CCTV data '''
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['HourStart'] = df['Hour'].str.extract(r'(\d{1,2}):00')[0].astype('Int64')
    


def get_camera_list(df):
    '''Get a list of the camera names from the df.'''
    return sorted(df['Source'].dropna().unique())

def plot_by_date(df, cameras, chart_type='Line', traffic_column='Combined'):
    '''Plot traffic data by date.'''
    num_dates = df['Date'].nunique()
    fig_width = max(10, min(0.5 * num_dates, 30))
    plt.figure(figsize=(fig_width, 6))

    if chart_type == 'Stacked Bar(use with one camera)':
        grouped = df[df['Source'].isin(cameras)]
        grouped = grouped.groupby('Date')[['F__of_Bicycles', 'F__of_People', 'F__of_Road_Vehicles']].sum()
        grouped.plot(kind='bar', stacked=True, figsize=(fig_width, 6))
    else:
        for camera in cameras:
            df_cam = df[df['Source'] == camera]
            grouped = df_cam.groupby('Date')

            if traffic_column == 'Combined':
                values = grouped[['F__of_Bicycles', 'F__of_People', 'F__of_Road_Vehicles']].sum().sum(axis=1)
            else:
                values = grouped[traffic_column].sum()

            if chart_type == 'Line':
                plt.plot(values.index, values, label=camera)
            elif chart_type == 'Bar':
                plt.bar(values.index, values, label=camera)

    plt.title("Traffic Volume Over Time")
    plt.ylabel("Total Count")
    plt.xlabel("Date")
    plt.xticks(rotation=45, ha='right')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_by_day(df, cameras, chart_type='Line', traffic_column='Combined'):
    '''Plot traffic data by day of the week.'''
    import numpy as np
    weekday_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    fig, ax = plt.subplots(figsize=(10, 6))

    if chart_type == 'Stacked Bar(use with one camera)':
        grouped = df[df['Source'].isin(cameras)]
        grouped = grouped.groupby('Day')[['F__of_Bicycles', 'F__of_People', 'F__of_Road_Vehicles']].sum()
        grouped = grouped.reindex(weekday_order)
        grouped.plot(kind='bar', stacked=True, ax=ax)
    elif chart_type == 'Bar' and len(cameras) > 1:

        bar_width = 0.8 / len(cameras)
        x = np.arange(len(weekday_order))

        for i, camera in enumerate(cameras):
            df_cam = df[df['Source'] == camera]
            grouped = df_cam.groupby('Day')
            values = (
                grouped[['F__of_Bicycles', 'F__of_People', 'F__of_Road_Vehicles']].sum().sum(axis=1)
                if traffic_column == 'Combined'
                else grouped[traffic_column].sum()
            )
            values = values.reindex(weekday_order).fillna(0)
            ax.bar(x + i * bar_width, values, bar_width, label=camera)

        ax.set_xticks(x + bar_width * (len(cameras) - 1) / 2)
        ax.set_xticklabels(weekday_order)
    else:
        for camera in cameras:
            df_cam = df[df['Source'] == camera]
            grouped = df_cam.groupby('Day')
            values = (
                grouped[['F__of_Bicycles', 'F__of_People', 'F__of_Road_Vehicles']].sum().sum(axis=1)
                if traffic_column == 'Combined'
                else grouped[traffic_column].sum()
            )
            values = values.reindex(weekday_order).fillna(0)

            if chart_type == 'Line':
                ax.plot(values.index, values, marker='o', label=camera)
            elif chart_type == 'Bar':
                ax.bar(values.index, values, label=camera)

    ax.set_title("Traffic Volume by Day of Week")
    ax.set_ylabel("Total Count")
    ax.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_by_hour(df, cameras, chart_type='Line', traffic_column='Combined'):
    '''Plot traffic data by hour of the day.'''
  
    fig, ax = plt.subplots(figsize=(10, 6))

    if chart_type == 'Stacked Bar(use with one camera)':
        grouped = df[df['Source'].isin(cameras)]
        grouped = grouped.groupby('HourStart')[['F__of_Bicycles', 'F__of_People', 'F__of_Road_Vehicles']].sum()
        grouped.plot(kind='bar', stacked=True, ax=ax)
    elif chart_type == 'Bar' and len(cameras) > 1:
        bar_width = 0.8 / len(cameras)
        x = np.arange(0, 24)

        for i, camera in enumerate(cameras):
            df_cam = df[df['Source'] == camera]
            grouped = df_cam.groupby('HourStart')
            values = (
                grouped[['F__of_Bicycles', 'F__of_People', 'F__of_Road_Vehicles']].sum().sum(axis=1)
                if traffic_column == 'Combined'
                else grouped[traffic_column].sum()
            )
            values = values.reindex(range(24)).fillna(0)
            ax.bar(x + i * bar_width, values, bar_width, label=camera)

        ax.set_xticks(x + bar_width * (len(cameras) - 1) / 2)
        ax.set_xticklabels([str(h) for h in range(24)])
    else:
        for camera in cameras:
            df_cam = df[df['Source'] == camera]
            grouped = df_cam.groupby('HourStart')
            values = (
                grouped[['F__of_Bicycles', 'F__of_People', 'F__of_Road_Vehicles']].sum().sum(axis=1)
                if traffic_column == 'Combined'
                else grouped[traffic_column].sum()
            )
            values = values.reindex(range(24)).fillna(0)

            if chart_type == 'Line':
                ax.plot(values.index, values, marker='o', label=camera)
            elif chart_type == 'Bar':
                ax.bar(values.index, values, label=camera)

    ax.set_title("Traffic Volume by Hour of Day")
    ax.set_xlabel("Hour")
    ax.set_ylabel("Total Count")
    ax.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()





def display_cctv_map(df, selected_cameras=None, date_min=None, date_max=None, agg_func='mean'):
    '''Display a map with camera locations and aggregated traffic data.'''
    if date_min is not None and date_max is not None:
        df = df[(df['Date'] >= date_min) & (df['Date'] <= date_max)]

    if selected_cameras is None:
        selected_cameras = df['Source'].unique().tolist()

    subset = df[df['Source'].isin(selected_cameras)]
    group = subset.groupby('Source')

    if agg_func == 'sum':
        stats = group[['F__of_Bicycles', 'F__of_People', 'F__of_Road_Vehicles']].sum()
    else:
        stats = group[['F__of_Bicycles', 'F__of_People', 'F__of_Road_Vehicles']].mean()

    coord_map = df[['Source', 'Coordinates']].drop_duplicates().set_index('Source')
    m = folium.Map(location=[56.460, -2.97], zoom_start=14)

    for source in selected_cameras:
        coords = coord_map.loc[source, 'Coordinates']
        lat, lon = map(float, coords.split(','))

        if source in stats.index:
            row = stats.loc[source]
            label = f"""
                <b>{source}</b><br>
                {agg_func.title()} Bicycles: {row['F__of_Bicycles']:.1f}<br>
                {agg_func.title()} People: {row['F__of_People']:.1f}<br>
                {agg_func.title()} Vehicles: {row['F__of_Road_Vehicles']:.1f}
            """
        else:
            label = f"<b>{source}</b><br>No data in range."

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(label, max_width=300),
            tooltip=source,
            icon=folium.Icon(color='blue', icon='camera', prefix='fa')
        ).add_to(m)

    return m

#cctv vehicle classification data
def load_vehicle_classification_data(csv_path):
    df = pd.read_csv(csv_path)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['HourStart'] = df['Hour'].str.extract(r'(\d{1,2}):')[0].astype('Int64')
    return df


# Bus routes through cctv cams.
def display_bus_routes_through_cctv(busNet, cctv_df, map_obj):
    
    shown_routes = set()

    for coord_str in cctv_df['Coordinates'].dropna().unique():
        lat, lon = map(float, coord_str.split(','))

        stop_id = busNet.findClosestStop(lat, lon, threshold=1000)  # (Threshold is metres 50-60 works well)
        if not stop_id:
            continue

        route_ids = busNet.getRoutesViaStop(stop_id)
        for route_id in route_ids:
            if route_id in shown_routes:
                continue  # avoid duplicates

            route_coords = busNet.getRouteCoordinates(route_id)
            if not route_coords:
                continue

            polyline = folium.Polyline(
                locations=route_coords,
                color="orange",
                fill=False,
                weight=3,
                opacity=0.7
            )
            map_obj.add_layer(polyline)
            shown_routes.add(route_id)



def haversine(lat1, lon1, lat2, lon2):
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    a = math.sin(dLat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dLon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return 6371 * c  # (km)

import json
from shapely.geometry import Point, LineString

def show_bus_routes_for_camera(config, busNet, gStops, cctv_df, router, max_dist=70):
    from ipywidgets import Dropdown, Output, VBox, Layout, Button, HBox
    from IPython.display import display
    from shapely.geometry import Point, LineString
    import folium
    import os, csv, json

    if cctv_df is None or cctv_df.empty:
        print("CCTV data is empty.")
        return

    # preload fast straightlines (unchanged)
    route_shapes = {}
    all_route_ids = [node for node in busNet.G.nodes if 'route' in busNet.G.nodes[node]]
    for route_id in all_route_ids:
        route_data = busNet.G.nodes[route_id].get("route", [])
        coords = []
        for stop_from, stop_to, *_ in route_data:
            try:
                from_node = busNet.G.nodes[stop_from]
                to_node = busNet.G.nodes[stop_to]
                coords.append((from_node["stop_lon"], from_node["stop_lat"]))
                coords.append((to_node["stop_lon"], to_node["stop_lat"]))
            except:
                continue
        if coords:
            try:
                route_shapes[route_id] = LineString(coords)
            except:
                continue

    # UI widgets (unchanged)
    camera_options = {
        row["Source"]: row["Coordinates"]
        for _, row in cctv_df.dropna(subset=["Coordinates", "Source"]).iterrows()
    }
    camera_dropdown = Dropdown(options=camera_options, description='Camera:')
    route_dropdown = Dropdown(options=[], description='Highlight Route:', layout=Layout(width='50%'))
    export_btn = Button(description="Export routes (no duplicates)", button_style='success')
    out = Output()

    # storage for current camera’s intersecting data {route_id: full_path[(lat,lon), ...]}
    intersecting_data = {}

    def render_map(center, cam_buffer, highlight_route_id=None):
        m = folium.Map(location=center, zoom_start=14)
        folium.Marker(location=center, tooltip="CCTV Camera", icon=folium.Icon(color="black")).add_to(m)
        folium.Circle(location=center, radius=max_dist, color="green", fill=False).add_to(m)

        included_stops = set()

        for route_id, full_path in intersecting_data.items():
            try:
                r, op, dest = route_id.split(":")
            except:
                r, op, dest = route_id, "?", "?"
            coords = [(lon, lat) for lat, lon in full_path]
            popup = f"{r} → {dest} ({op})"

            folium.GeoJson(
                data={
                    "type": "Feature",
                    "geometry": {"type": "LineString", "coordinates": coords},
                    "properties": {"popup": popup}
                },
                name=route_id,
                style_function=lambda feature, rid=route_id: {
                    'color': 'red' if rid == highlight_route_id else 'blue',
                    'weight': 6 if rid == highlight_route_id else 3,
                    'opacity': 1.0 if rid == highlight_route_id else 0.5
                },
                tooltip=popup
            ).add_to(m)

        # Stop markers (unchanged)
        for route_id in intersecting_data:
            route_data = busNet.G.nodes[route_id].get("route", [])
            for stop_from, stop_to, *_ in route_data:
                included_stops.update([stop_from, stop_to])

        for sid in included_stops:
            node = busNet.G.nodes.get(sid, {})
            s_lat, s_lon = node.get("stop_lat"), node.get("stop_lon")
            s_name = node.get("stop_name", "Unknown")
            if s_lat and s_lon:
                folium.CircleMarker(
                    location=(s_lat, s_lon),
                    radius=4,
                    color="black",
                    fill=True,
                    fill_opacity=0.7,
                    popup=f"{sid}<br>{s_name}"
                ).add_to(m)

        return m

    def on_camera_select(change):
        if not change['new']:
            return
        out.clear_output()
        route_dropdown.options = []
        route_dropdown.value = None
        intersecting_data.clear()

        lat, lon = map(float, change['new'].split(','))
        center = (lat, lon)
        cam_point = Point(lon, lat)
        radius_deg = max_dist / 111320
        cam_buffer = cam_point.buffer(radius_deg)

        # Find intersecting straight routes (unchanged)
        intersecting_routes = [rid for rid, line in route_shapes.items() if line.intersects(cam_buffer)]
        for route_id in intersecting_routes:
            route_data = busNet.G.nodes[route_id].get("route", [])
            full_path = []
            for stop_from, stop_to, *_ in route_data:
                try:
                    node_from = busNet.G.nodes[stop_from]
                    node_to = busNet.G.nodes[stop_to]
                    start_coords = (node_from["stop_lat"], node_from["stop_lon"])
                    end_coords = (node_to["stop_lat"], node_to["stop_lon"])

                    start_node = router.router.findNode(*start_coords)
                    end_node = router.router.findNode(*end_coords)
                    status, raw_path = router.router.doRoute(start_node, end_node)
                    if status != 'success' or not raw_path:
                        continue

                    path_coords = [router.router.nodeLatLon(n) for n in raw_path]
                    full_path.extend(path_coords)
                except:
                    continue
            if full_path:
                intersecting_data[route_id] = full_path

        with out:
            m = render_map(center, cam_buffer)
            display(m)

        route_dropdown.options = sorted([
            (f"{rid.split(':')[0]} → {rid.split(':')[-1]}", rid) for rid in intersecting_data
        ])

    def on_route_select(change):
        if not camera_dropdown.value or not change['new']:
            return
        out.clear_output()
        lat, lon = map(float, camera_dropdown.value.split(','))
        center = (lat, lon)
        cam_point = Point(lon, lat)
        radius_deg = max_dist / 111320
        cam_buffer = cam_point.buffer(radius_deg)
        with out:
            m = render_map(center, cam_buffer, highlight_route_id=change['new'])
            display(m)

    def _current_camera_name():
        """Get the selected camera's name from the options dict."""
        coord_val = camera_dropdown.value
        for name, coords in camera_options.items():
            if coords == coord_val:
                return name
        return None

    def _export_rows_for_current_selection():
        """Build rows (dicts) ready to write for the current camera + all intersecting routes."""
        cam_name = _current_camera_name()
        if not cam_name or not intersecting_data:
            return []

        cam_lat, cam_lon = map(float, camera_dropdown.value.split(','))
        rows = []
        for route_id, path in intersecting_data.items():
            # route_id format: "{routeNo}:{Operator}:{Destination}"
            parts = route_id.split(":")
            route_no = parts[0] if len(parts) > 0 else route_id
            operator = parts[1] if len(parts) > 1 else "?"
            destination = parts[2] if len(parts) > 2 else "?"

            rows.append({
                "Camera": cam_name,
                "CameraLat": cam_lat,
                "CameraLon": cam_lon,
                "RouteID": route_id,
                "RouteNo": route_no,
                "Operator": operator,
                "Destination": destination,
                # store coordinates as JSON string to be safe for CSV
                "PathCoordinates": json.dumps(path)
            })
        return rows

    def on_export_click(_):
        """Append unique rows (Camera+RouteID) to exports/cctv_bus_routes.csv without duplicates."""
        rows = _export_rows_for_current_selection()
        if not rows:
            print("Nothing to export. Select a camera first.")
            return

        os.makedirs("../exports", exist_ok=True)
        filepath = os.path.join("exports", "cctv_bus_routes.csv")
        fieldnames = ["Camera", "CameraLat", "CameraLon", "RouteID", "RouteNo", "Operator", "Destination", "PathCoordinates"]

        existing_keys = set()
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            with open(filepath, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    existing_keys.add((r.get("Camera", ""), r.get("RouteID", "")))

        # filter out duplicates
        new_rows = [r for r in rows if (r["Camera"], r["RouteID"]) not in existing_keys]
        if not new_rows:
            print("No new routes to add (all already exported for this camera).")
            return

        write_header = not os.path.exists(filepath) or os.path.getsize(filepath) == 0
        with open(filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerows(new_rows)

        print(f"✅ Exported {len(new_rows)} new route(s) to {filepath}")

    # Wire up events
    camera_dropdown.observe(on_camera_select, names='value')
    route_dropdown.observe(on_route_select, names='value')
    export_btn.on_click(on_export_click)

    # Display UI (added export button at the end; everything else unchanged)
    display(VBox([camera_dropdown, out, HBox([route_dropdown, export_btn])]))
