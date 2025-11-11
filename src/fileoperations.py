#!/usr/intel/pkgs/python3/3.13.2/bin/python3
import UsrIntel.R1

"""
File Operations - File import/export operations
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



class FileOperationsMixin:
    """Mixin class for file operations"""
    def export_to_csv(self):
        """Export current view to CSV."""
        if self.filtered_df is None or self.filtered_df.empty:
            messagebox.showwarning("No Data", "No data to export")
            return
        filename = filedialog.asksaveasfilename(
            title="Export to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.filtered_df.to_csv(filename, index=False)
                messagebox.showinfo("Success", f"Data exported to {filename}")
                self.update_status(f"Exported {len(self.filtered_df)} rows to CSV", "success")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export:\n{str(e)}")
                logger.error(f"Export error: {e}", exc_info=True)

    def sort_csv_column(self, tree, col, reverse):
        """Sort CSV viewer treeview by column."""
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        # Try numeric sort first, fall back to string sort
        try:
            data.sort(reverse=reverse, key=lambda x: float(x[0]) if x[0] else 0)
        except (ValueError, TypeError):
            data.sort(reverse=reverse, key=lambda x: str(x[0]).lower())
        for index, (_, child) in enumerate(data):
            tree.move(child, '', index)
        # Reverse sort next time
        tree.heading(col, command=lambda: self.sort_csv_column(tree, col, not reverse))
    


