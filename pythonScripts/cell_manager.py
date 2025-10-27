# cell_manager.py
# This file orchestrates notebook cells by calling into other modules.
# It intentionally avoids doing processing itself.

import ipywidgets as widgets
from IPython.display import display, clear_output
import pandas as pd

from pythonScripts import (
    BusNet4 as bus,
    data_manager,
    map_renderer,
    ui_manager,
    routing_manager,
    cctv_manager,
    business_manager,
    postcode_map_manager,
)

# -----------------------------
# Postcodes
# -----------------------------

def run_boundary_postcode_selection(config):
    """
    Filter postcodes by boundary, render the map, and show an Export CSV button
    that saves exactly what users see in popups (Postcode, Latitude, Longitude).
    """
    if config is None:
        print("Error: No city selected.")
        return

    boundary_selector, accept_button = ui_manager.get_ui_elements(config)
    map_output = widgets.Output()

    def update_map(_):
        selected_boundary = boundary_selector.value
        df_filtered = data_manager.load_filtered_postcodes(config, selected_boundary)

        with map_output:
            clear_output(wait=True)
            if df_filtered is not None and not df_filtered.empty:
                m = map_renderer.combine_map_layers(
                    config,
                    lambda mm: map_renderer.add_selected_boundary(mm, config, selected_boundary),
                    lambda mm: map_renderer.add_postcode_markers(mm, df_filtered),
                )
                display(m)

                # Delegate "what to export" and "button" to the right modules
                view_df = map_renderer.get_boundary_postcodes_view(df_filtered)
                ui_manager.show_export_button(
                    lambda: view_df,
                    prefix=f"boundary_postcodes_{str(selected_boundary).replace(' ', '_')}",
                    folder="exports/map_views",
                )
            else:
                print(f"No postcodes found for {selected_boundary}.")

    accept_button.on_click(update_map)
    display(boundary_selector, widgets.HBox([accept_button]), map_output)


def run_heatmap_with_boundaries(config):
    """
    Heatmap + markers with optional boundary overlay, plus Export CSV button
    that saves only the popup fields (Postcode, Population, Households, Metric).
    """
    if config is None:
        print("Error: No city selected.")
        return

    boundary_selector, boundary_toggle, heatmap_selector, accept_button = ui_manager.display_ui_for_heatmap(config)
    map_output = widgets.Output()

    def update_map(_):
        selected_boundary = boundary_selector.value
        include_boundary = boundary_toggle.value
        selected_heatmap = heatmap_selector.value

        print(f"🔄 Loading {selected_heatmap} heatmap with boundary: {selected_boundary if include_boundary else 'None'}")

        df_selected = data_manager.load_affluence_postcodes(config)

        # Metric + legend label
        if selected_heatmap == "Affluence":
            column_name = "Index of Multiple Deprivation"
            label = "Affluence Score (IMD)"
        elif selected_heatmap == "Population":
            column_name = "Population"
            label = "Population"
        else:
            column_name = "Households"
            label = "Households"

        with map_output:
            map_output.clear_output()
            if df_selected is not None and not df_selected.empty:
                m = map_renderer.generate_base_map(config)
                m = map_renderer.add_dynamic_heatmap(m, df_selected, column_name, label)
                m = map_renderer.add_dynamic_markers(m, df_selected, column_name)

                if include_boundary and selected_boundary is not None:
                    m = map_renderer.add_selected_boundary(m, config, selected_boundary)

                display(m)

                # Delegate "view df" + "export button"
                view_df = map_renderer.get_heatmap_view(df_selected, column_name)
                prefix = f"heatmap_{selected_heatmap}_{(selected_boundary if include_boundary else 'no_boundary')}".replace(" ", "_")
                ui_manager.show_export_button(lambda: view_df, prefix=prefix, folder="exports/map_views")
            else:
                print("No valid postcodes found.")

    accept_button.on_click(update_map)
    display(boundary_selector, boundary_toggle, heatmap_selector, accept_button, map_output)


def getLatLonFromPCode(postcode, df_postcodes):
    """Helper to fetch lat/lon for a postcode from a dataframe."""
    row = df_postcodes[df_postcodes["Postcode"] == postcode]
    if row.empty:
        print(f"ERROR: Postcode {postcode} not found in dataset.")
        return None
    return (row["Latitude"].values[0], row["Longitude"].values[0])

# -----------------------------
# Travel / Routing
# -----------------------------

def run_postcode_travel_time_search(config):
    """
    User enters a postcode; show BusNet4 route first, then walking/cycling/car routes on the same map.
    """
    if config is None:
        print("Error: No city selected.")
        return

    footRouter = routing_manager.initialize_router("foot", config.map_osm_gz, "gz")
    cycleRouter = routing_manager.initialize_router("cycle", config.map_osm_gz, "gz")
    carRouter = routing_manager.initialize_router("car", config.map_osm_gz, "gz")

    postcode_input = widgets.Text(placeholder="Enter postcode (e.g., DD3 0BN)", description="Postcode:", layout=widgets.Layout(width="300px"))
    destination_selector = widgets.Dropdown(options=["City Centre", "Shopping Districts"], value="City Centre", description="Destination:")
    calculate_button = widgets.Button(description="Calculate Routes", button_style="success")
    map_output = widgets.Output()

    def on_calculate(_):
        selected_postcode = postcode_input.value.strip().upper()
        dest_type = destination_selector.value
        if not selected_postcode:
            print("Please enter a postcode.")
            return

        df_postcodes = data_manager.load_affluence_postcodes(config)
        if df_postcodes is None or df_postcodes.empty:
            print("Postcode data not found.")
            return

        dest_df = data_manager.load_csv(config.pc_cityCentre) if dest_type == "City Centre" else data_manager.load_csv(config.pc_shopping)
        if dest_df is None or dest_df.empty:
            print(f"Destination data for {dest_type} is unavailable.")
            return

        start_coords = data_manager.getLatLonFromPCode(selected_postcode, df_postcodes)
        if not start_coords:
            return
        end_coords = routing_manager.find_nearest_destination(start_coords, dest_df)
        if not end_coords:
            return

        with map_output:
            map_output.clear_output()
            print(f"Drawing BusNet4 route from {start_coords} to {end_coords}")

            m = map_renderer.generate_base_map(config)

            route_summary = bus.findPath(start_coords, end=end_coords, walk=0.5)
            if route_summary[0] == "found":
                m = map_renderer.display_busnet_route_on_map(m, route_summary, bus.gStops, start_coords, end_coords)
            else:
                print("⚠ BusNet4 route not found.")

            distances, routes = routing_manager.calculate_distances_and_routes(
                selected_postcode, df_postcodes, dest_df, footRouter, cycleRouter, carRouter
            )

            data_manager.save_route_data(config, dest_type, selected_postcode, distances, routes)

            m = map_renderer.display_routes_on_map(m, routes)
            map_renderer.add_route_legend(m)

            display(m)

    calculate_button.on_click(on_calculate)
    display(postcode_input, destination_selector, calculate_button, map_output)


def run_closest_postcode_to_commercial_view(config):
    """Display only postcodes closest to the selected commercial zones."""
    destination_dropdown = widgets.Dropdown(options=["City Centre", "Shopping Districts"], value="City Centre", description="Area:")
    mode_dropdown = widgets.Dropdown(options=["Walking", "Cycling", "Driving"], value="Walking", description="Mode:")
    run_button = widgets.Button(description="Accept", button_style="success")
    map_output = widgets.Output()

    def update_map(_):
        selected_dest = destination_dropdown.value
        selected_mode = mode_dropdown.value

        df_shopping = data_manager.load_routes_csv(config.r_shopping)
        df_city = data_manager.load_routes_csv(config.r_cityCentre)

        df_shopping = df_shopping[df_shopping["Mode"] == selected_mode]
        df_city = df_city[df_city["Mode"] == selected_mode]

        merged = df_shopping.merge(df_city, on="Start Postcode", suffixes=("_shopping", "_city"))
        closer_shopping = merged[merged["Distance (miles)_shopping"] < merged["Distance (miles)_city"]]
        closer_city = merged[merged["Distance (miles)_city"] < merged["Distance (miles)_shopping"]]

        if selected_dest == "City Centre":
            df = closer_city[["Start Postcode", "Distance (miles)_city", "Route Coordinates_city"]].copy()
            df = df.rename(columns={"Distance (miles)_city": "Distance (miles)", "Route Coordinates_city": "Route Coordinates"})
            df["Target"] = "City Centre"
        else:
            df = closer_shopping[["Start Postcode", "Distance (miles)_shopping", "Route Coordinates_shopping"]].copy()
            df = df.rename(columns={"Distance (miles)_shopping": "Distance (miles)", "Route Coordinates_shopping": "Route Coordinates"})
            df["Target"] = "Shopping District"

        df["Mode"] = selected_mode

        with map_output:
            map_output.clear_output()
            m = map_renderer.generate_base_map(config)
            m = map_renderer.show_closest_routes_only(config, m, df)
            display(m)

    run_button.on_click(update_map)
    display(destination_dropdown, mode_dropdown, run_button, map_output)


def run_closest_zone_red_green_visualization(config):
    """Markers colored by which zone (City Centre or Shopping District) is closer."""
    zone_selector = widgets.Dropdown(options=["City Centre", "Shopping Districts"], value="City Centre", description="Area Type:")
    mode_selector = widgets.Dropdown(options=["Walking", "Cycling", "Driving"], value="Walking", description="Mode:")
    display_button = widgets.Button(description="Display Map", button_style="success")
    map_output = widgets.Output()

    def on_display(_):
        df_city = pd.read_csv(config.r_cityCentre)
        df_shop = pd.read_csv(config.r_shopping)

        with map_output:
            map_output.clear_output()
            m = map_renderer.generate_base_map(config)
            m = map_renderer.add_boundaries(m, config)
            m = map_renderer.add_red_green_closest_zone_markers(m, df_city, df_shop, zone_selector.value, mode_selector.value)
            display(m)

    display_button.on_click(on_display)
    display(zone_selector, mode_selector, display_button, map_output)

# -----------------------------
# BusNet4 utilities
# -----------------------------

from shapely.geometry import Point
import json

def initialise_busnetfour():
    """Setup BusNet4 within the city boundary."""
    j = json.load(open('data/dundee/boundaries/dundee_boundaries.geojson'))
    j = j['features'][0]
    coords = j['geometry']['coordinates'][0]
    dundeeBoundary = [Point(c[1], c[0]) for c in coords]

    bus.setup(
        cache="data/dundee/routes/busnet/dundeeworking",
        validAgency=["Ember", "Stagecoach East Scotland", "Moffat & Williamson", "Xplore Dundee"],
        boundingPoly=dundeeBoundary,
    )

def bus_route_to_boundary(config):
    """Example: draw a route to a fixed city-centre polygon."""
    city_centre = [
        Point(56.45521456343855, -2.975808604),
        Point(56.46084193778188, -2.9768997916807534),
        Point(56.463990223978904, -2.967079106389851),
        Point(56.460239044693814, -2.9604107398342996),
    ]
    start = (56.470206206351286, -2.989496813513388)
    r = bus.findPath(start, walk=0.5, centre=city_centre)
    print(r)

    m = map_renderer.generate_base_map(config)
    m = map_renderer.add_boundaries(m, config)
    m = map_renderer.display_busnet_route_on_map(m, r, bus.gStops, start_coords=start)
    display(m)

def show_route_between_points(start, end, config):
    r = bus.findPath(start, end=end, walk=0.5)
    m = map_renderer.generate_base_map(config)
    m = map_renderer.display_busnet_route_on_map(m, r, bus.gStops, start_coords=start, end_coords=end)
    display(m)

def run_postcode_route_between_selectable_points(config):
    """Pick start/end postcodes; show BusNet4 route between them."""
    if config is None:
        print("error: no city selected.")
        return

    df = data_manager.load_affluence_postcodes(config)
    if df is None or df.empty:
        print("No postcode data available.")
        return

    postcodes = sorted(df["Postcode"].unique())

    start_dropdown = widgets.Dropdown(options=postcodes, description="Start:", layout=widgets.Layout(width="300px"))
    end_dropdown = widgets.Dropdown(options=postcodes, description="End:", layout=widgets.Layout(width="300px"))
    go_button = widgets.Button(description="Show Route", button_style="success")
    map_output = widgets.Output()

    def on_click(_):
        start_pc = start_dropdown.value
        end_pc = end_dropdown.value
        start_coords = data_manager.getLatLonFromPCode(start_pc, df)
        end_coords = data_manager.getLatLonFromPCode(end_pc, df)
        if not start_coords or not end_coords:
            print("One or both postcodes are invalid.")
            return
        with map_output:
            map_output.clear_output()
            print(f"Showing BusNet4 route from {start_pc} → {end_pc}")
            show_route_between_points(start_coords, end_coords, config)

    go_button.on_click(on_click)
    display(widgets.VBox([start_dropdown, end_dropdown, go_button, map_output]))

# -----------------------------
# CCTV
# -----------------------------

def run_cctv_dataset_selector(config):
    """Show dataset selector and return merged CCTV dataframe after users click Accept."""
    result_holder = {}
    ui_manager.display_cctv_dataset_selector(config, result_holder)
    return _MergedCCTVDataLoader(result_holder)

class _MergedCCTVDataLoader:
    """Proxy to delay load until user accepts."""
    def __init__(self, result_holder):
        self.result_holder = result_holder

    def _load_df(self):
        paths = self.result_holder.get("paths", [])
        if not paths:
            print("No datasets selected.")
            return None
        return pd.concat([cctv_manager.load_cctv_data(p) for p in paths], ignore_index=True)

    def __repr__(self):
        return "<CCTVDataProxy: use .data to access merged dataframe>"

    @property
    def data(self):
        return self._load_df()

def run_cctv_analysis(df_proxy):
    """Graphs/controls for CCTV data (delegated to ui_manager)."""
    df = df_proxy.data if hasattr(df_proxy, "data") else df_proxy
    if df is not None:
        ui_manager.display_cctv_controls(df)

def run_cctv_map(df_proxy):
    """
    Display the cameras on a map with Average/Total + date range controls.
    UI + rendering is handled by ui_manager/cctv_manager.
    """
    df = df_proxy.data if hasattr(df_proxy, "data") else df_proxy
    if df is None or df.empty:
        print("No CCTV data loaded.")
        return
    ui_manager.display_cctv_map_controls(df)


def run_cctv_bus_routes(config, cctv_df):
    """
    Displays road routes that pass through the selected CCTV cameras (delegates to cctv_manager).
    """
    car_router = routing_manager.initialize_router("car", config.map_osm_gz, "gz")
    from pythonScripts import BusNet4 as bus
    cctv_manager.show_bus_routes_for_camera(config, bus, bus.gStops, cctv_df, car_router)


# -----------------------------
# Vehicle classification
# -----------------------------

def run_vehicle_dataset_selector(config):
    """Show selector for vehicle classification datasets. Returns a proxy object."""
    result_holder = {}
    ui_manager.display_vehicle_dataset_selector(config, result_holder)
    return _MergedVehicleDataLoader(result_holder)

class _MergedVehicleDataLoader:
    def __init__(self, result_holder):
        self.result_holder = result_holder

    def _load_df(self):
        paths = self.result_holder.get("paths", [])
        if not paths:
            print("No datasets selected.")
            return None
        return pd.concat([cctv_manager.load_vehicle_classification_data(p) for p in paths], ignore_index=True)

    def __repr__(self):
        return "<VehicleDataProxy: use .data to access merged dataframe>"

    @property
    def data(self):
        return self._load_df()

def run_vehicle_analysis(df_proxy):
    df = df_proxy.data if hasattr(df_proxy, "data") else df_proxy
    if df is not None:
        ui_manager.display_vehicle_controls(df)

def run_vehicle_map(df_proxy):
    """
    Show a map of vehicle types by camera with Average/Total + date range controls.
    UI + rendering is handled by ui_manager.
    """
    df = df_proxy.data if hasattr(df_proxy, "data") else df_proxy
    if df is None or df.empty:
        print("No vehicle classification data loaded.")
        return
    ui_manager.display_vehicle_map_controls(df)




# -----------------------------
# Businesses / other
# -----------------------------

def run_business_mapping(config):
    initialise_busnetfour()
    business_manager.load_business_data(config.business_data_path)
    business_manager.display_business_map()

def display_postcode_data(config):
    postcode_map_manager.render_postcode_search_map(config.selected_data_paths, config.boundary_paths)

