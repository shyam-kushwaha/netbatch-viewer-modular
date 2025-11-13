#!/usr/intel/pkgs/python3/3.13.2/bin/python3
import UsrIntel.R1

"""
Task Actions - Actions performed on tasks
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
import subprocess
import tempfile
import threading
import http.server
import socketserver
import webbrowser


logger = logging.getLogger(__name__)





class TaskActionsMixin:
    """Mixin class for task-related actions"""
    def open_stage_csv(self, task):
        """Open stage CSV file for the task - reports/<stage>/<stage>.csv."""
        task_id = task.get('TaskID', 'N/A')
        ca_ward = task.get('CA_ward', '')
        block = task.get('CA_block', '')
        tech = task.get('CA_tech', '')
        flow = task.get('CA_flow', '')
        stage = task.get('CA_stagename', '')
        self.update_status(f"Opening stage CSV for task {task_id}...", "info")
        if not ca_ward or not block or not tech or not flow:
            messagebox.showerror("Error", f"Missing required fields (CA_ward, CA_block, CA_tech, CA_flow) for task {task_id}")
            logger.error(f"Missing required fields for task {task_id}")
            return
        if not stage:
            messagebox.showwarning("Warning", f"CA_stagename not found for task {task_id}. Cannot determine stage CSV path.")
            logger.warning(f"CA_stagename not found for task {task_id}")
            return
        # Construct stage CSV path: CA_ward/runs/CA_block/CA_tech/CA_flow/reports/<stage>/<stage>.csv
        ca_ward = ca_ward.rstrip('/.')
        csv_file = f"{ca_ward}/runs/{block}/{tech}/{flow}/reports/{stage}/{stage}.csv"
        if not os.path.exists(csv_file):
            messagebox.showwarning("Warning", f"Stage CSV file does not exist:\n{csv_file}")
            logger.warning(f"Stage CSV file does not exist: {csv_file}")
            return
        try:
            # Open the CSV file in built-in viewer
            self.show_csv_viewer(csv_file, f"Stage CSV: {stage}")
            self.update_status(f"Opened stage CSV for task {task_id}", "success")
            logger.info(f"Successfully opened stage CSV for task {task_id}: {csv_file}")
        except Exception as e:
            error_msg = f"Failed to open stage CSV: {str(e)}"
            messagebox.showerror("Error", error_msg)
            logger.error(f"Failed to open stage CSV for task {task_id}: {str(e)}")
            self.update_status("Failed to open stage CSV", "error")

