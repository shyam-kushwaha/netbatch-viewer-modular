#!/usr/intel/pkgs/python3/3.13.2/bin/python3
import UsrIntel.R1
"""
Netbatch Status Viewer GUI
===========================

A professional GUI application for viewing and analyzing Netbatch status data.

Author: Shyam Sunder Kushwaha
Email: shyam.sunder.kushwaha@intel.com
Date: November 2, 2025
Version: 1.0
"""

import UsrIntel.R1
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
import os
import logging
import subprocess
import tempfile
import threading
import http.server
import socketserver
import webbrowser
from typing import Optional, Dict, List, Any
from datetime import datetime
import pandas as pd

from gui_data_provider import GUIDataProvider

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('netbatch_viewer_gui.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)



# Import mixin classes
from src.uicomponents import UIComponentsMixin
from src.dataoperations import DataOperationsMixin
from src.taskactions import TaskActionsMixin
from src.popupwindows import PopupWindowsMixin
from src.fileoperations import FileOperationsMixin
from src.utils import UtilsMixin


class NetbatchViewerGUI(
    UIComponentsMixin,
    DataOperationsMixin,
    TaskActionsMixin,
    PopupWindowsMixin,
    FileOperationsMixin,
    UtilsMixin
):
    """Main GUI application for Netbatch Status Viewer.
    
    This class inherits from multiple mixin classes, each providing
    a specific set of functionality:
    - UIComponentsMixin: UI setup and widget creation
    - DataOperationsMixin: Data loading and filtering
    - TaskActionsMixin: Task-related actions
    - PopupWindowsMixin: Dialog windows and popups
    - FileOperationsMixin: File import/export
    - UtilsMixin: Utility and helper functions
    """

    """Main GUI application for Netbatch Status Viewer."""
    def __init__(self, root: tk.Tk):
        """Initialize the GUI application."""
        self.root = root
        self.df: Optional[pd.DataFrame] = None
        self.data_provider = GUIDataProvider()  # API-based data provider
        self.filtered_df: Optional[pd.DataFrame] = None
        self.current_file: Optional[str] = None
        # Filter state
        self.filters = {
            'block': tk.StringVar(value="All Blocks"),
            'config': tk.StringVar(value="All Configs"),
            'status': tk.StringVar(value="All Status"),
            'search': tk.StringVar(value=""),
            'feeder': tk.StringVar(value="All Feeders"),
            'jobs_only': tk.BooleanVar(value=True)
        }
        # Auto-refresh settings - must be initialized before create_toolbar()
        self.auto_refresh_job = None
        self.refresh_interval = tk.StringVar(value='Off')
        self.setup_window()
        self.create_menu()
        self.create_toolbar()
        self.create_main_area()
        self.create_status_bar()
        logger.info("Netbatch Viewer GUI initialized")



def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description='Netbatch Status Viewer GUI')
    parser.add_argument('--xml-file', type=str, help='XML file to load on startup')
    args = parser.parse_args()
    root = tk.Tk()
    app = NetbatchViewerGUI(root)

    # Auto-load live data on startup

    # Auto-load live data on startup
    app.load_live_data()
    if args.xml_file:
        app.load_data_from_file(args.xml_file)
    root.mainloop()


if __name__ == '__main__':
    main()


