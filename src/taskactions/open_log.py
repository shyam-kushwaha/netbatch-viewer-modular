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
    def open_log(self, task):
        """Open log file in gvim after sourcing environment in xterm."""
        task_id = task.get('TaskID', 'N/A')
        stage = task.get('CA_stagename', '')
        taskname = task.get('Task', '')
        flow = task.get('CA_flow', '')
        wardarea = task.get('CA_ward', '')
        block = task.get('CA_block', '')
        
        # Determine log file path based on stage or taskname
        if stage and str(stage).strip() and str(stage).lower() != 'nan':
            # If stage exists, use: wardarea/NBFlogs/block/flow/stage.log
            log_file = f"{wardarea}/NBFlogs/{block}/{flow}/{stage}.log"
        else:
            # If no stage, use: wardarea/logs/taskname.log
            log_file = f"{wardarea}/logs/{taskname}.log"
        
        logger.info(f"Determined log file path: {log_file}")
        
        if not log_file:
            messagebox.showerror("Error", f"CA_output_log_file not found for task {task_id}")
            logger.error(f"CA_output_log_file not found for task {task_id}")
            return
            
        if not os.path.exists(log_file):
            messagebox.showerror("Error", f"Log file does not exist: {log_file}")
            logger.error(f"Log file does not exist: {log_file}")
            return
        
        try:
            # If we have ward area and block, source the environment
            if wardarea and block:
                wardarea = wardarea.rstrip('/.')
                setup_file = f"{wardarea}/setup/{block}_apr_fc_preFlowEnvDump.csh"
                
                if os.path.exists(setup_file):
                    # Create a temp script that sources env and opens gvim
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.csh', delete=False) as temp_script:
                        temp_script.write("#!/bin/tcsh -f\n\n")
                        temp_script.write(f"source {setup_file}\n")
                        temp_script.write(f"gvim {log_file} &\n")
                        temp_script.write("exit\n")
                        temp_script_path = temp_script.name
                    
                    os.chmod(temp_script_path, 0o755)
                    
                    # Open xterm to run the script
                    cmd = ['xterm', '-T', f'Log Viewer - {task_id}', '-e', temp_script_path]
                    subprocess.Popen(cmd)
                    
                    self.update_status(f"Opened log with environment for task {task_id}", "success")
                    logger.info(f"Successfully opened log with environment for task {task_id}: {log_file}")
                    return
            
            # Fallback: Open directly in gvim without sourcing
            cmd = ['gvim', log_file]
            subprocess.Popen(cmd)
            self.update_status(f"Opened log for task {task_id}", "success")
            logger.info(f"Successfully opened log for task {task_id}: {log_file}")
            
        except Exception as e:
            error_msg = f"Failed to open log: {str(e)}"
            messagebox.showerror("Error", error_msg)
            logger.error(f"Failed to open log for task {task_id}: {str(e)}")
            self.update_status("Failed to open log", "error")



