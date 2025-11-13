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
    def open_log_viewer(self, task):
        """Open log viewer in xterm using icc2_log_viewer."""
        task_id = task.get('TaskID', 'N/A')
        stage = task.get('CA_stagename', '')
        taskname = task.get('Task', '')
        flow = task.get('CA_flow', '')
        wardarea = task.get('CA_ward', '')
        block = task.get('CA_block', '')
        if stage and str(stage).strip() and str(stage).lower() != 'nan':
            # If stage exists, use: wardarea/NBFlogs/block/flow/stage.log
            log_file = f"{wardarea}/NBFlogs/{block}/{flow}/{stage}.log"
        else:
            # If no stage, use: wardarea/logs/taskname.log
            log_file = ""
        logger.info(f"Determined log file path: {log_file}")
        self.update_status(f"Opening log viewer for task {task_id}...", "info")
        
        if not log_file:
            messagebox.showerror("Error", f"This is not apr stage --> {task_id}")
            logger.error(f" This is not apr stage --> {task_id}")
            return
        
        if not os.path.exists(log_file):
            messagebox.showerror("Error", f"Log file does not exist: {log_file}")
            logger.error(f"Log file does not exist: {log_file}")
            return
        
        try:
            # Path to icc2_log_viewer
            log_viewer_cmd = '/nfs/site/disks/home_user/kushwaha/utility_scripts/sasi_scripts/scripts/icc2_log_viewer'
            
            if not os.path.exists(log_viewer_cmd):
                messagebox.showerror("Error", f"icc2_log_viewer not found at:\\n{log_viewer_cmd}")
                logger.error(f"icc2_log_viewer not found: {log_viewer_cmd}")
                return
            
            # Create temporary script file to run log viewer
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csh', delete=False) as temp_script:
                temp_script.write("#!/bin/tcsh -f\n\n")

                temp_script.write(f'{log_viewer_cmd} -v all --huge-file --no-merge "{log_file}"\n')
                temp_script.write('echo "Press Enter to close..."\n')
                temp_script.write("set dummy = $<\n")
                temp_script_path = temp_script.name
            
            # Make script executable
            os.chmod(temp_script_path, 0o755)
            
            # Run the script in xterm
            cmd = ['xterm', '-T', f'Log Viewer - Task {task_id}', '-e', temp_script_path]
            
            subprocess.Popen(cmd)
            
            self.update_status(f"Opened log viewer in xterm for task {task_id}", "success")
            logger.info(f"Successfully opened log viewer in xterm for task {task_id}: {log_file}")
            
        except Exception as e:
            error_msg = f"Failed to open log viewer: {str(e)}"
            messagebox.showerror("Error", error_msg)
            logger.error(f"Failed to open log viewer for task {task_id}: {str(e)}")
            self.update_status("Failed to open log viewer", "error")


