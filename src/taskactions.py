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

logger = logging.getLogger(__name__)



class TaskActionsMixin:
    """Mixin class for task-related actions"""
    def open_ward(self, task):
        """Open ward for the task - Opens Xterm in CA_ward directory."""
        task_id = task.get('TaskID', 'N/A')
        wardarea = task.get('CA_ward', '')
        self.update_status(f"Opening ward for task {task_id}...", "info")
        if not wardarea:
            messagebox.showerror("Error", f"CA_ward not found for task {task_id}")
            logger.error(f"CA_ward not found for task {task_id}")
            return
        if not os.path.exists(wardarea):
            messagebox.showerror("Error", f"Ward area directory does not exist: {wardarea}")
            logger.error(f"Ward area directory does not exist: {wardarea}")
            return
        try:
            # Open xterm in the wardarea directory
            cmd = ['xterm', '-T', f'{wardarea}', '-e', f'cd "{wardarea}" && tcsh']
            subprocess.Popen(cmd)
            self.update_status(f"Opened ward terminal for task {task_id}", "success")
            logger.info(f"Successfully opened ward terminal for task {task_id} in {wardarea}")
        except Exception as e:
            error_msg = f"Failed to open ward terminal: {str(e)}"
            messagebox.showerror("Error", error_msg)
            logger.error(f"Failed to open ward terminal for task {task_id}: {str(e)}")
            self.update_status("Failed to open ward terminal", "error")
    

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



    def open_ndm(self, task):
        """Open NDM - xterm in ward area with sourced environment."""
        task_id = task.get('TaskID', 'N/A')
        wardarea = task.get('CA_ward', '')
        block = task.get('CA_block', '')
        tech = task.get('CA_tech', '')
        flow = task.get('CA_flow', '')
        nb_pool = task.get('CA_nb_pool', '')
        nb_qslot = task.get('CA_nb_qslot', '')
        nb_class = task.get('CA_nb_class', '')
        logger.info(f"=== Opening NDM for task {task_id} ===")
        self.update_status(f"Opening NDM for task {task_id}...", "info")
        # Log all task attributes
        logger.info(f"Task attributes:")
        logger.info(f"  CA_ward: {wardarea}")
        logger.info(f"  CA_block: {block}")
        logger.info(f"  CA_tech: {tech}")
        logger.info(f"  CA_flow: {flow}")
        logger.info(f"  CA_nb_pool: {nb_pool}")
        logger.info(f"  CA_nb_qslot: {nb_qslot}")
        logger.info(f"  CA_nb_class: {nb_class}")
        logger.info(f"  CA_stagename: {task.get('CA_stagename', '')}")
        logger.info(f"  CA_design: {task.get('CA_design', '')}")
        if not wardarea:
            messagebox.showerror("Error", f"CA_ward not found for task {task_id}")
            logger.error(f"CA_ward not found for task {task_id}")
            return
        if not block:
            messagebox.showerror("Error", f"CA_block not found for task {task_id}")
            logger.error(f"CA_block not found for task {task_id}")
            return
        if not os.path.exists(wardarea):
            messagebox.showerror("Error", f"Ward area directory does not exist: {wardarea}")
            logger.error(f"Ward area directory does not exist: {wardarea}")
            return
        # Construct the setup file path
        wardarea = wardarea.rstrip('/.')
        setup_file = f"{wardarea}/setup/{block}_apr_fc_preFlowEnvDump.csh"
        logger.info(f"Setup file path: {setup_file}")
        if not os.path.exists(setup_file):
            logger.warning(f"Setup file does not exist: {setup_file}")
            messagebox.showwarning("Warning", f"Setup file does not exist:\n{setup_file}\n\nOpening terminal anyway...")
            # Continue anyway to open terminal
        try:
            # Construct the nbjob command
            # Get stage name and design for NDM path
            stage = task.get('CA_stagename', '')
            design = task.get('CA_design', block)  # Use design if available, fallback to block
            logger.info(f"Extracted values:")
            logger.info(f"  stage: {stage}")
            logger.info(f"  design: {design}")
            # Construct the nbjob command with proper NDM path: outputs/<stage>/<design>.ndm
            ndm_path = f"{wardarea}/runs/{block}/{tech}/{flow}/outputs/{stage}/{design}.ndm"
            logger.info(f"NDM path: {ndm_path}")
            nbjob_cmd = f'nbjob run --target {nb_pool} --qslot {nb_qslot} --class "{nb_class}" Ifc_shell -B {block} -D {block} -F apr_fc -P -I -S {ndm_path}'
            logger.info(f"nbjob command: {nbjob_cmd}")
            # Create tcsh command that sources the setup file and echoes the nbjob command
            if os.path.exists(setup_file):
                tcsh_cmd = f'cd {wardarea} && source {setup_file} && echo " Running NDM Command:" && echo {nbjob_cmd} && echo "" && sleep 10 && {nbjob_cmd} && exit '
            else:
                tcsh_cmd = f'cd "{wardarea}" && echo "NDM Command:" && echo "{nbjob_cmd}" && echo "Setup not found " && exit'
            logger.info(f"tcsh command: {tcsh_cmd}")
            # Open xterm with the sourced environment
            cmd = ['xterm', '-T', f'NDM: {block}', '-e', tcsh_cmd]
            logger.info(f"xterm command array: {cmd}")
            # Execute and capture process info
            process = subprocess.Popen(cmd)
            logger.info(f"subprocess.Popen executed successfully, PID: {process.pid}")
            self.update_status(f"Opened NDM terminal for task {task_id}", "success")
            logger.info(f"Successfully opened NDM terminal for task {task_id} in {wardarea}")
            logger.info(f"=== NDM open completed ===")
        except Exception as e:
            error_msg = f"Failed to open NDM terminal: {str(e)}"
            messagebox.showerror("Error", error_msg)
    

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



