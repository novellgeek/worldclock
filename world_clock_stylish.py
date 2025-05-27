import tkinter as tk
from tkinter import ttk
from datetime import datetime
import pytz

class WorldClockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌍 Stylish World Clock")
        self.size_mode = tk.StringVar(value="Normal")
        self.time_format_24h = tk.BooleanVar(value=True)
        self.all_cities = sorted(pytz.all_timezones)
        self.displayed_cities = ["Pacific/Auckland", "America/New_York", "Europe/London"]
        self.labels = {}
        self.font_sizes = {
            "Compact": (10, 12),
            "Normal": (12, 16),
            "Large": (16, 20)
        }

        self.setup_ui()
        self.refresh_clocks()

    def setup_ui(self):
        control = ttk.Frame(self.root)
        control.pack(padx=5, pady=5, fill="x")

        self.city_entry = ttk.Combobox(control, values=self.all_cities, width=30)
        self.city_entry.grid(row=0, column=0)
        ttk.Button(control, text="Add City", command=self.add_city).grid(row=0, column=1, padx=5)
        ttk.Button(control, text="Remove City", command=self.remove_city).grid(row=0, column=2, padx=5)
        ttk.Checkbutton(control, text="24h Format", variable=self.time_format_24h, command=self.refresh_clocks).grid(row=0, column=3)
        ttk.Label(control, text="Size:").grid(row=0, column=4)
        size_select = ttk.Combobox(control, textvariable=self.size_mode, values=["Compact", "Normal", "Large"], width=8)
        size_select.grid(row=0, column=5, padx=5)
        size_select.bind("<<ComboboxSelected>>", lambda e: self.refresh_clocks())

        self.clock_frame = ttk.Frame(self.root)
        self.clock_frame.pack(padx=10, pady=10, fill="both", expand=True)

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

    def refresh_clocks(self):
        for widget in self.clock_frame.winfo_children():
            widget.destroy()
        self.labels = {}

        name_font_size, time_font_size = self.font_sizes[self.size_mode.get()]
        for i, city in enumerate(self.displayed_cities):
            frame = ttk.Frame(self.clock_frame)
            frame.grid(row=i, column=0, sticky="w", pady=3)
            ttk.Label(frame, text=city.split("/")[-1], font=("Segoe UI", name_font_size, "bold")).grid(row=0, column=0, sticky="w", padx=5)
            time_label = tk.Label(frame, text="", font=("Courier", time_font_size, "bold"), fg="#00ffff", bg="black")
            time_label.grid(row=0, column=1, sticky="e", padx=10)
            self.labels[city] = time_label

        self.update_clocks()

    def update_clocks(self):
        fmt = "%H:%M:%S" if self.time_format_24h.get() else "%I:%M:%S %p"
        for city, label in self.labels.items():
            now = datetime.now(pytz.timezone(city)).strftime(fmt)
            label.config(text=now)
            # Animate: alternate fg color slightly (simulated glow)
            current_color = label.cget("fg")
            label.config(fg="#00ffff" if current_color == "#00eeee" else "#00eeee")
        self.root.after(1000, self.update_clocks)

if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg="black")
    app = WorldClockApp(root)
    root.mainloop()