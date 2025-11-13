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
    def open_report_dir(self, task):
        """Open report directory for the task."""
        task_id = task.get('TaskID', 'N/A')
        ca_ward = task.get('CA_ward', '')
        block = task.get('CA_block', '')
        tech = task.get('CA_tech', '')
        flow = task.get('CA_flow', '')
        stage= task.get('CA_stagename', '')
        self.update_status(f"Opening report dir for task {task_id}...", "info")
        if not ca_ward or not block or not tech or not flow:
            messagebox.showerror("Error", f"Missing required fields (CA_ward, CA_block, CA_tech, CA_flow) for task {task_id}")
            logger.error(f"Missing required fields for task {task_id}")
            return
        # Construct report directory path: CA_ward/runs/CA_block/CA_tech/CA_flow/reports
        ca_ward = ca_ward.rstrip('/.')
        report_dir = f"{ca_ward}/runs/{block}/{tech}/{flow}/reports/{stage}"
        if not os.path.exists(report_dir):
            messagebox.showerror("Error", f"Report directory does not exist: {report_dir}")
            logger.error(f"Report directory does not exist: {report_dir}")
            return
        try:
            # Open xterm in the report directory
            cmd = ['xterm', '-T', f'Reports: {block}/{tech}/{flow}', '-e', f'cd "{report_dir}" && tcsh']
            subprocess.Popen(cmd)
            self.update_status(f"Opened report directory for task {task_id}", "success")
            logger.info(f"Successfully opened report directory for task {task_id}: {report_dir}")
        except Exception as e:
            error_msg = f"Failed to open report directory: {str(e)}"
            messagebox.showerror("Error", error_msg)
            logger.error(f"Failed to open report directory for task {task_id}: {str(e)}")
            self.update_status("Failed to open report directory", "error")

