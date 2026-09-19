"""
MASA 02_Crypto Tracker App Using Tkinter in Python wtih Source Code
Developer: MASA
"""

import sys
import tkinter as tk
from datetime import datetime
import customtkinter as ctk
import matplotlib.dates as mdates
import pandas as pd
import requests
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Global UI Theme Settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Supported Crypto Configuration Map
CRYPTO_ASSETS = {
    "Bitcoin (BTC)": "bitcoin",
    "Ethereum (ETH)": "ethereum",
    "Solana (SOL)": "solana",
    "Cardano (ADA)": "cardano"
}

TIMEFRAMES = {
    "24 Hours": {"days": "1", "interval": "hourly", "date_fmt": "%H:%M"},
    "7 Days": {"days": "7", "interval": "daily", "date_fmt": "%b %d"},
    "30 Days": {"days": "30", "interval": "daily", "date_fmt": "%b %d"}
}


class AdvancedCryptoDashboard(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Main Window Configuration
        self.title("Crypto Tracker App")
        self.geometry("1000x650")
        self.minsize(950, 600)

        # State Properties
        self.selected_crypto_label = "Bitcoin (BTC)"
        self.selected_timeframe_label = "7 Days"
        self.current_price = 0.0
        self.price_change_24h = 0.0

        # UI Architecture Layout
        self.setup_grid_layout()
        self.create_sidebar_controls()
        self.create_header_panel()
        self.create_chart_panel()

        # Trigger first data ingestion
        self.update_dashboard_data()

    def setup_grid_layout(self):
        """Builds a responsive master grid interface layout."""
        self.grid_columnconfigure(0, weight=0, minsize=220)  # Sidebar
        self.grid_columnconfigure(1, weight=1)              # Main Content Area
        
        self.grid_rowconfigure(0, weight=0)                 # Top Header
        self.grid_rowconfigure(1, weight=1)                 # Core Chart Canvas

    def create_sidebar_controls(self):
        """Creates the asset selection menu and administrative controls."""
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=0, pady=0)
        
        # Branding Header
        brand_label = ctk.CTkLabel(
            self.sidebar, text="CRYPTO TRACKER", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        brand_label.pack(padx=20, pady=(30, 40))

        # Dropdown Label 1: Currency Selection
        crypto_lbl = ctk.CTkLabel(self.sidebar, text="Select Crypto Asset:", font=ctk.CTkFont(size=12, weight="bold"))
        crypto_lbl.pack(anchor="w", padx=20, pady=(10, 2))
        
        self.crypto_dropdown = ctk.CTkOptionMenu(
            self.sidebar, values=list(CRYPTO_ASSETS.keys()), command=self.on_crypto_changed
        )
        self.crypto_dropdown.pack(fill="x", padx=20, pady=(0, 20))

        # Dropdown Label 2: Historical Range
        time_lbl = ctk.CTkLabel(self.sidebar, text="Select Timeframe:", font=ctk.CTkFont(size=12, weight="bold"))
        time_lbl.pack(anchor="w", padx=20, pady=(10, 2))
        
        self.time_dropdown = ctk.CTkOptionMenu(
            self.sidebar, values=list(TIMEFRAMES.keys()), command=self.on_timeframe_changed
        )
        self.time_dropdown.set(self.selected_timeframe_label)
        self.time_dropdown.pack(fill="x", padx=20, pady=(0, 40))

        self.refresh_btn = ctk.CTkButton(
            self.sidebar, text="Force Refresh Data", command=self.update_dashboard_data, fg_color="#2980b9", hover_color="#3498db"
        )
        self.refresh_btn.pack(fill="x", padx=20, pady=10, side="bottom")

    def create_header_panel(self):
        """Creates the header displaying real-time metrics and financial data."""
        self.header_frame = ctk.CTkFrame(self, height=100, corner_radius=8)
        self.header_frame.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="nsew")
        self.header_frame.grid_propagate(False)

        # Asset Labeling
        self.asset_title = ctk.CTkLabel(
            self.header_frame, text=self.selected_crypto_label, font=ctk.CTkFont(size=22, weight="bold")
        )
        self.asset_title.pack(side="left", padx=25, pady=20)

        # Metrics Values Stack
        self.metrics_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.metrics_box.pack(side="right", padx=25, pady=15)

        self.price_display = ctk.CTkLabel(self.metrics_box, text="$0.00", font=ctk.CTkFont(size=26, weight="bold"))
        self.price_display.pack(anchor="e")

        self.change_display = ctk.CTkLabel(self.metrics_box, text="0.00%", font=ctk.CTkFont(size=13, weight="bold"))
        self.change_display.pack(anchor="e", pady=(2, 0))

    def create_chart_panel(self):
        """Initializes the integrated visualization layout."""
        self.chart_frame = ctk.CTkFrame(self, corner_radius=8)
        self.chart_frame.grid(row=1, column=1, padx=20, pady=(10, 20), sticky="nsew")

        # Configure Matplotlib Canvas Space
        self.fig = Figure(figsize=(7, 4), dpi=100, facecolor="#1e1e1e")
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#1e1e1e")
        
        # Format grids and borders
        self.ax.grid(True, color="#333333", linestyle="--", linewidth=0.5)
        for spine in self.ax.spines.values():
            spine.set_color("#333333")
        self.ax.tick_params(colors="#aaaaaa", labelsize=9)

        # Pack component into frame structure
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    # Event Handlers
    def on_crypto_changed(self, choice):
        self.selected_crypto_label = choice
        self.asset_title.configure(text=choice)
        self.update_dashboard_data()

    def on_timeframe_changed(self, choice):
        self.selected_timeframe_label = choice
        self.update_dashboard_data()

    # Core Logic & Network Operations
    def fetch_market_intelligence(self):
        """Pulls structural spot prices and historical intervals with robust error handling."""
        coin_id = CRYPTO_ASSETS[self.selected_crypto_label]
        tf_settings = TIMEFRAMES[self.selected_timeframe_label]

        # Explicit Request Headers to minimize server drops
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }

        try:
            # 1. Ingest Ticker Metrics
            ticker_url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
            res_ticker = requests.get(ticker_url, headers=headers, timeout=10)
            
            if res_ticker.status_code != 200:
                print(f"API Warning: Ticker status returned {res_ticker.status_code}", file=sys.stderr)
                return None
                
            ticker_data = res_ticker.json()
            if coin_id not in ticker_data:
                print(f"API Structure Mismatch: Key '{coin_id}' not found.", file=sys.stderr)
                return None

            self.current_price = ticker_data[coin_id]["usd"]
            self.price_change_24h = ticker_data[coin_id].get("usd_24h_change", 0.0)

            # 2. Ingest Range Vector Data Matrices
            chart_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={tf_settings['days']}"
            if tf_settings['interval'] == "daily":
                chart_url += "&interval=daily"
                
            res_chart = requests.get(chart_url, headers=headers, timeout=10)
            if res_chart.status_code != 200:
                print(f"API Warning: Chart status returned {res_chart.status_code}", file=sys.stderr)
                return None

            chart_data = res_chart.json()
            if "prices" not in chart_data:
                print("API Structure Mismatch: Missing core 'prices' array data.", file=sys.stderr)
                return None
                
            prices_arr = chart_data["prices"]

            # Parse array results into structural Pandas format
            df = pd.DataFrame(prices_arr, columns=["timestamp", "price"])
            df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
            
            # Compress massive high-density index lists on the 24h timeline
            if tf_settings['days'] == "1" and len(df) > 50:
                df = df.iloc[::4].reset_index(drop=True)

            return df

        except Exception as e:
            print(f"Exception handled during remote API integration: {e}", file=sys.stderr)
            return None

    def update_dashboard_data(self):
        """Processes calculations and scales visualization interfaces gracefully."""
        self.refresh_btn.configure(state="disabled", text="Syncing Data...")
        self.update_idletasks()

        df = self.fetch_market_intelligence()

        if df is not None and not df.empty:
            # Format decimals dynamically based on absolute token values
            fmt_str = f"${self.current_price:,.4f}" if self.current_price < 2 else f"${self.current_price:,.2f}"
            self.price_display.configure(text=fmt_str)

            # Color update elements based on positive/negative trends
            if self.price_change_24h >= 0:
                self.change_display.configure(text=f"+{self.price_change_24h:.2f}%", text_color="#2ecc71")
                trend_color = "#2ecc71"
            else:
                self.change_display.configure(text=f"{self.price_change_24h:.2f}%", text_color="#e74c3c")
                trend_color = "#e74c3c"

            # Re-draw the visualization trend line
            self.ax.clear()
            self.ax.set_facecolor("#1e1e1e")
            self.ax.grid(True, color="#333333", linestyle="--", linewidth=0.5)

            self.ax.plot(df["datetime"], df["price"], color=trend_color, linewidth=2)
            self.ax.fill_between(
                df["datetime"], df["price"], df["price"].min() * 0.995, 
                color=trend_color, alpha=0.12
            )

            # Re-apply date styling depending on selection
            date_format = TIMEFRAMES[self.selected_timeframe_label]["date_fmt"]
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
            self.ax.tick_params(colors="#aaaaaa", labelsize=9)
            
            self.fig.tight_layout()
            self.canvas.draw()
        else:
            # Graceful warning if rate limited or connection drops
            self.price_display.configure(text="Sync Delayed")
            self.change_display.configure(text="Rate Limited (120s Auto-Retry)", text_color="#f39c12")

        # Re-enable the interactive data sync controls
        self.refresh_btn.configure(state="normal", text="Force Refresh Data")
        
        # Recurse routine loops every 2 minutes (120000ms) to bypass public rate limitations safely
        self.after(120000, self.update_dashboard_data)


if __name__ == "__main__":
    app = AdvancedCryptoDashboard()
    app.mainloop()