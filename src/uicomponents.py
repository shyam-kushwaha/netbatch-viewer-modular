"""
UI Components - Window setup and widget creation
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import sys
import logging
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, List, Any

logger = logging.getLogger(__name__)



class UIComponentsMixin:
    """Mixin class for UI component creation and setup"""
    def setup_window(self):
        """Configure the main window."""
        self.root.title("Netbatch Status Viewer")
        self.root.geometry("1400x900")
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 10, 'bold'))
        style.configure('Treeview', font=('Arial', 11), rowheight=25)
        style.configure('Treeview.Heading', font=('Arial', 11, 'bold'))
        # Configure grid - only main area (row 1) should expand
        self.root.grid_rowconfigure(0, weight=0)  # Toolbar - fixed height
        self.root.grid_rowconfigure(1, weight=1)  # Main area - expandable
        self.root.grid_rowconfigure(2, weight=0)  # Status bar - fixed height
        self.root.grid_columnconfigure(0, weight=1)

    def create_menu(self):
        """Create the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load XML File...", command=self.load_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Refresh Data", command=self.refresh_view, accelerator="Ctrl+L")
        file_menu.add_separator()
        file_menu.add_command(label="Export to CSV...", command=self.export_to_csv, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh", command=self.refresh_view, accelerator="F5")
        view_menu.add_command(label="Clear Filters", command=self.clear_filters, accelerator="Ctrl+L")
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        # Bind keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.load_file())
        self.root.bind('<Control-l>', lambda e: self.refresh_view())
        self.root.bind('<Control-e>', lambda e: self.export_to_csv())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Control-r>', lambda e: self.clear_filters())
        self.root.bind('<F5>', lambda e: self.refresh_view())

    def create_toolbar(self):
        """Create the toolbar with action buttons."""
        toolbar = ttk.Frame(self.root, relief=tk.RAISED, borderwidth=1)
        toolbar.grid(row=0, column=0, sticky='ew', padx=0, pady=0)
        # Refresh button
        ttk.Button(toolbar, text="Refresh", command=self.refresh_view, width=8).pack(side=tk.LEFT, padx=2)
        # Auto-refresh dropdown
        ttk.Label(toolbar, text="Auto-refresh:", font=('Arial', 11)).pack(side=tk.LEFT, padx=(10, 2))
        refresh_options = ['Off', '10s', '30s', '1m', '5m', '10m', '30m']
        self.refresh_combo = ttk.Combobox(toolbar, textvariable=self.refresh_interval, 
                                         values=refresh_options, state='readonly', width=8, font=('Arial', 11))
        self.refresh_combo.pack(side=tk.LEFT, padx=2)
        self.refresh_combo.bind('<<ComboboxSelected>>', self.on_refresh_interval_changed)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=3)
        # Filter controls - more compact
        ttk.Label(toolbar, text="Feeder:", font=('Arial', 12)).pack(side=tk.LEFT, padx=(2, 1))
        self.feeder_combo = ttk.Combobox(toolbar, textvariable=self.filters['feeder'], 
                                         width=25, state='readonly', font=('Arial', 12))
        self.feeder_combo.pack(side=tk.LEFT, padx=2)
        self.feeder_combo.bind('<<ComboboxSelected>>', lambda e: self.on_feeder_changed())
        ttk.Label(toolbar, text="Config:", font=('Arial', 12)).pack(side=tk.LEFT, padx=(2, 1))
        self.config_combo = ttk.Combobox(toolbar, textvariable=self.filters['config'], 
                                         width=40, state='readonly', font=('Arial', 12))
        self.config_combo.pack(side=tk.LEFT, padx=2)
        self.config_combo.bind('<<ComboboxSelected>>', lambda e: self.on_config_changed())
        ttk.Label(toolbar, text="Block:", font=('Arial', 12)).pack(side=tk.LEFT, padx=(2, 1))
        self.block_combo = ttk.Combobox(toolbar, textvariable=self.filters['block'], 
                                         width=20, state='readonly', font=('Arial', 12))
        self.block_combo.pack(side=tk.LEFT, padx=2)
        self.block_combo.bind('<<ComboboxSelected>>', lambda e: self.on_block_changed())
        ttk.Label(toolbar, text="Status:", font=('Arial', 12)).pack(side=tk.LEFT, padx=(2, 1))
        self.status_combo = ttk.Combobox(toolbar, textvariable=self.filters['status'], 
                                         width=20, state='readonly', font=('Arial', 12))
        self.status_combo.pack(side=tk.LEFT, padx=2)
        self.status_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=3)
        # Search - more compact
        ttk.Label(toolbar, text="Search:", font=('Arial', 12)).pack(side=tk.LEFT, padx=(2, 1))
        search_entry = ttk.Entry(toolbar, textvariable=self.filters['search'], width=18, font=('Arial', 12))
        search_entry.pack(side=tk.LEFT, padx=2)
        self.filters['search'].trace('w', lambda *args: self.apply_filters())
        # Jobs only checkbox
        ttk.Checkbutton(toolbar, text="Jobs Only", 
                       variable=self.filters['jobs_only'],
                       command=self.apply_filters).pack(side=tk.LEFT, padx=5)

        # Clear filters button
        ttk.Button(toolbar, text="Clear", command=self.clear_filters, width=8).pack(side=tk.LEFT, padx=10)

    def create_main_area(self):
        """Create the main content area with notebook tabs."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=1, column=0, sticky='nsew', padx=0, pady=0)
        self.create_tasks_tab()


    def create_status_bar(self):
        """Create status bar at bottom of window."""
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=2, column=0, sticky='ew', padx=2, pady=2)


    def create_tasks_tab(self):
        """Create the tasks table tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Tasks Table")
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        columns = ('TaskID', 'TaskName', 'Config', 'Block', 'Design', 'Stage', 
                  'Status', 'Duration', 'Started', 'NBClass', 'NBQSlot', 'WorkAreaPercentUsed')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        column_widths = {
            'TaskID': 20, 'TaskName': 220, 'Config': 150, 'Block': 80, 'Design': 80,
            'Stage': 80, 'Status': 80, 'Duration': 80, 'Started': 80,
            'NBClass': 80, 'NBQSlot': 80, 'WorkAreaPercentUsed': 10
        }
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c))
            self.tree.column(col, width=column_widths.get(col, 100))
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Double-click to show task details
        self.tree.bind('<Double-Button-1>', self.show_task_details)
        # Comprehensive status color scheme
        self.status_colors = {
            "Completed": "#4CAF50",            # Green
            "Completed (failures)": "#FF9800", # Orange  
            "Canceled/Stopped": "#F44336",     # Red
            "Running": "#2196F3",              # Blue
            "Skipped": "#9C27B0",              # Purple
            "Not Running": "#9E9E9E",          # Gray
            "Loaded": "#FFEB3B",               # Yellow
            "Force Completed": "#2E7D32",      # Dark Green
            "ExitStatus1 (1)": "#6D4C41",      # Brown
            "ExitStatus2 (2)": "#D32F2F",      # Dark Red
            "ExitStatus3 (3)": "#F8BBD0",      # Pink
            "ExitStatus5 (5)": "#827717"       # Olive
        }
        # Configure all status tags with colors
        for status, color in self.status_colors.items():
            # Determine if we need white text for dark backgrounds
            dark_backgrounds = ["#F44336", "#2E7D32", "#6D4C41", "#D32F2F", "#827717"]
            text_color = "white" if color in dark_backgrounds else "black"
            self.tree.tag_configure(status, background=color, foreground=text_color)
        # Legacy compatibility tags
        self.tree.tag_configure('PASSED', background='#4CAF50')
        self.tree.tag_configure('FAILED', background='#F44336', foreground='white') 
        self.tree.tag_configure('RUNNING', background='#2196F3', foreground='white')
        self.tree.tag_configure('PENDING', background='#FFEB3B')
        self.tree.tag_configure('EXIT', background='#D32F2F', foreground='white')
        self.tree.tag_configure('Fail', background='#FF9800', foreground='white')
        self.tree.tag_configure('DONE', background='#4CAF50')
        # Map original Netbatch statuses to display statuses
        self.netbatch_to_display_status = {
            'Completed': 'Completed',
            'Running': 'Running', 
            'Canceled': 'Canceled/Stopped',
            'Skipped': 'Skipped',
            'Loaded': 'Loaded',
            'Force Completed': 'Force Completed',
            'Wait': 'Not Running',
            'Rerun Wait': 'Not Running',
            'Finished': 'Completed'
        }


