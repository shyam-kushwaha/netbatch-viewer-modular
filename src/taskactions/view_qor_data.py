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
    def view_qor_data(self, task):
        """View QOR Data report in browser using Python HTTP server."""
        task_id = task.get('TaskID', 'N/A')
        wardarea = task.get('CA_ward', '')
        block = task.get('CA_block', '')
        tech = task.get('CA_tech', '')
        flow = task.get('CA_flow', '')
        self.update_status(f"Opening QOR Data viewer for task {task_id}...", "info")
        
        if not wardarea:
            messagebox.showerror("Error", f"CA_ward not found for task {task_id}")
            logger.error(f"CA_ward not found for task {task_id}")
            return
        
        if not block:
            messagebox.showerror("Error", f"CA_block not found for task {task_id}")
            logger.error(f"CA_block not found for task {task_id}")
            return
        
        if not tech:
            messagebox.showerror("Error", f"CA_tech not found for task {task_id}")
            logger.error(f"CA_tech not found for task {task_id}")
            return
        
        # Build QOR report path: <ward>/runs/<block><tech>/<flow>/Qor_sum_reports/compare_qor_data
        qor_path = os.path.join(wardarea, "runs", block,tech, flow, "Qor_sum_reports", "compare_qor_data")
        
        logger.info(f"QOR path: {qor_path}")
        
        if not os.path.exists(qor_path):
            error_msg = f"QOR report directory not found:\n{qor_path}"
            messagebox.showerror("Error", error_msg)
            logger.error(f"QOR report directory not found: {qor_path}")
            self.update_status("QOR report not found", "error")
            return
        
        # Check if index.html exists
        index_file = os.path.join(qor_path, "index.html")
        if not os.path.exists(index_file):
            error_msg = f"index.html not found in QOR report directory:\n{qor_path}"
            messagebox.showerror("Error", error_msg)
            logger.error(f"index.html not found: {index_file}")
            return
        
        try:
            # Find an available port
            import socket
            def find_free_port():
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', 0))
                    s.listen(1)
                    port = s.getsockname()[1]
                return port
            
            port = find_free_port()
            
            # Start HTTP server in a separate thread
            def start_server():
                os.chdir(qor_path)
                Handler = http.server.SimpleHTTPRequestHandler
                with socketserver.TCPServer(("", port), Handler) as httpd:
                    logger.info(f"Serving QOR report at http://localhost:{port}")
                    httpd.serve_forever()
            
            server_thread = threading.Thread(target=start_server, daemon=True)
            server_thread.start()
            
            # Give server a moment to start
            import time
            time.sleep(1)
            
            # Open browser
            url = f"http://localhost:{port}"
            webbrowser.open(url)
            
            self.update_status(f"QOR Data viewer opened at port {port}", "success")
            logger.info(f"Successfully opened QOR Data viewer for task {task_id} at {url}")
            
            # Info dialog removed - browser opens automatically
            
        except Exception as e:
            error_msg = f"Failed to open QOR Data viewer: {str(e)}"
            messagebox.showerror("Error", error_msg)
            logger.error(f"Failed to open QOR Data viewer for task {task_id}: {str(e)}")
            self.update_status("Failed to open QOR viewer", "error")



