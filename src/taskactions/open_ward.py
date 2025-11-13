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
    def open_ward(self, task):
        """Open ward for the task - Opens Xterm in CA_ward directory and sources setup file."""
        task_id = task.get('TaskID', 'N/A')
        wardarea = task.get('CA_ward', '')
        block = task.get('CA_block', '')
        
        
        self.update_status(f"Opening ward for task {task_id}...", "info")
        
        if not wardarea:
            messagebox.showerror("Error", f"CA_ward not found for task {task_id}")
            logger.error(f"CA_ward not found for task {task_id}")
            return
        
        if not os.path.exists(wardarea):
            messagebox.showerror("Error", f"Ward area directory does not exist: {wardarea}")
            logger.error(f"Ward area directory does not exist: {wardarea}")
            return
        
        # Search for setup file: <partition>_<config>_<partition>_apr_fc.csh
        setup_file = None
        setup_file_patterns = []
        if block:
            # Fallback patterns
            setup_file_patterns.append(f'{wardarea}/setup/{block}_apr_fc_preFlowEnvDump.csh')
        
                
        # Search for the setup file
        for pattern in setup_file_patterns:
            if os.path.exists(pattern):
                setup_file = pattern
                logger.info(f"Found setup file: {setup_file}")
                break
        
        try:
            # Build the xterm command
            if setup_file:
                # Source the setup file if found
                tcsh_cmd = f'cd "{wardarea}" && echo "" && echo "=== Sourcing Setup File ===" && echo "Setup file: {setup_file}" && echo "" && source "{setup_file}" && echo "" && echo "Setup file sourced successfully!" && echo "" && tcsh'
                logger.info(f"Opening ward terminal with setup file: {setup_file}")
            else:
                # No setup file found, just cd to wardarea
                tcsh_cmd = f'cd "{wardarea}" && tcsh'
                logger.warning(f"No setup file found for task {task_id}, opening ward without sourcing")
            
            cmd = ['xterm', '-T', f'{wardarea}', '-e', tcsh_cmd]
            subprocess.Popen(cmd)
            
            if setup_file:
                self.update_status(f"Opened ward terminal with setup file for task {task_id}", "success")
            else:
                self.update_status(f"Opened ward terminal for task {task_id} (no setup file found)", "success")
            
            logger.info(f"Successfully opened ward terminal for task {task_id} in {wardarea}")
        except Exception as e:
            error_msg = f"Failed to open ward terminal: {str(e)}"
            messagebox.showerror("Error", error_msg)
            logger.error(f"Failed to open ward terminal for task {task_id}: {str(e)}")
            self.update_status("Failed to open ward terminal", "error")
    
