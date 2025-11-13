#!/usr/intel/pkgs/python3/3.13.2/bin/python3
import UsrIntel.R1

"""
Task Actions - Run Interactively
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import sys
import logging
import re
import tempfile

logger = logging.getLogger(__name__)

class TaskActionsMixin:
    """Mixin class for task-related actions"""
    def run_interactively(self, task):
        """Show popup window to configure NetBatch parameters and command for interactive debug."""
        import subprocess
        import os
        import re
        
        task_id = task.get('TaskID', 'N/A')
        wardarea = task.get('CA_ward', '').rstrip('/.')
        block = task.get('CA_block', '')
        tech = task.get('CA_tech', '')
        flow = task.get('CA_flow', '')
        stage = task.get('CA_stagename', '')
        design = task.get('CA_design', block)
        
        # Get NetBatch parameters with defaults
        nb_pool = task.get('CA_nb_pool', '')
        nb_qslot = task.get('CA_nb_qslot', '')
        nb_class = task.get('CA_nb_class', '')
        
        # Get FC version from setup file by grepping FUSIONCOMPILER_DIR/MANPATH/PATH
        fc_version_from_setup = ''
        original_setup_file = f'{wardarea}/setup/{block}_apr_fc_preFlowEnvDump.csh'
            
        if os.path.exists(original_setup_file):
            try:
                with open(original_setup_file, 'r') as f:
                    for line in f:
                        # Search for /p/hdk/cad/fusioncompiler/<version> in any line
                        # Version may end with /, :, ', or whitespace
                        match = re.search(r'/p/hdk/cad/fusioncompiler/([^/:\s\'\"]+)', line)
                        if match:
                            fc_version_from_setup = match.group(1)
                            break
            except Exception as e:
                print(f"Error reading setup file: {e}")
       
        # Get available FC versions from /p/hdk/cad/fusioncompiler/
        fc_versions = []
        fc_dir = '/p/hdk/cad/fusioncompiler/'
        if os.path.exists(fc_dir):
            try:
                fc_versions = sorted([d for d in os.listdir(fc_dir) 
                                     if os.path.isdir(os.path.join(fc_dir, d)) and not d.startswith('.')],
                                    reverse=True)
            except Exception as e:
                print(f"Error listing FC versions: {e}")
        
        # Get CA_debugcommand or construct default
        ca_command = task.get('CA_debugcommand', '')
        
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title(f"Run Interactively - Task {task_id}")
        popup.geometry("900x700")
        popup.transient(self.root)
        
        # Main frame
        main_frame = ttk.Frame(popup, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text=f"Configure Interactive Debug - {block}", 
                               font=('Arial', 12, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # NetBatch Parameters Frame
        nb_frame = ttk.LabelFrame(main_frame, text="NetBatch Parameters", padding=10)
        nb_frame.pack(fill=tk.X, pady=(0, 10))
        
        # NB Pool - Text Entry
        ttk.Label(nb_frame, text="NB Pool:", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        ttk.Label(nb_frame, text=f"Current: {nb_pool if nb_pool else 'Not set'}", 
                 font=('Arial', 8, 'bold'), foreground='blue').grid(row=0, column=2, sticky='w', padx=5, pady=5)
        nb_pool_var = tk.StringVar(value=nb_pool)
        nb_pool_entry = ttk.Entry(nb_frame, textvariable=nb_pool_var, width=40)
        nb_pool_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        # NB QSlot - Text Entry
        ttk.Label(nb_frame, text="NB QSlot:", font=('Arial', 9, 'bold')).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        ttk.Label(nb_frame, text=f"Current: {nb_qslot if nb_qslot else 'Not set'}", 
                 font=('Arial', 8, 'bold'), foreground='blue').grid(row=1, column=2, sticky='w', padx=5, pady=5)
        nb_qslot_var = tk.StringVar(value=nb_qslot)
        nb_qslot_entry = ttk.Entry(nb_frame, textvariable=nb_qslot_var, width=40)
        nb_qslot_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        # NB Class - Text Entry
        ttk.Label(nb_frame, text="NB Class:", font=('Arial', 9, 'bold')).grid(row=2, column=0, sticky='w', padx=5, pady=5)
        ttk.Label(nb_frame, text=f"Current: {nb_class if nb_class else 'Not set'}", 
                 font=('Arial', 8, 'bold'), foreground='blue').grid(row=2, column=2, sticky='w', padx=5, pady=5)
        nb_class_var = tk.StringVar(value=nb_class)
        nb_class_entry = ttk.Entry(nb_frame, textvariable=nb_class_var, width=40)
        nb_class_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        
        # FC Version - Dropdown
        ttk.Label(nb_frame, text="FC Version:", font=('Arial', 9, 'bold')).grid(row=3, column=0, sticky='w', padx=5, pady=5)
        ttk.Label(nb_frame, text=f"Current: {fc_version_from_setup if fc_version_from_setup else 'Not found'}", 
                 font=('Arial', 8, 'bold'), foreground='blue').grid(row=3, column=2, sticky='w', padx=5, pady=5)
        fc_version_var = tk.StringVar(value=fc_version_from_setup if fc_version_from_setup else (fc_versions[0] if fc_versions else ''))
        fc_version_combo = ttk.Combobox(nb_frame, textvariable=fc_version_var, width=40, values=fc_versions)
        fc_version_combo.grid(row=3, column=1, sticky='ew', padx=5, pady=5)
        
        nb_frame.columnconfigure(1, weight=1)
        
        # Command Frame
        cmd_frame = ttk.LabelFrame(main_frame, text="Command", padding=10)
        cmd_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(cmd_frame, text="CA Debug Command:", font=('Arial', 9, 'bold')).pack(anchor='w', pady=(0, 5))
        
        # Text widget for command editing
        cmd_text = tk.Text(cmd_frame, height=8, wrap=tk.WORD, font=('Courier', 9))
        cmd_text.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        cmd_text.insert('1.0', ca_command)
        
        # Preview Frame
        preview_frame = ttk.LabelFrame(main_frame, text="Command Preview", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        preview_text = tk.Text(preview_frame, height=6, wrap=tk.WORD, font=('Courier', 8), state=tk.DISABLED)
        preview_text.pack(fill=tk.BOTH, expand=True)
        
        def update_preview(*args):
            """Update the command preview."""
            pool = nb_pool_var.get()
            qslot = nb_qslot_var.get()
            nbclass = nb_class_var.get()
            command = cmd_text.get('1.0', 'end-1c').strip()
            
            # Modify -output_log_file to add _debug before .log
            modified_command = re.sub(r'(-output_log_file\s+\S*?)\.log', r'\1_debug.log', command)
            
            if '-output_log_file' not in modified_command and modified_command:
                # If no -output_log_file exists, add it
                modified_command += f' -output_log_file {wardarea}/logs/{block}_debug.log'
            
            # Build nbjob command
            full_cmd = f'nbjob run'
            if pool:
                full_cmd += f' --target {pool}'
            if qslot:
                full_cmd += f' --qslot {qslot}'
            if nbclass:
                full_cmd += f' --class "{nbclass}"'
            full_cmd += f' {modified_command}'
            
            preview_text.config(state=tk.NORMAL)
            preview_text.delete('1.0', tk.END)
            preview_text.insert('1.0', full_cmd)
            preview_text.config(state=tk.DISABLED)
        
        # Bind updates
        nb_pool_var.trace('w', update_preview)
        nb_qslot_var.trace('w', update_preview)
        nb_class_var.trace('w', update_preview)
        fc_version_var.trace('w', update_preview)
        cmd_text.bind('<KeyRelease>', update_preview)
        
        # Initial preview
        update_preview()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def execute_command():
            """Execute the configured command."""
            import tempfile
            
            pool = nb_pool_var.get()
            qslot = nb_qslot_var.get()
            nbclass = nb_class_var.get()
            command = cmd_text.get('1.0', 'end-1c').strip()
            selected_fc_version = fc_version_var.get()
            
            # Modify -output_log_file to add _debug before .log
            modified_command = re.sub(r'(-output_log_file\s+\S*?)\.log', r'\1_debug.log', command)
            
            if '-output_log_file' not in modified_command and modified_command:
                modified_command += f' -output_log_file {wardarea}/logs/{block}_debug.log'
            

            try:
                nbjob_cmd = f'nbjob run --target {nb_pool} --qslot {nb_qslot} --class "{nb_class}" {modified_command}'
                logger.info(f"nbjob command: {nbjob_cmd}")
                # Determine setup file to use
                setup_file_to_use = original_setup_file
                
                # If user changed FC version, create temp setup file
                if selected_fc_version and selected_fc_version != fc_version_from_setup and original_setup_file:
                    try:
                        # Create temp file
                        fd, temp_setup_file = tempfile.mkstemp(suffix='.csh', prefix='fc_setup_', dir='/tmp')
                        os.close(fd)
                        
                        # Read original and replace ALL FC version paths
                        with open(original_setup_file, 'r') as f:
                            setup_content = f.read()
                        
                        # Replace ALL occurrences of the old FC version path with new one
                        # This handles FUSIONCOMPILER_DIR, MANPATH, PATH, and any other references
                        new_fc_path = f'/p/hdk/cad/fusioncompiler/{selected_fc_version}'
                        
                        # Replace using regex to handle different endings (/, :, ', whitespace)
                        setup_content = re.sub(
                            r'/p/hdk/cad/fusioncompiler/[^/:\s\'"]+',
                            new_fc_path,
                            setup_content
                        )
                        
                        with open(temp_setup_file, 'w') as f:
                            f.write(setup_content)
                        
                        setup_file_to_use = temp_setup_file
                        print(f"Created temp setup file with FC version {selected_fc_version}: {temp_setup_file}")
                    except Exception as e:
                        print(f"Error creating temp setup file: {e}")
                        messagebox.showerror("Error", f"Failed to create temp setup file: {str(e)}")
                        return
                
                
                # Build tcsh command
                if os.path.exists(setup_file_to_use):
                    if 'temp_setup_file' in locals() and setup_file_to_use == temp_setup_file:
                        tcsh_cmd = f'cd {wardarea} && source {setup_file_to_use} && {nbjob_cmd} && sleep 30 && rm -rf {temp_setup_file} && exit'
                    else:
                        tcsh_cmd = f'cd {wardarea} && source {setup_file_to_use} && {nbjob_cmd} && sleep 30 && exit'
                else:
                    tcsh_cmd = f'cd "{wardarea}" && echo "Setup not found: {setup_file_to_use}" && echo "Press Enter to close..." && set dummy = $<'
                
                logger.info(f"tcsh command: {tcsh_cmd}")
                
                # Write tcsh command to log file
                cmd_log_file = f"{wardarea}/run_interactively_tcsh_cmd_{block}.log"
                try:
                    with open(cmd_log_file, "w") as f:
                        f.write("="*80 + "\n")
                        f.write(f"Run Interactively Command for {block}\n")
                        f.write(f"Timestamp: " + __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
                        f.write("="*80 + "\n\n")
                        f.write("TCSH Command:\n")
                        f.write("-"*80 + "\n")
                        f.write(tcsh_cmd + "\n\n")
                        f.write("="*80 + "\n")
                    logger.info(f"Wrote tcsh command to: {cmd_log_file}")
                except Exception as e:
                    logger.warning(f"Could not write command log file: {e}")

                cmd = ['xterm', '-T', f'Interactive Debug: {block}', '-e', tcsh_cmd]
                subprocess.Popen(cmd)
                
                self.update_status(f"Launched interactive debug for task {task_id}", "success")
                logger.info(f"Interactive debug launched for task {task_id} with command: {nbjob_cmd}")
                popup.destroy()
                
            except Exception as e:
                error_msg = f"Failed to launch interactive debug: {str(e)}"
                messagebox.showerror("Error", error_msg)
                logger.error(error_msg)
        
        ttk.Button(button_frame, text="Launch", command=execute_command, width=15).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=popup.destroy, width=15).pack(side=tk.RIGHT)
        
        popup.grab_set()
