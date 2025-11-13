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
    def open_nbflow_gui(self, task):
        """Simple NBflow GUI: copy CA_ward/.gui_nbf, append setenv, execute."""
        task_id = task.get('TaskID', 'N/A')
        parent_task = task.get('ParentTask', task_id)
        ca_ward = task.get('CA_ward', '')
        self.update_status(f"Opening NBflow GUI for task {task_id}...", "info")
        if not ca_ward or not os.path.exists(ca_ward):
            messagebox.showerror("Error", f"CA_ward not found or invalid: {ca_ward}")
            return
        try:
            # Read existing __NB_FLOW_GUI_URL from .gui_nbf
            gui_nbf_source = os.path.join(ca_ward, ".gui_nbf")
            existing_url = None
            if os.path.exists(gui_nbf_source):
                with open(gui_nbf_source, 'r') as source:
                    for line in source:
                        # Extract existing setenv __NB_FLOW_GUI_URL value
                        if line.strip().startswith('setenv __NB_FLOW_GUI_URL'):
                            existing_url = line.strip().split(' ', 2)[-1] if len(line.strip().split(' ', 2)) > 2 else None
                            print(f"Found existing __NB_FLOW_GUI_URL: {existing_url}")
                            break
            # Create new URL by appending /{parent_task}
            if existing_url:
                new_url = f"{existing_url}/{parent_task}"
            else:
                # Fallback URL if no existing URL found
                new_url = f"https://nbflow-pesg.swiss.intel.com/feeder/scce02441316.zsc7.intel.com:45393/tasks/{parent_task}"
            print(f"New __NB_FLOW_GUI_URL: {new_url}")
            # Create tcsh script with new URL
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csh', delete=False) as temp_script:
                temp_script.write("#!/bin/tcsh -f\n\n")
                temp_script.write(f"setenv __NB_FLOW_GUI_URL {new_url}\n")
                temp_script.write("nbflow &\n")
                temp_script_path = temp_script.name
            # Make script executable and run it
            os.chmod(temp_script_path, 0o755)
            subprocess.run(temp_script_path, shell=True, executable="/bin/tcsh")

        except Exception as e:
            error_msg = f"Failed to launch NBflow GUI: {str(e)}"
            messagebox.showerror("Error", error_msg)
            logger.error(f"NBflow GUI error for task {task_id}: {str(e)}")
            self.update_status("NBflow GUI failed", "error")

