import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import pytz
import json
import os

SETTINGS_FILE = "clock_prefs.json"

THEMES = {
    "Dark": {"bg": "black", "fg": "#00ffff", "label_fg": "white"},
    "Light": {"bg": "white", "fg": "#007070", "label_fg": "black"},
}
FONTS = ["Segoe UI", "Arial", "Courier New", "Tahoma", "Consolas"]
FAVORITE_CITIES = ["Pacific/Auckland", "America/New_York", "Europe/London"]

SIZE_PRESETS = {
    "Compact": (10, 12),
    "Normal": (12, 16),
    "Large": (16, 20)
}

class WorldClockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌍 Stylish World Clock")
        self.size_mode = tk.StringVar(value="Normal")
        self.layout_mode = tk.StringVar(value="Vertical")
        self.time_format_24h = tk.BooleanVar(value=True)
        self.show_date = tk.BooleanVar(value=False)
        self.theme = tk.StringVar(value="Dark")
        self.font_family = tk.StringVar(value=FONTS[0])
        self.refresh_rate = tk.IntVar(value=1000)  # ms
        self.city_font_size = tk.IntVar(value=SIZE_PRESETS[self.size_mode.get()][0])
        self.time_font_size = tk.IntVar(value=SIZE_PRESETS[self.size_mode.get()][1])
        self.all_cities = sorted(FAVORITE_CITIES + [c for c in pytz.all_timezones if c not in FAVORITE_CITIES])
        self.displayed_cities = FAVORITE_CITIES.copy()
        self.labels = {}
        self.load_preferences()
        self.setup_ui()
        self.refresh_clocks()

    def setup_ui(self):
        self.root.configure(bg=THEMES[self.theme.get()]["bg"])
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        control = ttk.Frame(self.root)
        control.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        for i in range(22):
            control.columnconfigure(i, weight=0)
        control.columnconfigure(0, weight=1)

        self.city_entry = ttk.Combobox(control, values=self.all_cities, width=30)
        self.city_entry.grid(row=0, column=0)
        ttk.Button(control, text="Add City", command=self.add_city).grid(row=0, column=1, padx=3)
        ttk.Button(control, text="Remove City", command=self.remove_city).grid(row=0, column=2, padx=3)
        ttk.Button(control, text="↑", width=2, command=lambda: self.move_city(-1)).grid(row=0, column=3)
        ttk.Button(control, text="↓", width=2, command=lambda: self.move_city(1)).grid(row=0, column=4)

        ttk.Checkbutton(control, text="24h Format", variable=self.time_format_24h, command=self.refresh_clocks).grid(row=0, column=5, padx=4)
        ttk.Checkbutton(control, text="Show Date", variable=self.show_date, command=self.refresh_clocks).grid(row=0, column=6, padx=4)

        # Size mode
        ttk.Label(control, text="Preset Size:").grid(row=0, column=7)
        size_select = ttk.Combobox(control, textvariable=self.size_mode, values=list(SIZE_PRESETS.keys()), width=8)
        size_select.grid(row=0, column=8, padx=2)
        size_select.bind("<<ComboboxSelected>>", self.change_size_mode)

        # Custom font size controls
        ttk.Label(control, text="City Font Size:").grid(row=0, column=9)
        city_font_spin = tk.Spinbox(control, from_=6, to=48, textvariable=self.city_font_size, width=4, command=self.refresh_clocks)
        city_font_spin.grid(row=0, column=10, padx=2)
        ttk.Label(control, text="Time Font Size:").grid(row=0, column=11)
        time_font_spin = tk.Spinbox(control, from_=8, to=64, textvariable=self.time_font_size, width=4, command=self.refresh_clocks)
        time_font_spin.grid(row=0, column=12, padx=2)
        # Also update on manual entry
        city_font_spin.bind("<Return>", lambda e: self.refresh_clocks())
        time_font_spin.bind("<Return>", lambda e: self.refresh_clocks())

        ttk.Label(control, text="Layout:").grid(row=0, column=13)
        layout_select = ttk.Combobox(control, textvariable=self.layout_mode, values=["Vertical", "Horizontal"], width=10)
        layout_select.grid(row=0, column=14, padx=2)
        layout_select.bind("<<ComboboxSelected>>", lambda e: self.refresh_clocks())

        ttk.Label(control, text="Theme:").grid(row=0, column=15)
        theme_select = ttk.Combobox(control, textvariable=self.theme, values=list(THEMES.keys()), width=6)
        theme_select.grid(row=0, column=16, padx=2)
        theme_select.bind("<<ComboboxSelected>>", self.change_theme)

        ttk.Label(control, text="Font:").grid(row=0, column=17)
        font_select = ttk.Combobox(control, textvariable=self.font_family, values=FONTS, width=12)
        font_select.grid(row=0, column=18, padx=2)
        font_select.bind("<<ComboboxSelected>>", lambda e: self.refresh_clocks())

        ttk.Label(control, text="Refresh (ms):").grid(row=0, column=19)
        refresh_entry = ttk.Entry(control, textvariable=self.refresh_rate, width=6)
        refresh_entry.grid(row=0, column=20, padx=2)
        refresh_entry.bind("<Return>", lambda e: self.refresh_clocks())

        ttk.Button(control, text="Save Preferences", command=self.save_preferences).grid(row=0, column=21, padx=3)
        ttk.Button(control, text="Load Preferences", command=self.load_and_refresh).grid(row=0, column=22, padx=3)

        self.clock_frame = tk.Frame(self.root, bg=THEMES[self.theme.get()]["bg"])
        self.clock_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.clock_frame.rowconfigure(0, weight=1)
        self.clock_frame.columnconfigure(0, weight=1)

    def change_size_mode(self, event=None):
        name_size, time_size = SIZE_PRESETS[self.size_mode.get()]
        self.city_font_size.set(name_size)
        self.time_font_size.set(time_size)
        self.refresh_clocks()

    def add_city(self):
        city = self.city_entry.get()
        if city and city in self.all_cities and city not in self.displayed_cities:
            self.displayed_cities.append(city)
            self.refresh_clocks()

    def remove_city(self):
        city = self.city_entry.get()
        if city in self.displayed_cities:
            self.displayed_cities.remove(city)
            self.refresh_clocks()

    def move_city(self, direction):
        city = self.city_entry.get()
        if city in self.displayed_cities:
            idx = self.displayed_cities.index(city)
            new_idx = idx + direction
            if 0 <= new_idx < len(self.displayed_cities):
                self.displayed_cities[idx], self.displayed_cities[new_idx] = \
                    self.displayed_cities[new_idx], self.displayed_cities[idx]
                self.refresh_clocks()

    def refresh_clocks(self):
        for widget in self.clock_frame.winfo_children():
            widget.destroy()
        self.labels = {}

        theme = THEMES[self.theme.get()]
        name_font_size = self.city_font_size.get()
        time_font_size = self.time_font_size.get()
        font_family = self.font_family.get()
        count = len(self.displayed_cities)

        for i in range(max(count, 10)):
            self.clock_frame.rowconfigure(i, weight=0)
            self.clock_frame.columnconfigure(i, weight=0)

        if self.layout_mode.get() == "Vertical":
            self.clock_frame.columnconfigure(0, weight=1)
            total_rows = len(self.displayed_cities)
            row_offset = max((10 - total_rows)//2, 0)
            for i, city in enumerate(self.displayed_cities):
                self.clock_frame.rowconfigure(i+row_offset, weight=1)
                frame = tk.Frame(self.clock_frame, bg=theme["bg"])
                frame.grid(row=i+row_offset, column=0, sticky="ew", pady=3)
                frame.columnconfigure(0, weight=1)
                tk.Label(frame, text=city.split("/")[-1], font=(font_family, name_font_size, "bold"),
                         fg=theme["label_fg"], bg=theme["bg"]).grid(row=0, column=0, sticky="e", padx=5)
                time_label = tk.Label(frame, text="", font=(font_family, time_font_size, "bold"),
                                     fg=theme["fg"], bg=theme["bg"])
                time_label.grid(row=0, column=1, sticky="w", padx=10)
                date_label = tk.Label(frame, text="", font=(font_family, name_font_size),
                                     fg=theme["label_fg"], bg=theme["bg"])
                if self.show_date.get():
                    date_label.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5)
                self.labels[city] = (time_label, date_label)
        else:
            self.clock_frame.rowconfigure(0, weight=1)
            total_cols = len(self.displayed_cities)
            col_offset = max((10 - total_cols)//2, 0)
            for i, city in enumerate(self.displayed_cities):
                self.clock_frame.columnconfigure(i+col_offset, weight=1)
                frame = tk.Frame(self.clock_frame, bg=theme["bg"])
                frame.grid(row=0, column=i+col_offset, sticky="ns", padx=3)
                frame.rowconfigure(0, weight=1)
                tk.Label(frame, text=city.split("/")[-1], font=(font_family, name_font_size, "bold"),
                         fg=theme["label_fg"], bg=theme["bg"]).grid(row=0, column=0, sticky="s", padx=5)
                time_label = tk.Label(frame, text="", font=(font_family, time_font_size, "bold"),
                                     fg=theme["fg"], bg=theme["bg"])
                time_label.grid(row=1, column=0, sticky="n", padx=10)
                date_label = tk.Label(frame, text="", font=(font_family, name_font_size),
                                     fg=theme["label_fg"], bg=theme["bg"])
                if self.show_date.get():
                    date_label.grid(row=2, column=0, sticky="ns", padx=5)
                self.labels[city] = (time_label, date_label)

        self.update_clocks()

    def update_clocks(self):
        fmt = "%H:%M:%S" if self.time_format_24h.get() else "%I:%M:%S %p"
        today_fmt = "%A, %Y-%m-%d"
        for city, (label, date_label) in self.labels.items():
            now = datetime.now(pytz.timezone(city))
            label.config(text=now.strftime(fmt))
            if self.show_date.get():
                date_label.config(text=now.strftime(today_fmt))
            current_color = label.cget("fg")
            theme = THEMES[self.theme.get()]
            alt_fg = "#00eeee" if theme["fg"] == "#00ffff" else "#007080"
            label.config(fg=theme["fg"] if current_color == alt_fg else alt_fg)
        self.root.after(self.refresh_rate.get(), self.update_clocks)

    def change_theme(self, event=None):
        self.root.configure(bg=THEMES[self.theme.get()]["bg"])
        self.clock_frame.config(bg=THEMES[self.theme.get()]["bg"])
        self.refresh_clocks()

    def save_preferences(self):
        data = {
            "cities": self.displayed_cities,
            "size_mode": self.size_mode.get(),
            "layout_mode": self.layout_mode.get(),
            "time_format_24h": self.time_format_24h.get(),
            "show_date": self.show_date.get(),
            "theme": self.theme.get(),
            "font_family": self.font_family.get(),
            "refresh_rate": self.refresh_rate.get(),
            "city_font_size": self.city_font_size.get(),
            "time_font_size": self.time_font_size.get()
        }
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f)
        messagebox.showinfo("Saved", "Preferences saved!")

    def load_preferences(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
            self.displayed_cities = data.get("cities", FAVORITE_CITIES.copy())
            self.size_mode.set(data.get("size_mode", "Normal"))
            self.layout_mode.set(data.get("layout_mode", "Vertical"))
            self.time_format_24h.set(data.get("time_format_24h", True))
            self.show_date.set(data.get("show_date", False))
            self.theme.set(data.get("theme", "Dark"))
            self.font_family.set(data.get("font_family", FONTS[0]))
            self.refresh_rate.set(data.get("refresh_rate", 1000))
            self.city_font_size.set(data.get("city_font_size", SIZE_PRESETS[self.size_mode.get()][0]))
            self.time_font_size.set(data.get("time_font_size", SIZE_PRESETS[self.size_mode.get()][1]))

    def load_and_refresh(self):
        self.load_preferences()
        self.change_theme()
        self.refresh_clocks()

if __name__ == "__main__":
    root = tk.Tk()
    app = WorldClockApp(root)
    root.mainloop()