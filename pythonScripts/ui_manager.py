# this file handles displaying ui elements for the cells such as drop down menues and buttons for users to interact with.
import ipywidgets as widgets
from IPython.display import display


from ipywidgets import VBox, RadioButtons, SelectionRangeSlider, Button, Output, Layout
from IPython.display import display
import pandas as pd
import folium
from ipywidgets import VBox, SelectMultiple, RadioButtons, Button, Output, Layout
from IPython.display import display
import matplotlib.pyplot as plt
from pythonScripts.export_saver import save_dataframe_snapshot

def display_boundary_dropdown(config):
    """
    Creates a dropdown UI for selecting a boundary.

    Parameters:
    - config: The city config file.

    Returns:
    - A drop down for boundary selection.
    """
    if config is None:
        print("Error: No city selected.")
        return None

    available_boundaries = {
        attr.replace("b_", "").replace("_", " ").title(): attr
        for attr in dir(config) if attr.startswith("b_")
    }

    if not available_boundaries:
        print("No boundaries found for this city.")
        return None

    default_boundary = next(iter(available_boundaries.values()), None)

    return widgets.Dropdown(
        options=available_boundaries,
        value=default_boundary,
        description="Boundary:",
    )

def display_accept_button():
    """
    Creates an accept button to confirm selection.

    Returns:
    - A button for user confirmation.
    """
    return widgets.Button(description="Accept", button_style="success")

def get_ui_elements(config):
    """
    Groups all UI elements needed for boundary selection.

    Parameters:
    - config: The city config file.

    Returns:
    - A tuple containing (dropdown, accept button).
    """
    boundary_dropdown = display_boundary_dropdown(config)
    accept_button = display_accept_button()

    return boundary_dropdown, accept_button

def display_toggle():
    """
    Creates a toggle switch to enable/disable boundary inclusion.

    Returns:
    - A checkbox object to toggle boundary inclusion.
    """
    return widgets.Checkbox(value=False, description="Include Boundary")
    

def display_ui_for_heatmap(config):
    """
    Builds UI for selecting optional boundaries & heatmap type.

    Parameters:
    - config: The city configuration.

    Returns:
    - A tuple containing the dropdown, toggle, heatmap selection, and accept button.
    """
    boundary_dropdown = display_boundary_dropdown(config)
    toggle = display_toggle()

    heatmap_selector = widgets.Dropdown(
        options={
            "Affluence": "Affluence",
            "Population": "Population",
            "Households": "Households"  
        },
        value="Affluence",
        description="Heatmap Type:",
    )

    accept_button = widgets.Button(description="Apply", button_style="success")

    return boundary_dropdown, toggle, heatmap_selector, accept_button

def show_export_button(df_supplier, *, prefix: str, folder: str = "exports/map_views"):
    """
    Displays a single 'Export CSV' button that saves whatever df_supplier() returns.
    df_supplier should return the view DataFrame (already trimmed to what's shown).
    """
    btn = widgets.Button(description="Export CSV", button_style="info", tooltip="Export displayed data")
    status = widgets.Output()

    def _on_click(_):
        with status:
            status.clear_output()
            try:
                df = df_supplier()
                if df is None or df.empty:
                    print("Nothing to export. Render the map first.")
                    return
                save_dataframe_snapshot(df, prefix=prefix, folder=folder, add_timestamp=True, show_link=True)
            except Exception as e:
                print(f"Failed to export: {e}")

    btn.on_click(_on_click)
    display(widgets.HBox([btn, status]))

#region CCTV
import os
from pythonScripts import cctv_manager
import pandas as pd
import pytz

utc = pytz.UTC



def display_cctv_dataset_selector(config, result_holder):
    """Displays a multi-select UI for CCTV datasets. Stores list of selected paths in result_holder['paths']."""
    folder = getattr(config, "cctv_datasets", None)
    if not folder or not os.path.isdir(folder):
        print("CCTV dataset folder is missing.")
        return

    files = [f for f in os.listdir(folder) if f.endswith(".csv")]
    if not files:
        print("No CSV files found in the folder.")
        return

    selector = widgets.SelectMultiple(
        options=files,
        description="Datasets:",
        layout=widgets.Layout(width="400px", height="200px")
    )
    button = widgets.Button(description="Accept", button_style="success")
    output = widgets.Output()

    def on_click(_):
        output.clear_output()
        selected = list(selector.value)
        if not selected:
            with output:
                print("Please select at least one dataset.")
                return

        full_paths = [os.path.join(folder, f) for f in selected]
        result_holder['paths'] = full_paths
        with output:
            print("Selected:")
            for f in selected:
                print(f" - {f}")

    button.on_click(on_click)
    display(widgets.VBox([selector, button, output]))



def display_cctv_controls(df):
    """Displays controls for visualising CCTV data."""
    cameras = cctv_manager.get_camera_list(df)

    camera_selector = widgets.SelectMultiple(
        options=cameras,
        description='Cameras:',
        layout=widgets.Layout(width='300px', height='300px')
    )

    view_selector = widgets.RadioButtons(
        options=['By Date', 'By Day of Week', 'By Hour of Day'],
        description='View:',
        layout=widgets.Layout(width='300px')
    )

    chart_type_selector = widgets.RadioButtons(
        options=['Line', 'Bar', 'Stacked Bar(use with one camera)'],
        description='Chart Type:',
        layout=widgets.Layout(width='300px')
    )

    traffic_type_selector = widgets.RadioButtons(
        options=[
            ('Combined', 'Combined'),
            ('Road Vehicles', 'F__of_Road_Vehicles'),
            ('People', 'F__of_People'),
            ('Bicycles', 'F__of_Bicycles')
        ],
        description='Traffic:',
        layout=widgets.Layout(width='300px')
    )

    # Generate date range
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    date_list = pd.date_range(min_date, max_date, freq='D').date

    date_range_slider = widgets.SelectionRangeSlider(
        options=list(date_list),
        index=(0, len(date_list) - 1),
        description='Date Range:',
        layout=widgets.Layout(width='600px'),
        format_func=lambda d: d.strftime("%Y-%m-%d")  # 👈 cleaner labels
    )

    button = widgets.Button(description="Show Visualisation", button_style='success')
    output = widgets.Output()

    def on_click(_):
        output.clear_output()
        with output:
            selected_cameras = list(camera_selector.value)
            view = view_selector.value
            chart_type = chart_type_selector.value
            traffic_column = traffic_type_selector.value
            date_min, date_max = date_range_slider.value
            date_min_dt = pd.to_datetime(str(date_min))
            date_max_dt = pd.to_datetime(str(date_max))

            df_filtered = df[(df['Date'] >= date_min_dt) & (df['Date'] <= date_max_dt)]

            if not selected_cameras:
                print("Please select at least one camera, to select more use ctrl or shift keys.")
                return

            if view == 'By Date':
                cctv_manager.plot_by_date(df_filtered, selected_cameras, chart_type, traffic_column)
            elif view == 'By Day of Week':
                cctv_manager.plot_by_day(df_filtered, selected_cameras, chart_type, traffic_column)
            elif view == 'By Hour of Day':
                cctv_manager.plot_by_hour(df_filtered, selected_cameras, chart_type, traffic_column)

    button.on_click(on_click)

    display(widgets.VBox([
        camera_selector,
        view_selector,
        chart_type_selector,
        traffic_type_selector,
        date_range_slider,
        button,
        output
    ]))



def display_cctv_map_controls(df):
    """
    CCTV map controls with DatePickers + Export CSV.
    - Popups show per-camera Bicycles/People/Vehicles (+ Combined).
    - Export saves exactly those columns for the current date range / aggregation.
    """
    if df is None or df.empty:
        print("No CCTV data loaded.")
        return

    # Ensure Date column is datetime
    if "Date" in df.columns:
        df = df.copy()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Build camera list
    try:
        from pythonScripts import cctv_manager  # local import to avoid circulars
        cameras_all = cctv_manager.get_camera_list(df)
    except Exception:
        cameras_all = sorted(df["Source"].dropna().unique().tolist())

    # Default date bounds
    date_min_default = pd.to_datetime(df["Date"].min()) if "Date" in df.columns else None
    date_max_default = pd.to_datetime(df["Date"].max()) if "Date" in df.columns else None

    # Widgets
    camera_select = widgets.SelectMultiple(
        options=cameras_all,
        value=tuple(cameras_all) if cameras_all else (),
        description="Cameras:",
        layout=widgets.Layout(width="350px", height="160px")
    )

    date_from = widgets.DatePicker(
        description="From:",
        value=date_min_default.to_pydatetime().date() if pd.notnull(date_min_default) else None
    )
    date_to = widgets.DatePicker(
        description="To:",
        value=date_max_default.to_pydatetime().date() if pd.notnull(date_max_default) else None
    )

    agg_dropdown = widgets.Dropdown(
        options=[("Average", "mean"), ("Total (sum)", "sum")],
        value="mean",
        description="Aggregation:"
    )

    accept_btn = widgets.Button(description="Show Map", button_style="info")
    export_btn = widgets.Button(description="Export CSV", button_style="success")
    map_output = widgets.Output()
    status_output = widgets.Output()

    # Cache last rendered selection for export
    _latest = {
        "export_df": None,
        "agg": "mean",
        "from": None,
        "to": None
    }

    def _compute_aggregates(df_in, selected_cameras, dt_from, dt_to, agg):
        """Reproduce exactly what the map shows per camera for export, using date-filtered data only."""
        d = df_in.copy()
        if dt_from is not None:
            d = d[d["Date"] >= pd.to_datetime(dt_from)]
        if dt_to is not None:
            d = d[d["Date"] <= pd.to_datetime(dt_to)]

        valid_cams = sorted(d["Source"].dropna().unique().tolist())
        sel = [c for c in (selected_cameras or []) if c in valid_cams]
        if sel:
            d = d[d["Source"].isin(sel)]
        else:
            return pd.DataFrame(columns=["Source", "Latitude", "Longitude", "Bicycles", "People", "Vehicles", "Combined"])

        cols = [c for c in ["F__of_Bicycles", "F__of_People", "F__of_Road_Vehicles"] if c in d.columns]
        if not cols:
            return pd.DataFrame(columns=["Source", "Latitude", "Longitude", "Bicycles", "People", "Vehicles", "Combined"])

        stats = (d.groupby("Source")[cols].sum(numeric_only=True) if agg == "sum"
                 else d.groupby("Source")[cols].mean(numeric_only=True))

        # Coordinates from the same date-filtered frame
        coord_map = (
            d.dropna(subset=["Source"])
             .drop_duplicates(subset=["Source"])
             .set_index("Source")
        )
        # Prefer "Coordinates" (lat,lon) string; fall back to separate columns
        rows = []
        for source, row in stats.iterrows():
            lat = lon = None
            coords_str = None
            if "Coordinates" in coord_map.columns:
                coords_str = coord_map.at[source, "Coordinates"] if source in coord_map.index else None
            if isinstance(coords_str, str) and "," in coords_str:
                try:
                    la, lo = coords_str.split(",", 1)
                    lat, lon = float(la.strip()), float(lo.strip())
                except Exception:
                    pass
            if (lat is None or lon is None):
                lat_col = next((c for c in ["Latitude", "Lat", "latitude", "lat"] if c in coord_map.columns), None)
                lon_col = next((c for c in ["Longitude", "Lon", "lng", "long", "longitude"] if c in coord_map.columns), None)
                if lat_col and lon_col and source in coord_map.index:
                    try:
                        lat = float(coord_map.at[source, lat_col])
                        lon = float(coord_map.at[source, lon_col])
                    except Exception:
                        lat = lon = None

            bicycles = float(row.get("F__of_Bicycles", 0) or 0)
            people   = float(row.get("F__of_People", 0) or 0)
            vehicles = float(row.get("F__of_Road_Vehicles", 0) or 0)
            rows.append({
                "Source": source,
                "Latitude": lat,
                "Longitude": lon,
                "Bicycles": bicycles,
                "People": people,
                "Vehicles": vehicles,
                "Combined": bicycles + people + vehicles
            })

        return pd.DataFrame(rows)

    def on_accept(_):
        selected_cameras = list(camera_select.value) if camera_select.value else cameras_all
        dt_from = date_from.value
        dt_to = date_to.value
        agg = agg_dropdown.value  # "mean" or "sum"

        # Pre-filter for rendering (keeps coordinate keys aligned)
        dsub = df.copy()
        if dt_from is not None:
            dsub = dsub[dsub["Date"] >= pd.to_datetime(dt_from)]
        if dt_to is not None:
            dsub = dsub[dsub["Date"] <= pd.to_datetime(dt_to)]

        valid_after_filter = sorted(dsub["Source"].dropna().unique().tolist())
        selected_valid = [c for c in selected_cameras if c in valid_after_filter]

        with map_output:
            map_output.clear_output()
            if not selected_valid:
                print("No data for the selected range/cameras. Try widening the date range or choosing different cameras.")
            else:
                # Render map using existing function
                from pythonScripts import cctv_manager
                m = cctv_manager.display_cctv_map(
                    df=dsub,  # date-filtered
                    selected_cameras=selected_valid,
                    date_min=None,
                    date_max=None,
                    agg_func=("sum" if agg == "sum" else "mean")
                )
                display(m)

        # Prepare export data mirroring the map's view
        try:
            export_df = _compute_aggregates(df, selected_valid, dt_from, dt_to, agg)
        except Exception as e:
            export_df = None
            with status_output:
                status_output.clear_output()
                print(f"⚠ Failed to prepare export data: {e}")

        _latest["export_df"] = export_df
        _latest["agg"] = agg
        _latest["from"] = dt_from
        _latest["to"] = dt_to

    def on_export(_):
        with status_output:
            status_output.clear_output()
            export_df = _latest.get("export_df", None)
            if export_df is None or export_df.empty:
                print("Nothing to export: click 'Show Map' first.")
                return

            def _fmt(d):
                if d is None:
                    return "all"
                try:
                    return pd.Timestamp(d).strftime("%Y%m%d")
                except Exception:
                    return "all"

            f_from = _fmt(_latest["from"])
            f_to = _fmt(_latest["to"])
            f_agg = "mean" if _latest["agg"] == "mean" else "sum"

            out_df = export_df.copy()
            out_df["Aggregation"] = f_agg
            out_df["Date From"] = f_from
            out_df["Date To"] = f_to

            # Use your saver (shows a clickable link)
            save_dataframe_snapshot(
                out_df,
                prefix=f"cctv_map_{f_agg}_{f_from}-{f_to}",
                folder="exports",
                add_timestamp=True,
                show_link=True,
            )

    accept_btn.on_click(on_accept)
    export_btn.on_click(on_export)

    # Layout
    controls_top = widgets.HBox([
        camera_select,
        widgets.VBox([widgets.HBox([date_from, date_to]), agg_dropdown, widgets.HBox([accept_btn, export_btn])])
    ])
    display(widgets.VBox([controls_top, map_output, status_output]))




#vehicle classification parts
def display_vehicle_dataset_selector(config, result_holder):
    """Multi-select for vehicle classification datasets."""
    

    folder = getattr(config, "cctv_vehicle_classification", None)
    if not folder or not os.path.isdir(folder):
        print("Vehicle dataset folder missing.")
        return

    files = [f for f in os.listdir(folder) if f.endswith(".csv")]
    if not files:
        print("No CSV files found.")
        return

    selector = widgets.SelectMultiple(
        options=files,
        description="Datasets:",
        layout=widgets.Layout(width="400px", height="200px")
    )
    button = widgets.Button(description="Accept", button_style="success")
    output = widgets.Output()

    def on_click(_):
        output.clear_output()
        selected = list(selector.value)
        if not selected:
            print("Please select at least one dataset.")
            return
        full_paths = [os.path.join(folder, f) for f in selected]
        result_holder['paths'] = full_paths
        with output:
            print("Selected:")
            for f in selected:
                print(f" - {f}")

    button.on_click(on_click)
    display(widgets.VBox([selector, button, output]))

def display_vehicle_controls(df):
    from ipywidgets import VBox, SelectMultiple, RadioButtons, SelectionRangeSlider, Button, Output, Layout
    from IPython.display import display
    import matplotlib.pyplot as plt
    import pandas as pd

    cameras = sorted(df['Source'].dropna().unique())
    vehicle_types = sorted(df['Classification_Road_Vehicles'].dropna().unique())

    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    date_list = pd.date_range(min_date, max_date, freq='D').date

    camera_selector = SelectMultiple(
        options=cameras,
        description='Cameras:',
        layout=Layout(width='300px', height='250px')
    )

    vehicle_type_selector = SelectMultiple(
        options=vehicle_types,
        description='Vehicle Types:',
        layout=Layout(width='300px', height='250px')
    )

    chart_type_selector = RadioButtons(
        options=['Line', 'Bar', 'Stacked Bar'],
        description='Chart:',
        layout=Layout(width='300px')
    )

    date_range_slider = SelectionRangeSlider(
        options=list(date_list),
        index=(0, len(date_list) - 1),
        description='Date:',
        layout=Layout(width='600px'),
        format_func=lambda d: d.strftime("%Y-%m-%d")
    )

    button = Button(description="Show Graph", button_style='success')
    output = Output()

    def on_click(_):
        output.clear_output()
        with output:
            selected_cameras = list(camera_selector.value)
            selected_vehicle_types = list(vehicle_type_selector.value)
            chart_type = chart_type_selector.value
            dmin, dmax = date_range_slider.value
            dmin = pd.to_datetime(str(dmin))
            dmax = pd.to_datetime(str(dmax))

            if not selected_cameras or not selected_vehicle_types:
                print("Please select at least one camera and one vehicle type.")
                return

            # Filter by camera, vehicle type, and date
            filtered = df[
                (df['Source'].isin(selected_cameras)) &
                (df['Classification_Road_Vehicles'].isin(selected_vehicle_types)) &
                (df['Date'] >= dmin) & (df['Date'] <= dmax)
            ]

            grouped = filtered.groupby(['Date', 'Classification_Road_Vehicles'])['Number_of_Road_Vehicles'].sum().unstack().fillna(0)
            grouped = grouped[selected_vehicle_types]  # preserve user order

            plt.figure(figsize=(14, 6))
            if chart_type == 'Stacked Bar':
                grouped.plot(kind='bar', stacked=True)
            elif chart_type == 'Bar':
                grouped.plot(kind='bar')
            else:
                grouped.plot()

            plt.title('Vehicle Counts by Type Over Time')
            plt.xlabel('Date')
            plt.ylabel('Number of Vehicles')
            plt.xticks(rotation=45)
            plt.grid(True)
            plt.tight_layout()
            plt.show()

    button.on_click(on_click)

    display(VBox([
        camera_selector,
        vehicle_type_selector,
        chart_type_selector,
        date_range_slider,
        button,
        output
    ]))




def display_vehicle_map_controls(df):
    """
    Vehicle map controls with DatePickers + Export CSV.
    - Popups show per-camera counts for each vehicle class (per aggregation) + Combined.
    - Export saves exactly those columns for the current date range / aggregation.
    """
    if df is None or df.empty:
        print("No vehicle classification data loaded.")
        return

    df = df.copy()
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # UI
    agg_dropdown = RadioButtons(
        options=[('Average', 'mean'), ('Total', 'sum')],
        value='mean',
        description='Summary:',
        layout=Layout(width='280px')
    )

    min_dt = pd.to_datetime(df["Date"].min()) if "Date" in df.columns else None
    max_dt = pd.to_datetime(df["Date"].max()) if "Date" in df.columns else None
    date_from = widgets.DatePicker(description="From:", value=min_dt.date() if pd.notnull(min_dt) else None)
    date_to   = widgets.DatePicker(description="To:",   value=max_dt.date() if pd.notnull(max_dt) else None)

    show_btn   = Button(description="Show Map", button_style='info')
    export_btn = Button(description="Export CSV", button_style='success')
    map_output = Output()
    status_output = Output()

    latest = {"export_df": None, "agg": "mean", "from": None, "to": None}

    def _filter_dates(dfin):
        if "Date" not in dfin.columns:
            return dfin
        d = dfin.copy()
        if date_from.value is not None:
            d = d[d["Date"] >= pd.to_datetime(date_from.value)]
        if date_to.value is not None:
            d = d[d["Date"] <= pd.to_datetime(date_to.value)]
        return d

    def _coords_map(dfin):
        out = {}
        if "Coordinates" in dfin.columns:
            tmp = (dfin.dropna(subset=["Source","Coordinates"])
                       .drop_duplicates(subset=["Source"])
                       .set_index("Source")["Coordinates"])
            for s,v in tmp.items():
                if isinstance(v,str) and "," in v:
                    try:
                        la,lo = v.split(",",1)
                        out[s] = (float(la.strip()), float(lo.strip()))
                    except Exception:
                        pass
        lat_col = next((c for c in ["Latitude","Lat","latitude","lat"] if c in dfin.columns), None)
        lon_col = next((c for c in ["Longitude","Lon","lng","long","longitude"] if c in dfin.columns), None)
        if lat_col and lon_col:
            tmp = (dfin.dropna(subset=["Source",lat_col,lon_col])
                       .drop_duplicates(subset=["Source"])
                       .set_index("Source")[[lat_col,lon_col]])
            for s,row in tmp.iterrows():
                out[s]=(float(row[lat_col]), float(row[lon_col]))
        return out

    def _aggregate_view(dfin, how):
        # long → wide per Source
        needed = {"Source", "Classification_Road_Vehicles", "Number_of_Road_Vehicles"}
        if not needed.issubset(dfin.columns):
            return pd.DataFrame(columns=["Source","Latitude","Longitude","Combined"])

        stats = (dfin.groupby(["Source","Classification_Road_Vehicles"])["Number_of_Road_Vehicles"]
                     .agg(how).unstack().fillna(0))

        cmap = _coords_map(dfin)
        rows = []
        for source, row in stats.iterrows():
            la, lo = cmap.get(source, (None, None))
            rec = {"Source": source, "Latitude": la, "Longitude": lo}
            combined = 0.0
            for klass, val in row.items():
                rec[str(klass)] = float(val)
                combined += float(val)
            rec["Combined"] = combined
            rows.append(rec)

        out = pd.DataFrame(rows)
        if out.empty:
            return out
        class_cols = sorted([c for c in out.columns if c not in {"Source","Latitude","Longitude","Combined"}])
        return out[["Source","Latitude","Longitude"] + class_cols + ["Combined"]]

    def on_show(_):
        how = agg_dropdown.value
        dsub = _filter_dates(df)

        view = _aggregate_view(dsub, how)
        latest["export_df"] = view
        latest["agg"] = how
        latest["from"] = date_from.value
        latest["to"] = date_to.value

        with map_output:
            map_output.clear_output()
            if dsub.empty or view.empty:
                print("No data for the selected date range.")
                return

            # Render folium map similar to your original
            fmap = folium.Map(location=[56.460, -2.97], zoom_start=14)
            for _, r in view.iterrows():
                la, lo = r["Latitude"], r["Longitude"]
                if pd.isna(la) or pd.isna(lo):
                    continue
                lines = [f"<b>{r['Source']}</b>"]
                class_cols = [c for c in view.columns if c not in {"Source","Latitude","Longitude","Combined"}]
                for c in class_cols:
                    lines.append(f"{c}: {r[c]:.2f}")
                lines.append(f"<b>Combined:</b> {r['Combined']:.2f}")

                folium.Marker(
                    location=[la, lo],
                    popup=folium.Popup("<br>".join(lines), max_width=300),
                    tooltip=r["Source"],
                    icon=folium.Icon(color='green', icon='car', prefix='fa')
                ).add_to(fmap)

            display(fmap)

    def _fmt(d):
        if d is None: return "all"
        try: return pd.Timestamp(d).strftime("%Y%m%d")
        except Exception: return "all"

    def on_export(_):
        with status_output:
            status_output.clear_output()
            out = latest["export_df"]
            if out is None or out.empty:
                print("Nothing to export: click 'Show Map' first.")
                return
            out = out.copy()
            out["Aggregation"] = "mean" if latest["agg"] == "mean" else "sum"
            out["Date From"] = _fmt(latest["from"])
            out["Date To"]   = _fmt(latest["to"])
            save_dataframe_snapshot(
                out,
                prefix=f"vehicle_map_{out['Aggregation'].iloc[0]}_{out['Date From'].iloc[0]}-{out['Date To'].iloc[0]}",
                folder="exports",
                add_timestamp=True,
                show_link=True,
            )

    show_btn.on_click(on_show)
    export_btn.on_click(on_export)

    controls = VBox([
        agg_dropdown,
        widgets.HBox([date_from, date_to]),
        widgets.HBox([show_btn, export_btn])
    ])
    display(VBox([controls, map_output, status_output]))


#endregion