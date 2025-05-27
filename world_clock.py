import tkinter as tk
from tkinter import ttk, simpledialog
from datetime import datetime
import pytz

class WorldClockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("World Clock")
        self.root.geometry("600x200")
        self.root.resizable(False, False)

        self.all_cities = sorted(pytz.all_timezones)
        self.displayed_cities = ["Pacific/Auckland", "America/New_York", "Europe/London"]
        self.time_format_24h = tk.BooleanVar(value=True)
        self.horizontal_mode = tk.BooleanVar(value=True)

        self.clock_frame = ttk.Frame(self.root)
        self.clock_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.control_frame = ttk.Frame(self.root)
        self.control_frame.pack(fill="x")

        self.city_entry = ttk.Combobox(self.control_frame, values=self.all_cities, width=30)
        self.city_entry.grid(row=0, column=0, padx=5)
        ttk.Button(self.control_frame, text="Add City", command=self.add_city).grid(row=0, column=1, padx=5)
        ttk.Button(self.control_frame, text="Remove City", command=self.remove_city).grid(row=0, column=2, padx=5)
        ttk.Checkbutton(self.control_frame, text="24h Format", variable=self.time_format_24h, command=self.refresh_clocks).grid(row=0, column=3, padx=5)
        ttk.Checkbutton(self.control_frame, text="Horizontal Layout", variable=self.horizontal_mode, command=self.refresh_clocks).grid(row=0, column=4, padx=5)

        self.labels = {}
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

    def refresh_clocks(self):
        for widget in self.clock_frame.winfo_children():
            widget.destroy()
        self.labels = {}

        orientation = "horizontal" if self.horizontal_mode.get() else "vertical"
        for i, city in enumerate(self.displayed_cities):
            row, col = (0, i) if orientation == "horizontal" else (i, 0)
            city_label = ttk.Label(self.clock_frame, text=city.split('/')[-1], font=("Arial", 12, "bold"))
            city_label.grid(row=row * 2, column=col, padx=5, pady=2)
            time_label = ttk.Label(self.clock_frame, text="", font=("Courier", 12))
            time_label.grid(row=row * 2 + 1, column=col, padx=5, pady=2)
            self.labels[city] = time_label

        self.update_clocks()

    def update_clocks(self):
        fmt = "%H:%M:%S" if self.time_format_24h.get() else "%I:%M:%S %p"
        for city, label in self.labels.items():
            now = datetime.now(pytz.timezone(city)).strftime(fmt)
            label.config(text=now)
        self.root.after(1000, self.update_clocks)

if __name__ == "__main__":
    root = tk.Tk()
    app = WorldClockApp(root)
    root.mainloop()