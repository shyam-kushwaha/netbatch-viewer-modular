"""
Utilities - Utility and helper functions
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



class UtilsMixin:
    """Mixin class for utility functions"""
    def clear_filters(self):
        """Clear all filters."""
        self.filters['block'].set('All Blocks')
        self.filters['config'].set('All Configs')
        self.filters['status'].set('All Status')
        self.filters['search'].set('')
        self.filters['feeder'].set('All Feeders')
        self.filters['jobs_only'].set(True)
        # Also stop auto-refresh when clearing filters
        self.refresh_interval.set('Off')
        self.stop_auto_refresh()
        self.apply_filters()
        self.update_status("Filters cleared and auto-refresh stopped", "info")

    def refresh_view(self):
        """Refresh the current view."""
        if self.current_file and self.current_file != "Live API Data":
            self.load_data_from_file(self.current_file)
        elif self.current_file == "Live API Data":
            self.load_live_data()
        else:
            self.update_status("No data loaded", "warning")

    def update_status(self, message: str, msg_type: str = "info"):
        """Update status bar message."""
        icons = {
            'info': '[INFO]',
            'success': '[OK]',
            'error': '[ERROR]',
            'warning': '[WARN]',
            'loading': '[WAIT]'
        }
        icon = icons.get(msg_type, '[INFO]')
        self.status_bar.config(text=f"{icon} {message}")
        self.root.update_idletasks()


    def on_refresh_interval_changed(self, event=None):
        """Handle refresh interval change."""
        interval = self.refresh_interval.get()
        # Stop any existing auto-refresh
        self.stop_auto_refresh()
        if interval == 'Off':
            self.update_status("Auto-refresh disabled", "info")
            return
        # Parse interval and convert to milliseconds
        interval_ms = self.parse_interval(interval)
        if interval_ms:
            self.start_auto_refresh(interval_ms)
            self.update_status(f"Auto-refresh enabled: every {interval}", "info")
            logger.info(f"Auto-refresh started with interval: {interval} ({interval_ms}ms)")

    def parse_interval(self, interval_str):
        """Parse interval string to milliseconds."""
        if interval_str == 'Off':
            return None
        # Map interval strings to milliseconds
        intervals = {
            '10s': 10 * 1000,
            '30s': 30 * 1000,
            '1m': 60 * 1000,
            '5m': 5 * 60 * 1000,
            '10m': 10 * 60 * 1000,
            '30m': 30 * 60 * 1000
        }
        return intervals.get(interval_str, None)

    def start_auto_refresh(self, interval_ms):
        """Start auto-refresh with given interval in milliseconds."""
        self.auto_refresh_job = self.root.after(interval_ms, self.auto_refresh_callback)
        logger.info(f"Scheduled auto-refresh job: {self.auto_refresh_job}")

    def stop_auto_refresh(self):
        """Stop auto-refresh."""
        if self.auto_refresh_job:
            self.root.after_cancel(self.auto_refresh_job)
            logger.info(f"Cancelled auto-refresh job: {self.auto_refresh_job}")
            self.auto_refresh_job = None

    def auto_refresh_callback(self):
        """Callback for auto-refresh."""
        logger.info("Auto-refresh triggered")
        self.refresh_view()
        # Schedule next refresh if still enabled
        interval = self.refresh_interval.get()
        if interval != 'Off':
            interval_ms = self.parse_interval(interval)
            if interval_ms:
                self.auto_refresh_job = self.root.after(interval_ms, self.auto_refresh_callback)


