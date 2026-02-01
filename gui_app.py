import customtkinter as ctk
import threading
import time
import win32gui
import sys
from bot_logic import MetinBot

# Setup appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class MetinApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("NeuraBot - AI Farming Assistant")
        self.geometry("900x600")
        
        # Grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Logic Instance
        self.bot = MetinBot(log_callback=self.log_message, status_callback=self.update_status_label, stats_callback=self.update_stats)
        self.bot_thread = None
        self.selected_hwnd = None
        
        # --- UI SETUP ---
        self.create_sidebar()
        self.create_dashboard()
        self.create_console()
        
    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="NEURABOT", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Window Selection
        self.window_label = ctk.CTkLabel(self.sidebar_frame, text="Select Game Window:", anchor="w")
        self.window_label.grid(row=1, column=0, padx=20, pady=(10, 0))
        
        self.window_combo = ctk.CTkComboBox(self.sidebar_frame, values=["Click Refresh"])
        self.window_combo.grid(row=2, column=0, padx=20, pady=(0, 10))
        
        self.refresh_btn = ctk.CTkButton(self.sidebar_frame, text="Refresh Windows", command=self.refresh_windows)
        self.refresh_btn.grid(row=3, column=0, padx=20, pady=5)
        
        # Settings
        self.check_loot = ctk.CTkCheckBox(self.sidebar_frame, text="Auto Loot")
        self.check_loot.select()
        self.check_loot.grid(row=4, column=0, padx=20, pady=10, sticky="n")
        
        self.check_debug = ctk.CTkCheckBox(self.sidebar_frame, text="Debug View")
        self.check_debug.select()
        self.check_debug.grid(row=5, column=0, padx=20, pady=10, sticky="n")

    def create_dashboard(self):
        self.dashboard_frame = ctk.CTkFrame(self, corner_radius=10)
        self.dashboard_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.dashboard_frame.grid_columnconfigure(0, weight=1)
        
        # Status
        self.status_label = ctk.CTkLabel(self.dashboard_frame, text="STATUS: IDLE", font=ctk.CTkFont(size=24, weight="bold"))
        self.status_label.grid(row=0, column=0, padx=20, pady=20)
        
        # Stats
        self.stats_label = ctk.CTkLabel(self.dashboard_frame, text="Stones Destroyed: 0", font=ctk.CTkFont(size=18))
        self.stats_label.grid(row=1, column=0, padx=20, pady=10)
        
        # Start/Stop Button
        self.start_btn = ctk.CTkButton(self.dashboard_frame, text="START BOT", 
                                       font=ctk.CTkFont(size=20, weight="bold"),
                                       height=60, fg_color="green", hover_color="darkgreen",
                                       command=self.toggle_bot)
        self.start_btn.grid(row=2, column=0, padx=50, pady=20, sticky="ew")
        
    def create_console(self):
        self.console_frame = ctk.CTkFrame(self, height=150, corner_radius=0)
        self.console_frame.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="nsew")
        self.console_frame.grid_columnconfigure(0, weight=1)
        self.console_frame.grid_rowconfigure(0, weight=1)
        
        self.log_box = ctk.CTkTextbox(self.console_frame, width=400)
        self.log_box.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.log_box.configure(state="disabled")

    def log_message(self, message):
        
        self.after(0, lambda: self._append_log(message))
    
    def _append_log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def update_status_label(self, message):
         self.after(0, lambda: self.status_label.configure(text=f"STATUS: {message}"))

    def update_stats(self, count):
         self.after(0, lambda: self.stats_label.configure(text=f"Stones Destroyed: {count}"))

    def refresh_windows(self):
        windows = []
        def enum_handler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    # Filter logic (optional, show only metin?)
                    windows.append((title, hwnd))
        win32gui.EnumWindows(enum_handler, None)
        windows.sort(key=lambda x: x[0])
        self.window_titles = [w[0] for w in windows]
        self.window_map = {w[0]: w[1] for w in windows}
        self.window_combo.configure(values=self.window_titles)
        if self.window_titles:
            self.window_combo.set(self.window_titles[0])
            
    def toggle_bot(self):
        if not self.bot.running:
            # Start
            try:
                selected_title = self.window_combo.get()
                hwnd = self.window_map.get(selected_title)
                if not hwnd:
                    self.log_message("Error: No Window Selected.")
                    return
                
                self.selected_hwnd = hwnd
                self.bot_thread = threading.Thread(target=self.bot.run, args=(hwnd, self.check_debug.get() == 1))
                self.bot_thread.start()
                
                self.start_btn.configure(text="STOP BOT", fg_color="red", hover_color="darkred")
                self.window_combo.configure(state="disabled")
                
                # Apply Settings
                self.bot.auto_loot_enabled = (self.check_loot.get() == 1)
                
            except Exception as e:
                self.log_message(f"Start Error: {e}")
        else:
            # Stop
            self.bot.stop()
            self.start_btn.configure(text="START BOT", fg_color="green", hover_color="darkgreen")
            self.status_label.configure(text="STATUS: STOPPING...")
            self.window_combo.configure(state="normal")

if __name__ == "__main__":
    app = MetinApp()
    app.refresh_windows() # Init list
    app.mainloop()
