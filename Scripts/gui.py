"""GUI for COVID-19 Data Analysis using Tkinter."""
import os
import sys
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import configparser
from PIL import Image, ImageTk
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

from Library.data_utils import (
    connect_to_database, ensure_columns_exist_in_db, load_all_csvs,
    clean_data, insert_data_into_db, load_data_from_db,
    truncate_covid_data_table
)
from Library.stats import (
    stats_by_country, stats_by_month, stats_by_year, stats_by_date_range,
    filter_data
)
from Library.advanced_metrics import (
    calculate_rates, describe_cases, generate_pivot, compare_wave_intensity
)
from Library.plot_generator import (
    correlation_heatmap, bar_total_cases, line_trend_by_country,
    boxplot_cases_by_month, scatter_deaths_vs_cases
)
from analysis_module import save_report
from Library.data_exporter import export_to_csv

CSV_FOLDER_PATH = "../Data/csse_covid_19_daily_reports/"
CONFIG_PATH = "config.ini"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FONT_FAMILY = FONT_SIZE = SIDEBAR_FONT_FAMILY = SIDEBAR_FONT_SIZE = None
REPORT_BUTTON_COLOR = EXPORT_BUTTON_COLOR = BUTTON_COLOR = None
SIDEBAR_COLOR = BG_COLOR = None


def load_config():
    """Load the interface configuration from the INI file."""
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    if 'interface' not in config:
        config['interface'] = {}
    return config


def save_config(config):
    """Save the interface configuration to the INI file."""
    with open(CONFIG_PATH, 'w', encoding='utf-8') as configfile:
        config.write(configfile)


def apply_config():
    """Apply values from config.ini to global UI settings."""
    global FONT_FAMILY, FONT_SIZE, SIDEBAR_FONT_FAMILY, SIDEBAR_FONT_SIZE
    global REPORT_BUTTON_COLOR, EXPORT_BUTTON_COLOR, BUTTON_COLOR
    global SIDEBAR_COLOR, BG_COLOR

    config = load_config()
    interface = config['interface']

    def safe_get(key, default):
        val = interface.get(key, default)
        return val if val else default

    FONT_FAMILY = safe_get("font_family", "Arial")
    FONT_SIZE = safe_get("font_size", "14")
    SIDEBAR_FONT_FAMILY = safe_get("sidebar_font_family", "Arial")
    SIDEBAR_FONT_SIZE = safe_get("sidebar_font_size", "14")
    REPORT_BUTTON_COLOR = safe_get("report_button_color", "yellow")
    EXPORT_BUTTON_COLOR = safe_get("export_button_color", "green")
    BUTTON_COLOR = safe_get("button_color", "blue")
    SIDEBAR_COLOR = safe_get("sidebar_color", "blue")
    BG_COLOR = safe_get("bg_color", "white")


def _graphics_output_dir():
    """Return the absolute path to the graphics output directory."""
    return os.path.join(os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'Work', 'Graphics'
    )


def data_page(page_frame):
    """Builds the Data & Statistics page with controls and data display."""
    data_page_frame = tk.Frame(page_frame, bg=BG_COLOR)
    data_page_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
    data_page_frame.columnconfigure(0, weight=1)
    data_page_frame.rowconfigure(1, weight=0)
    data_page_frame.rowconfigure(2, weight=1)

    button_frame = tk.Frame(data_page_frame, bg=BG_COLOR)
    button_frame.grid(row=0, column=0, pady=30, padx=20, sticky="ew")
    button_frame.columnconfigure((0, 1, 2, 3, 4), weight=1)

    status_label = tk.Label(
        data_page_frame,
        text="",
        bg=BG_COLOR,
        fg="green",
        font=(FONT_FAMILY, int(FONT_SIZE), "bold")
    )
    status_label.grid(row=1, column=0, pady=10, sticky="ew")

    table_frame = tk.Frame(data_page_frame, bg=BG_COLOR)
    table_frame.grid(row=2, column=0, sticky="nsew", padx=20)

    data_page.tree = None

    def show_table(df):
        for widget in table_frame.winfo_children():
            widget.destroy()
        if df.empty:
            return
        tree = ttk.Treeview(
            table_frame,
            columns=list(df.columns),
            show="headings",
            height=15
        )
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")
        for _, row in df.iterrows():
            tree.insert("", tk.END, values=list(row))
        tree.pack(fill=tk.BOTH, expand=True)
        data_page.tree = tree

    def update_status(text, color):
        status_label.config(text=text, fg=color)
        status_label.update_idletasks()

    def handle_connect_db():
        update_status("🔄 Connecting to database...", "orange")
        try:
            conn = connect_to_database()
            ensure_columns_exist_in_db(conn)
            conn.close()
            update_status("✅ Connected and verified table schema.", "green")
        except Exception as error:
            update_status(f"❌ Failed to connect: {error}", "red")

    def handle_load_data():
        update_status("🔄 Loading data from CSVs...", "orange")
        df = load_all_csvs(CSV_FOLDER_PATH)
        data_page.df = df
        update_status(f"✅ Loaded {len(df)} rows from CSVs.", "green")
        show_table(df)

    def handle_clean_data():
        if not hasattr(data_page, 'df'):
            update_status("⚠️ No data loaded yet.", "red")
            return
        update_status("🧹 Cleaning data...", "orange")
        data_page.df = clean_data(data_page.df)
        update_status(f"✅ Cleaned data. {len(data_page.df)} rows ready.", "green")
        show_table(data_page.df)

    def handle_insert_data():
        if not hasattr(data_page, 'df'):
            update_status("⚠️ No data to insert.", "red")
            return
        update_status("⬆️ Inserting data into the database...", "orange")
        insert_data_into_db(data_page.df)
        update_status("✅ Data inserted into database.", "green")

    def handle_clear_table():
        try:
            truncate_covid_data_table()
            update_status("🗑️ All data cleared from covid_data table.", "blue")
        except Exception as error:
            update_status(f"❌ Failed to clear table: {error}", "red")

    buttons = [
        ("Connect to DB", handle_connect_db),
        ("Load csv Data", handle_load_data),
        ("Clean Data", handle_clean_data),
        ("Insert into DB", handle_insert_data),
        ("Clear Table", handle_clear_table)
    ]

    for i, (text, command) in enumerate(buttons):
        tk.Button(
            button_frame, text=text, command=command, bg=BUTTON_COLOR, fg="white",
            padx=10, pady=5,font=(FONT_FAMILY, int(FONT_SIZE), "bold")
        ).grid(row=0, column=i, padx=5, sticky="ew")


def filtered_data_page(page_frame):
    """Render the filtered data view with load and filter capabilities."""
    def load_data():
        """Load data from the database into the global data_page object."""
        df = load_data_from_db()
        data_page.df = df
        status_label.config(
            text=f"✅ Loaded {len(df)} rows from the database.",
            fg="green"
        )

    def apply_filter():
        """Apply filters and update the table with filtered data."""
        if not hasattr(data_page, 'df'):
            status_label.config(text="⚠️ No data loaded yet.", fg="red")
            return

        filtered_df = filter_data(
            data_page.df, year_var.get(), month_var.get(), country_var.get()
        )

        tree.delete(*tree.get_children())
        tree["columns"] = list(filtered_df.columns)
        tree["show"] = "headings"

        for col in filtered_df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")

        for _, row in filtered_df.iterrows():
            row_values = list(row)
            try:
                # Try parsing the date and reformatting it
                parsed_date = datetime.strptime(str(row_values[1]), "%Y-%m-%d %H:%M:%S")
                row_values[1] = parsed_date.strftime("%m-%d-%Y")
            except Exception:
                pass  # If formatting fails, leave the original value
            tree.insert("", tk.END, values=row_values)

        status_label.config(text=f"✅ Filtered {len(filtered_df)} rows.", fg="green")

    # Setup frames
    filtered_page_frame = tk.Frame(page_frame, bg=BG_COLOR)
    filtered_page_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
    filtered_page_frame.columnconfigure(0, weight=1)
    filtered_page_frame.rowconfigure(2, weight=1)

    filter_frame = tk.Frame(filtered_page_frame, bg=BG_COLOR)
    filter_frame.grid(row=0, column=0, padx=10, sticky="ew")

    # Load button
    load_btn = tk.Button(
        filter_frame, text="Load Data", command=load_data,
        bg=BUTTON_COLOR, fg="white", padx=10, pady=5,
        font=(FONT_FAMILY, int(FONT_SIZE), 'bold')
    )
    load_btn.grid(row=0, column=0, padx=5)

    tk.Label(filter_frame, text="", bg=BG_COLOR).grid(row=0, column=1, padx=5)

    # Filters
    year_var = tk.StringVar()
    month_var = tk.StringVar()
    country_var = tk.StringVar()

    tk.Label(filter_frame, text="Year:", bg=BG_COLOR).grid(row=0, column=2)
    year_menu = ttk.Combobox(
        filter_frame, textvariable=year_var,
        values=["", "2021", "2022", "2023"]
    )
    year_menu.grid(row=0, column=3, padx=5)

    tk.Label(filter_frame, text="Month:", bg=BG_COLOR).grid(row=0, column=4)
    month_menu = ttk.Combobox(
        filter_frame, textvariable=month_var,
        values=[""] + [str(i) for i in range(1, 13)]
    )
    month_menu.grid(row=0, column=5, padx=5)

    tk.Label(filter_frame, text="Country:", bg=BG_COLOR).grid(row=0, column=6)
    country_menu = ttk.Combobox(
        filter_frame, textvariable=country_var,
        values=[
            "", "India", "Brazil", "Russia", "United Kingdom",
            "Egypt", "Italy", "South Africa"
        ]
    )
    country_menu.grid(row=0, column=7, padx=5)

    tk.Label(filter_frame, text="", bg=BG_COLOR).grid(row=0, column=8, padx=5)

    filter_btn = tk.Button(
        filter_frame, text="Apply Filter", command=apply_filter,
        bg=BUTTON_COLOR, fg="white", padx=10, pady=5,
        font=(FONT_FAMILY, int(FONT_SIZE), 'bold')
    )
    filter_btn.grid(row=0, column=9, padx=5)

    status_label = tk.Label(
        filtered_page_frame, text="", bg=BG_COLOR,
        fg="green", font=(FONT_FAMILY, int(FONT_SIZE) - 1)
    )
    status_label.grid(row=1, column=0, sticky="w", padx=10)

    # Table section
    tree_frame = tk.Frame(filtered_page_frame)
    tree_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

    tree_scroll_y = tk.Scrollbar(tree_frame)
    tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    tree_scroll_x = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
    tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

    tree = ttk.Treeview(
        tree_frame,
        yscrollcommand=tree_scroll_y.set,
        xscrollcommand=tree_scroll_x.set
    )
    tree.pack(fill=tk.BOTH, expand=True)

    tree_scroll_y.config(command=tree.yview)
    tree_scroll_x.config(command=tree.xview)


def statistics_page(page_frame):
    """Display the statistics page with filters and result table."""
    stats_frame = tk.Frame(page_frame, bg=BG_COLOR)
    stats_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
    stats_frame.columnconfigure(0, weight=1)
    stats_frame.rowconfigure(2, weight=1)

    filter_frame = tk.Frame(stats_frame, bg=BG_COLOR)
    filter_frame.grid(row=0, column=0, pady=10, padx=10, sticky="ew")

    button_frame = tk.Frame(filter_frame, bg=BG_COLOR)
    button_frame.grid(row=2, column=0, columnspan=4, sticky="w")

    table_frame = tk.Frame(stats_frame)
    table_frame.grid(row=2, column=0, sticky="nsew")

    stats_tree = ttk.Treeview(table_frame, show='headings')
    stats_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                              command=stats_tree.yview)
    stats_tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    status_label = tk.Label(
        stats_frame, text="", bg=BG_COLOR, anchor="w",
        font=(FONT_FAMILY, int(FONT_SIZE) - 1)
    )
    status_label.grid(row=3, column=0, sticky="ew", padx=10, pady=5)

    def load_data():
        df = load_data_from_db()
        data_page.df = df
        status_label.config(text=f"✅ Loaded {len(df)} rows from the database.",
                            fg="green")

    def show_table(df):
        stats_tree.delete(*stats_tree.get_children())
        stats_tree["columns"] = list(df.columns)
        for col in df.columns:
            stats_tree.heading(col, text=col)
            stats_tree.column(col, anchor="center")
        for _, row in df.iterrows():
            stats_tree.insert("", tk.END, values=list(row))

    load_data_btn = tk.Button(
        filter_frame, text="Load Data", command=load_data,
        bg=BUTTON_COLOR, fg="white", padx=10, pady=5,
        font=(FONT_FAMILY, int(FONT_SIZE), 'bold')
    )
    load_data_btn.grid(row=0, column=0, padx=5)

    tk.Label(filter_frame, text="", bg=BG_COLOR).grid(row=0, column=1, padx=5)

    stat_var = tk.StringVar(value="Select Stat")
    stat_menu = ttk.OptionMenu(
        filter_frame, stat_var, "Select Stat",
        "Country Stats", "Rates", "Descriptive", "Pivot",
        "Month Stats", "Year Stats", "Wave Intensity", "Date Range"
    )
    stat_menu.grid(row=0, column=2, padx=5)

    start_label = tk.Label(filter_frame, text="Start Date (YYYY-MM-DD):",
                           bg=BG_COLOR)
    start_entry = tk.Entry(filter_frame, width=15)
    end_label = tk.Label(filter_frame, text="End Date (YYYY-MM-DD):",
                         bg=BG_COLOR)
    end_entry = tk.Entry(filter_frame, width=15)

    def toggle_date_fields(*_):
        if stat_var.get() == "Date Range":
            start_label.grid(row=1, column=0, padx=5, pady=5)
            start_entry.grid(row=1, column=1, padx=5, pady=5)
            end_label.grid(row=1, column=2, padx=5, pady=5)
            end_entry.grid(row=1, column=3, padx=5, pady=5)
        else:
            start_label.grid_forget()
            start_entry.grid_forget()
            end_label.grid_forget()
            end_entry.grid_forget()

    stat_var.trace("w", toggle_date_fields)

    def handle_stat_selection():
        selected = stat_var.get()
        if not hasattr(data_page, 'df'):
            messagebox.showwarning("Data Not Loaded", "Please load data first.")
            return

        df = data_page.df
        title, desc = "", ""
        stats, fname, rname = None, "", ""

        try:
            if selected == "Country Stats":
                stats = stats_by_country(df)
                fname = "stats_by_country.csv"
                rname = "stats_by_country.txt"
                title, desc = "Stats by Country", "Cumulative numbers."
            elif selected == "Rates":
                stats = calculate_rates(df)
                fname = "fatality_recovery_rates.csv"
                rname = "fatality_recovery_rates.txt"
                title, desc = "Rates", "Fatality & Recovery Rates."
            elif selected == "Descriptive":
                stats = describe_cases(df)
                fname = "descriptive_statistics.csv"
                rname = "descriptive_statistics.txt"
                title, desc = "Descriptive", "Statistical summary."
            elif selected == "Pivot":
                stats = generate_pivot(df)
                fname = "pivot_cases_by_year.csv"
                rname = "pivot_cases_by_year.txt"
                title, desc = "Pivot", "Confirmed Cases by Year."
            elif selected == "Month Stats":
                stats = stats_by_month(df)
                fname = "stats_by_month.csv"
                rname = "stats_by_month.txt"
                title, desc = "Monthly", "Monthly statistics."
            elif selected == "Year Stats":
                stats = stats_by_year(df)
                fname = "stats_by_year.csv"
                rname = "stats_by_year.txt"
                title, desc = "Yearly", "Yearly statistics."
            elif selected == "Wave Intensity":
                stats = compare_wave_intensity(df)
                fname = "wave_intensity_comparison.csv"
                rname = "wave_intensity_comparison.txt"
                title, desc = "Wave Intensity", "Wave intensity comparison."
            elif selected == "Date Range":
                try:
                    start = datetime.strptime(start_entry.get(), "%Y-%m-%d").date()
                    end = datetime.strptime(end_entry.get(), "%Y-%m-%d").date()
                except ValueError:
                    messagebox.showerror("Invalid Date Format", "Please enter valid dates in YYYY-MM-DD format.")
                    return

                if end <= start:
                    messagebox.showerror("Invalid Date Range", "End date must be after start date.")
                    return

                stats = stats_by_date_range(df, start, end)
                fname = "stats_by_date_range.csv"
                rname = f"stats_by_range_{start}_to_{end}.txt"
                title = f"Date Range {start} to {end}"
                desc = "Filtered analysis."

        except Exception as e:
            messagebox.showerror("Error", f"Something went wrong:\n{e}")

        show_table(stats)
        status_label.config(text=f"📊 {selected} generated: {len(stats)} rows.",
                            fg="green")

        for widget in button_frame.winfo_children():
            widget.destroy()

        def export_stat():
            export_to_csv(stats, fname, BASE_DIR)
            status_label.config(text=f"✅ Exported {selected} to {fname}.",
                                fg="green")

        def generate_report():
            save_report(stats, rname, BASE_DIR, title, desc)
            status_label.config(text=f"✅ Report for {selected} saved.",
                                fg="green")

        export_btn = tk.Button(
            button_frame, text="Export", command=export_stat,
            bg=EXPORT_BUTTON_COLOR, bd=0, fg="white", padx=10, pady=5,
            font=(FONT_FAMILY, int(FONT_SIZE), 'bold')
        )
        export_btn.pack(side="left", padx=5, pady=5)

        report_btn = tk.Button(
            button_frame, text="Generate Report", command=generate_report,
            bg=REPORT_BUTTON_COLOR, bd=0, fg="white", padx=10, pady=5,
            font=(FONT_FAMILY, int(FONT_SIZE), 'bold')
        )
        report_btn.pack(side="left", padx=5, pady=5)

    gen_btn = tk.Button(
        filter_frame, text="Generate", command=handle_stat_selection,
        bg=BUTTON_COLOR, fg="white", padx=10, pady=5,
        font=(FONT_FAMILY, int(FONT_SIZE), 'bold')
    )
    gen_btn.grid(row=0, column=10, padx=5)


def visualization_page(page_frame):
    """Render the visualization page where users can load data and generate plots."""
    visualization_page_frame = tk.Frame(page_frame, bg=BG_COLOR)
    visualization_page_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
    visualization_page_frame.columnconfigure(0, weight=1)
    visualization_page_frame.rowconfigure(1, weight=1)

    filter_frame = tk.Frame(visualization_page_frame, bg=BG_COLOR)
    filter_frame.grid(row=0, column=0, pady=10, padx=10, sticky="ew")

    status_label = tk.Label(
        visualization_page_frame,
        text="",
        bg=BG_COLOR,
        fg="green",
        font=(FONT_FAMILY, int(FONT_SIZE))
    )
    status_label.grid(row=1, column=0, pady=10, sticky="w")

    visualization_page.img_label = None

    def load_data():
        df = load_data_from_db()
        visualization_page.df = df
        status_label.config(text=f"✅ Loaded {len(df)} rows from the database.")

    load_data_button = tk.Button(
        filter_frame,
        text="Load Data",
        command=load_data,
        bg=BUTTON_COLOR,
        fg="white",
        padx=10,
        pady=5,
        font=(FONT_FAMILY, int(FONT_SIZE), 'bold')
    )
    load_data_button.grid(row=0, column=0, padx=5)

    plot_var = tk.StringVar()
    plot_var.set("Select Plot")
    plot_menu = ttk.OptionMenu(
        filter_frame,
        plot_var,
        "Select Plot",
        "Correlation Heatmap",
        "Bar Chart: Total Cases by Country",
        "Line Trend by Country",
        "Boxplot by Month",
        "Scatter: Deaths vs Cases"
    )
    plot_menu.grid(row=0, column=1, padx=5)

    def handle_plot_selection():
        selected_plot = plot_var.get()

        if not hasattr(visualization_page, 'df'):
            messagebox.showwarning("Data Not Loaded", "Please load data first.")
            return

        # Generate the selected plot
        if selected_plot == "Correlation Heatmap":
            correlation_heatmap(visualization_page.df, BASE_DIR)
            plot_filename = "correlation_heatmap.png"
        elif selected_plot == "Bar Chart: Total Cases by Country":
            bar_total_cases(visualization_page.df, BASE_DIR)
            plot_filename = "bar_total_cases.png"
        elif selected_plot == "Line Trend by Country":
            line_trend_by_country(visualization_page.df, BASE_DIR)
            plot_filename = "line_trend_by_country.png"
        elif selected_plot == "Boxplot by Month":
            boxplot_cases_by_month(visualization_page.df, BASE_DIR)
            plot_filename = "boxplot_cases_by_month.png"
        elif selected_plot == "Scatter: Deaths vs Cases":
            scatter_deaths_vs_cases(visualization_page.df, BASE_DIR)
            plot_filename = "scatter_deaths_vs_cases.png"
        else:
            messagebox.showwarning("Invalid Plot", "Please select a valid plot.")
            return

        plot_path = os.path.join(_graphics_output_dir(), plot_filename)
        status_label.config(text=f"✅ Plot saved as {plot_filename}")

        if os.path.exists(plot_path):
            try:
                pil_image = Image.open(plot_path)
                pil_image.thumbnail((800, 500), Image.Resampling.LANCZOS)
                img = ImageTk.PhotoImage(pil_image)

                if visualization_page.img_label:
                    visualization_page.img_label.configure(image=img)
                    visualization_page.img_label.image = img
                else:
                    visualization_page.img_label = tk.Label(
                        visualization_page_frame, image=img
                    )
                    visualization_page.img_label.image = img
                    visualization_page.img_label.grid(row=2, column=0, pady=10)
            except Exception as e:
                messagebox.showerror("Image Error", f"Error displaying image: {e}")
        else:
            messagebox.showwarning("File Not Found", "Plot image could not be found.")

    generate_button = tk.Button(
        filter_frame,
        text="Generate Plot",
        command=handle_plot_selection,
        bg=BUTTON_COLOR,
        fg="white",
        padx=10,
        pady=5,
        font=(FONT_FAMILY, int(FONT_SIZE), 'bold')
    )
    generate_button.grid(row=0, column=2, padx=5)


def configuration_page(page_frame):
    """Render the configuration page for adjusting interface preferences."""
    configuration_page_frame = tk.Frame(page_frame, bg=BG_COLOR)
    configuration_page_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)

    config = load_config()
    interface = config['interface']

    fonts = ["Arial", "Calibri", "Times New Roman", "Verdana", "Courier New"]
    colors = ["blue", "red", "cyan", "yellow", "green", "pink", "purple"]
    font_sizes = ["12", "13", "14", "15", "16"]
    bg_color_choices = {
        "White": "white",
        "Beige": "beige",
        "Light Beige": "#f5f5dc",
        "Light Lavender": "#e6e6fa",
        "Powder Blue": "#b0e0e6",
        "Alice Blue": "#f0f8ff",
        "Honeydew": "#f0fff0",
        "Seashell": "#fff5ee",
        "Light Cyan": "#e0ffff",
        "Misty Rose": "#ffe4e1"
    }

    entries = {}
    row = 0
    col = 0

    def add_field(label_text, key, options=None, default="", is_dropdown=True):
        nonlocal row, col
        label = tk.Label(
            configuration_page_frame,
            text=label_text,
            bg=BG_COLOR,
            anchor="w"
        )
        label.grid(row=row, column=col, sticky="w", padx=(10, 5), pady=8)

        if key == "bg_color":
            hex_value = interface.get(key, default)
            name_value = next(
                (name for name, code in bg_color_choices.items() if code == hex_value),
                default
            )
            var = tk.StringVar(value=name_value)
        else:
            var = tk.StringVar(value=interface.get(key, default))

        if options:
            widget = ttk.Combobox(
                configuration_page_frame,
                textvariable=var,
                values=options,
                state="readonly"
            )
        else:
            widget = ttk.Entry(configuration_page_frame, textvariable=var)

        widget.grid(row=row, column=col + 1, sticky="ew", padx=(5, 20), pady=8)
        entries[key] = var

        col += 2
        if col >= 6:
            row += 1
            col = 0

    # Add all fields
    add_field("Font Family", "font_family", fonts, "Arial")
    add_field("Font Size", "font_size", font_sizes, "14")
    add_field("Sidebar Font Family", "sidebar_font_family", fonts, "Arial")
    add_field("Sidebar Font Size", "sidebar_font_size", font_sizes, "14")
    add_field("Report Button Color", "report_button_color", colors, "yellow")
    add_field("Export Button Color", "export_button_color", colors, "green")
    add_field("Button Color", "button_color", colors, "blue")
    add_field("Sidebar Color", "sidebar_color", colors, "blue")
    add_field("Background Color", "bg_color", list(bg_color_choices.keys()), "White")

    def on_save():
        for key, var in entries.items():
            value = var.get()
            if key == "bg_color":
                interface[key] = bg_color_choices.get(value, value)
            else:
                interface[key] = value

        save_config(config)

        messagebox.showinfo(
            "Restart Required",
            "Configuration saved. The application will now restart."
        )

        python = sys.executable
        os.execl(python, python, *sys.argv)

    save_btn = tk.Button(
        configuration_page_frame,
        text="Save Configuration",
        command=on_save,
        bg=BUTTON_COLOR,
        fg="white",
        padx=10,
        pady=5,
        font=(FONT_FAMILY, int(FONT_SIZE), 'bold')
    )
    save_btn.grid(row=row + 1, column=0, columnspan=6, pady=(25, 0))

    for c in range(6):
        configuration_page_frame.columnconfigure(c, weight=1, minsize=100)


def launch_gui():
    """Launch the Graphical User Interface"""
    apply_config()
    root = tk.Tk()
    root.geometry('900x600')
    root.title('Tkinter Covid-19 Analysis')

    # Sidebar icons
    toggle_icon = tk.PhotoImage(file='images/open_menu.png')
    close_icon = tk.PhotoImage(file='images/close_menu.png')
    data_icon = tk.PhotoImage(file='images/data.png')
    filter_icon = tk.PhotoImage(file='images/data_filtering.png')
    statistics_icon = tk.PhotoImage(file='images/statistics.png')
    visualization_icon = tk.PhotoImage(file='images/visualization.png')
    configuration_icon = tk.PhotoImage(file='images/configuration.png')


    def switcher(ind, page, pg):
        """Switch between sidebar buttons and load respective page."""
        data_button_ind.config(bg=SIDEBAR_COLOR)
        filter_button_ind.config(bg=SIDEBAR_COLOR)
        statistics_button_ind.config(bg=SIDEBAR_COLOR)
        visualization_button_ind.config(bg=SIDEBAR_COLOR)
        configuration_button_ind.config(bg=SIDEBAR_COLOR)
        ind.config(bg='white')
        if menu_sidebar_frame.winfo_width() > 50:
            shrink_menu_sidebar()

        for frame in page_frame.winfo_children():
            frame.destroy()

        page(pg)


    def expand_menu():
        """Animate expanding the sidebar."""
        current_width = menu_sidebar_frame.winfo_width()
        if current_width != 250:
            current_width += 10
            menu_sidebar_frame.config(width=current_width)
            root.after(ms=10, func=expand_menu)


    def expand_menu_sidebar():
        """Trigger sidebar expansion."""
        expand_menu()
        toggle_button.config(image=close_icon)
        toggle_button.config(command=shrink_menu_sidebar)


    def shrink_menu():
        """Animate shrinking the sidebar."""
        current_width = menu_sidebar_frame.winfo_width()
        if current_width != 50:
            current_width -= 10
            menu_sidebar_frame.config(width=current_width)
            root.after(ms=12, func=shrink_menu)


    def shrink_menu_sidebar():
        """Trigger sidebar shrinking."""
        shrink_menu()
        toggle_button.config(image=toggle_icon)
        toggle_button.config(command=expand_menu_sidebar)


    # frames
    page_frame = tk.Frame(root, bg=BG_COLOR)
    page_frame.place(relwidth=1.0, relheight=1.0, x=30)
    data_page(page_frame)

    menu_sidebar_frame = tk.Frame(root, bg=SIDEBAR_COLOR)

    # buttons
    toggle_button = tk.Button(
        menu_sidebar_frame, image=toggle_icon, bg=SIDEBAR_COLOR, bd=0,
        activebackground=SIDEBAR_COLOR, command=lambda: expand_menu_sidebar()
    )
    toggle_button.place(x=5, y=10, width=40, height=40)

    data_button = tk.Button(
        menu_sidebar_frame, image=data_icon, bg=SIDEBAR_COLOR, bd=0,
        activebackground=SIDEBAR_COLOR,
        command=lambda: switcher(ind=data_button_ind, page=data_page,
                                 pg=page_frame)
    )
    data_button.place(x=5, y=140, width=40, height=40)

    data_button_ind = tk.Label(menu_sidebar_frame, bg='white')
    data_button_ind.place(x=2, y=140, width=3, height=40)

    data_button_title = tk.Label(
        menu_sidebar_frame, text='Loading/Preprocess', bg=SIDEBAR_COLOR, fg='white',
        font=(SIDEBAR_FONT_FAMILY, int(SIDEBAR_FONT_SIZE), 'bold'), anchor=tk.W
    )
    data_button_title.place(x=50, y=140, width=180, height=40)
    data_button_title.bind('<Button-1>', lambda e: switcher(ind=data_button_ind,
                                                            page=data_page,
                                                            pg=page_frame)
                           )

    filter_button = tk.Button(
        menu_sidebar_frame, image=filter_icon, bg=SIDEBAR_COLOR, bd=0,
        activebackground=SIDEBAR_COLOR,
        command=lambda: switcher(ind=filter_button_ind,
                                 page=filtered_data_page,
                                 pg=page_frame)
    )
    filter_button.place(x=5, y=200, width=40, height=40)

    filter_button_ind = tk.Label(menu_sidebar_frame, bg=SIDEBAR_COLOR)
    filter_button_ind.place(x=2, y=200, width=3, height=40)

    filter_button_title = tk.Label(
        menu_sidebar_frame, text='Data Filtering', bg=SIDEBAR_COLOR, fg='white',
        font=(SIDEBAR_FONT_FAMILY, int(SIDEBAR_FONT_SIZE), 'bold'), anchor=tk.W
    )
    filter_button_title.place(x=50, y=200, width=180, height=40)
    filter_button_title.bind('<Button-1>',
                             lambda e: switcher(ind=filter_button_ind,
                                                page=filtered_data_page,
                                                pg=page_frame))

    statistics_button = tk.Button(
        menu_sidebar_frame, image=statistics_icon, bg=SIDEBAR_COLOR, bd=0,
        activebackground=SIDEBAR_COLOR,
        command=lambda: switcher(ind=statistics_button_ind,
                                 page=statistics_page,
                                 pg=page_frame)
    )
    statistics_button.place(x=5, y=260, width=40, height=40)

    statistics_button_ind = tk.Label(menu_sidebar_frame, bg=SIDEBAR_COLOR)
    statistics_button_ind.place(x=2, y=260, width=3, height=40)

    statistics_button_title = tk.Label(
        menu_sidebar_frame, text='Statistics', bg=SIDEBAR_COLOR, fg='white',
        font=(SIDEBAR_FONT_FAMILY, int(SIDEBAR_FONT_SIZE), 'bold'), anchor=tk.W
    )
    statistics_button_title.place(x=50, y=260, width=180, height=40)
    statistics_button_title.bind('<Button-1>',
                                 lambda e: switcher(ind=statistics_button_ind,
                                                    page=statistics_page,
                                                    pg=page_frame)
                                 )

    visualization_button = tk.Button(
        menu_sidebar_frame, image=visualization_icon, bg=SIDEBAR_COLOR, bd=0,
        activebackground=SIDEBAR_COLOR,
        command=lambda: switcher(ind=visualization_button_ind,
                                 page=visualization_page,
                                 pg=page_frame)
    )
    visualization_button.place(x=5, y=320, width=40, height=40)

    visualization_button_ind = tk.Label(menu_sidebar_frame, bg=SIDEBAR_COLOR)
    visualization_button_ind.place(x=2, y=320, width=3, height=40)

    visualization_button_title = tk.Label(
        menu_sidebar_frame, text='Visualizations', bg=SIDEBAR_COLOR, fg='white',
        font=(SIDEBAR_FONT_FAMILY, int(SIDEBAR_FONT_SIZE), 'bold'), anchor=tk.W
    )
    visualization_button_title.place(x=50, y=320, width=180, height=40)
    visualization_button_title.bind(
        '<Button-1>', lambda e: switcher(ind=visualization_button_ind,
                                         page=visualization_page,
                                         pg=page_frame)
    )

    configuration_button = tk.Button(
        menu_sidebar_frame, image=configuration_icon, bg=SIDEBAR_COLOR, bd=0,
        activebackground=SIDEBAR_COLOR,
        command=lambda: switcher(ind=configuration_button_ind,
                                 page=configuration_page,
                                 pg=page_frame)
    )
    configuration_button.place(x=5, y=380, width=40, height=40)

    configuration_button_ind = tk.Label(menu_sidebar_frame, bg=SIDEBAR_COLOR)
    configuration_button_ind.place(x=2, y=380, width=3, height=40)

    configuration_button_title = tk.Label(
        menu_sidebar_frame, text='Configuration', bg=SIDEBAR_COLOR, fg='white',
        font=(SIDEBAR_FONT_FAMILY, int(SIDEBAR_FONT_SIZE), 'bold'), anchor=tk.W
    )
    configuration_button_title.place(x=50, y=380, width=180, height=40)
    configuration_button_title.bind(
        '<Button-1>', lambda e: switcher(ind=configuration_button_ind,
                                         page=configuration_page,
                                         pg=page_frame)
    )

    menu_sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=3)
    menu_sidebar_frame.pack_propagate(flag=False)
    menu_sidebar_frame.configure(width=50)

    try:
        root.mainloop()
    except Exception:
        pass
