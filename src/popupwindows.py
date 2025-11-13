#!/usr/intel/pkgs/python3/3.13.2/bin/python3
import UsrIntel.R1

"""
Popup Windows - Dialog windows and popups
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



class PopupWindowsMixin:
    """Mixin class for popup windows and dialogs"""
    def show_job_details(self, task, parent_window):
        """Show comprehensive job information from XML data."""
        details_window = tk.Toplevel(parent_window)
        details_window.title(f"Job Details - Task {task.get('TaskID', 'N/A')}")
        details_window.geometry("1000x800")
        # Create main frame with tabs
        notebook = ttk.Notebook(details_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # Tab 1: Status & Summary
        status_frame = ttk.Frame(notebook, padding=10)
        notebook.add(status_frame, text="Status & Summary")
        # Tab 2: Technical Details  
        tech_frame = ttk.Frame(notebook, padding=10)
        notebook.add(tech_frame, text="Technical Details")
        # Tab 3: Custom Attributes
        custom_frame = ttk.Frame(notebook, padding=10)
        notebook.add(custom_frame, text="Custom Attributes")
        # Tab 4: All Fields (Raw XML Data)
        raw_frame = ttk.Frame(notebook, padding=10)
        notebook.add(raw_frame, text="All XML Fields")
        # Populate all tabs
        self._populate_status_tab(status_frame, task)
        self._populate_technical_tab(tech_frame, task)
        self._populate_custom_tab(custom_frame, task)
        self._populate_raw_tab(raw_frame, task)
        # Close button
        ttk.Button(details_window, text="Close", command=details_window.destroy).pack(pady=5)


    def _populate_status_tab(self, parent, task):
        """Populate the Status & Summary tab."""
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        # Status determination explanation
        status_explanation = ttk.LabelFrame(scrollable_frame, text="Status Determination Logic", padding=10)
        status_explanation.pack(fill=tk.X, pady=(0, 10))
        status_text = f"""STATUS ANALYSIS FOR TASK {task.get('TaskID', 'N/A')}:

Current Status: {task.get('Status', 'N/A')}
Exit Status: {task.get('ExitStatus', 'N/A')}

HOW STATUS IS DETERMINED:
1. Status Field: Comes directly from XML <Status> tag
   - Common values: Completed, Running, Pending, Failed, Suspended
2. Exit Status: Numeric code from <ExitStatus> tag  
   - 0: Success (all jobs completed successfully)
   - Negative values (e.g., -10): Various failure codes
   - Empty/N/A: Not yet completed or no exit code
3. Job Counts Analysis:
   - Total Jobs: {task.get('TotalJobs', 'N/A')}
   - Successful: {task.get('SuccessfulJobs', 'N/A')}
   - Failed: {task.get('FailedJobs', 'N/A')}
   - Skipped: {task.get('SkippedJobs', 'N/A')}
   - Running: {task.get('RunningJobs', 'N/A')}
4. Progress String: {task.get('Progress', 'N/A')}
   Format: WL=waiting_local; WR=waiting_remote; Run=running; Succ=successful; Fail=failed; Skip=skipped

INTERPRETATION:
- A task can be "Completed" but have a negative exit status if some jobs failed
- Exit Status -10 typically indicates job failures or resource issues
- Check FailedJobs count to see how many jobs within the task failed
"""
        status_label = tk.Text(status_explanation, height=22, wrap=tk.WORD, font=('Courier', 9))
        status_label.pack(fill=tk.BOTH, expand=True)
        status_label.insert('1.0', status_text)
        status_label.config(state=tk.DISABLED)
        # Key Information
        key_info = ttk.LabelFrame(scrollable_frame, text="Key Information", padding=10)
        key_info.pack(fill=tk.X, pady=(0, 10))
        key_fields = [
            ('Task ID', task.get('TaskID', 'N/A')),
            ('Task Name', task.get('Task', 'N/A')),
            ('Full ID', task.get('FullID', 'N/A')),
            ('User', task.get('User', 'N/A')),
            ('Status', task.get('Status', 'N/A')),
            ('Exit Status', task.get('ExitStatus', 'N/A')),
            ('Type', task.get('Type', 'N/A')),
            ('Duration', task.get('Duration', 'N/A')),
            ('Started', task.get('Started', 'N/A')),
            ('Finished', task.get('Finished', 'N/A')),
            ('Work Area', task.get('WorkArea', 'N/A')),
        ]
        for i, (label, value) in enumerate(key_fields):
            row_frame = ttk.Frame(key_info)
            row_frame.pack(fill=tk.X, pady=1)
            ttk.Label(row_frame, text=f"{label}:", width=15, font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
            ttk.Label(row_frame, text=str(value), font=('Arial', 9)).pack(side=tk.LEFT, padx=(5, 0))
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


    def _populate_technical_tab(self, parent, task):
        """Populate the Technical Details tab."""
        scrollbar = ttk.Scrollbar(parent)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget = tk.Text(parent, wrap=tk.WORD, yscrollcommand=scrollbar.set, font=('Courier', 9))
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        technical_info = f"""{'='*80}
TECHNICAL DETAILS FOR TASK {task.get('TaskID', 'N/A')}
{'='*80}

SCHEDULING & EXECUTION:
{'─'*50}
Scheduling Method:    {task.get('SchedulingMethod', 'N/A')}
Local QSlot:         {task.get('LocalQslot', 'N/A')}
Remote Queue:        {task.get('RemoteQueue', 'N/A')}
Weight:              {task.get('Weight', 'N/A')}

TIMING INFORMATION:
{'─'*50}
Submitted:           {task.get('Submitted', 'N/A')}
Started:             {task.get('Started', 'N/A')}
Finished:            {task.get('Finished', 'N/A')}
Duration:            {task.get('Duration', 'N/A')}
Last Update:         {task.get('LastUpdate', 'N/A')}
ETA:                 {task.get('ETA', 'N/A')}
Task Jobs Wait Time: {task.get('TaskJobsWaitTime', 'N/A')}
Times Restarted:     {task.get('TimesRestarted', 'N/A')}

RESOURCE USAGE:
{'─'*50}
Task STime:          {task.get('TaskSTime', 'N/A')} seconds
Task UTime:          {task.get('TaskUTime', 'N/A')} seconds  
Task WTime:          {task.get('TaskWTime', 'N/A')} seconds
Financial Cost:      ${task.get('TaskFinancialCost', 'N/A')}
Work Area % Used:    {task.get('WorkAreaPercentUsed', 'N/A')}% ({task.get('WorkAreaPercentUsedType', 'N/A')})

FILES & PATHS:
{'─'*50}
Configuration File:  {task.get('ConfigurationFile', 'N/A')}
Logfile:             {task.get('Logfile', 'N/A')}
Absolute Path:       {task.get('AbsolutePath', 'N/A')}
Work Area:           {task.get('WorkArea', 'N/A')}

DEPENDENCIES & HIERARCHY:
{'─'*50}
Parent Task:         {task.get('ParentTask', 'N/A')}
Dependent Tasks:     {task.get('DependentTasks', 'N/A')}
Dependency:          {task.get('Dependency', 'N/A')}
Level:               {task.get('Level', 'N/A')}

MONITORING & STATUS:
{'─'*50}
UUID:                {task.get('UUID', 'N/A')}
Is Logging:          {task.get('IsLogging', 'N/A')}
Jobs Log Hierarchy:  {task.get('JobsLogHierarchy', 'N/A')}
Exit Reason:         {task.get('ExitReason', 'N/A')}
Wait Reason:         {task.get('WaitReason', 'N/A')}
Jobs Wait Reason:    {task.get('JobsWaitReason', 'N/A')}
Suspend Reason:      {task.get('SuspendReason', 'N/A')}
"""
        text_widget.insert('1.0', technical_info)
        text_widget.config(state=tk.DISABLED)


    def _populate_custom_tab(self, parent, task):
        """Populate the Custom Attributes tab.""" 
        scrollbar = ttk.Scrollbar(parent)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget = tk.Text(parent, wrap=tk.WORD, yscrollcommand=scrollbar.set, font=('Courier', 9))
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        custom_info = f"""{'='*80}
CUSTOM ATTRIBUTES FOR TASK {task.get('TaskID', 'N/A')}
{'='*80}

"""
        # Get all CA_ attributes
        ca_attrs = [col for col in task.index if col.startswith('CA_')]
        if ca_attrs:
            custom_info += "CA_* ATTRIBUTES:\n"
            custom_info += "─" * 80 + "\n"
            for attr in sorted(ca_attrs):
                value = task.get(attr, 'N/A')
                custom_info += f"{attr:<35}: {value}\n"
        else:
            custom_info += "No CA_* custom attributes found.\n"
        # Also parse CustomAttributes field if it exists
        custom_attrs_raw = task.get('CustomAttributes', '')
        if custom_attrs_raw and custom_attrs_raw != 'N/A' and str(custom_attrs_raw).strip():
            custom_info += f"\n{'='*80}\n"
            custom_info += f"RAW CUSTOM ATTRIBUTES STRING:\n"
            custom_info += f"{'='*80}\n"
            custom_info += f"{custom_attrs_raw}\n\n"
            custom_info += f"PARSED CUSTOM ATTRIBUTES:\n"
            custom_info += f"{'─'*80}\n"
            # Parse key=value pairs
            try:
                pairs = custom_attrs_raw.split(',')
                for pair in pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        custom_info += f"{key.strip():<25}: {value.strip()}\n"
            except Exception as e:
                custom_info += f"Error parsing custom attributes: {e}\n"
        text_widget.insert('1.0', custom_info)
        text_widget.config(state=tk.DISABLED)


    def _populate_raw_tab(self, parent, task):
        """Populate the All XML Fields tab."""
        scrollbar = ttk.Scrollbar(parent)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget = tk.Text(parent, wrap=tk.WORD, yscrollcommand=scrollbar.set, font=('Courier', 8))
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        raw_info = f"""{'='*100}
ALL XML FIELDS (RAW DATA) FOR TASK {task.get('TaskID', 'N/A')}
{'='*100}

Total Fields Available: {len(task.index)}

"""
        # Sort all fields and display them
        for field in sorted(task.index):
            value = task.get(field, 'N/A')
            # Truncate very long values for readability
            if isinstance(value, str) and len(str(value)) > 200:
                display_value = str(value)[:200] + "... [TRUNCATED]"
            else:
                display_value = str(value)
            raw_info += f"{field:<35}: {display_value}\n"
        text_widget.insert('1.0', raw_info)
        text_widget.config(state=tk.DISABLED)

    def show_task_details(self, event):
        """Show detailed information for selected task in a popup window with action buttons."""
        print("DEBUG: show_task_details called")
        selection = self.tree.selection()
        if not selection:
            print("DEBUG: No selection")
            return
        item = self.tree.item(selection[0])
        task_id = item['values'][0]
        # Convert task_id to string for comparison (TaskID in df is stored as string)
        task_id = str(task_id)
        print(f"DEBUG: Selected TaskID: {task_id} (type: {type(task_id).__name__})")
        if self.df is None:
            print("DEBUG: df is None")
            return
        # Get task data from full dataset (not filtered_df)
        # Use simple iteration to avoid duplicate column issues
        try:
            # Convert to string for comparison
            task_id_str = str(task_id).strip()
            
            # Find matching row by iterating
            task = None
            for idx, row in self.df.iterrows():
                # Get TaskID value (handle if it's a Series due to duplicates)
                try:
                    tid = row['TaskID']
                    if isinstance(tid, pd.Series):
                        tid = tid.iloc[0]
                    if str(tid).strip() == task_id_str:
                        task = row
                        break
                except Exception as e:
                    continue
            
            if task is None:
                print(f"DEBUG: Task {task_id} not found in dataframe")
                messagebox.showwarning("Not Found", f"Task {task_id} not found in current data")
                return
                
        except Exception as e:
            print(f"DEBUG: Error getting task data: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to get task data: {str(e)}")
            return
        print(f"DEBUG: Found task data, creating popup window")
        # task is already set from the loop above
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title(f"Task Actions - {task_id}")
        popup.geometry("900x750")
        # Create main container
        main_frame = ttk.Frame(popup)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # Title
        title_label = ttk.Label(main_frame, 
                               text=f"Task: {task_id} - {task.get('TaskName', 'N/A')}", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        # Subtitle with status
        status = task.get('Status', 'N/A')
        subtitle = ttk.Label(main_frame, 
                            text=f"Status: {status} | Config: {task.get('Config', 'N/A')} | Block: {task.get('Block', 'N/A')}",
                            font=('Arial', 10))
        subtitle.pack(pady=(0, 15))
        # Buttons frame
        button_frame = ttk.LabelFrame(main_frame, text="Actions", padding=15)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        # Create 4 buttons vertically stacked
        buttons_info = [
            ("Job Details", lambda: self.show_job_details(task, popup)),
            ("Open Ward", lambda: self.open_ward(task)),
            ("Open Log", lambda: self.open_log(task)),
            ("Load Design for Review", lambda: self._show_load_design_popup(task)),
            ("Open Report Dir", lambda: self.open_report_dir(task)),
            ("Open Stage CSV", lambda: self.open_stage_csv(task)),
            ("Open Log Viewer", lambda: self.open_log_viewer(task)),
            ("View QOR Data", lambda: self.view_qor_data(task)),
            ("Open NBflow GUI", lambda: self.open_nbflow_gui(task))
        ]
        # Add new Run Interactively button after Load Design
        buttons_info.insert(6, ("Run Interactively", lambda: self.run_interactively(task)))
        
        # Arrange buttons in 2 columns
        for idx, (btn_text, btn_command) in enumerate(buttons_info):
            row = idx // 2
            col = idx % 2
            btn = ttk.Button(button_frame, text=btn_text, command=btn_command, width=25)
            btn.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
        
        # Configure column weights for equal distribution
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)        
        # Details frame with scrollbar
        details_frame = ttk.LabelFrame(main_frame, text="Task Information", padding=10)
        details_frame.pack(fill=tk.BOTH, expand=True)
        # Create scrolled text widget
        scrollbar = ttk.Scrollbar(details_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget = tk.Text(details_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                             font=('Courier', 9), height=15)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        # Build details content
        details = f"""BASIC INFORMATION:
TaskID:          {task.get('TaskID', 'N/A')}
Status:          {task.get('Status', 'N/A')}
Block:           {task.get('Block', 'N/A')}
Config:          {task.get('Config', 'N/A')}
Design:          {task.get('Design', 'N/A')}
TaskName:        {task.get('TaskName', 'N/A')}

TIMING:
Started:         {task.get('Started', 'N/A')}
Duration:        {task.get('Duration', 'N/A')}

NETBATCH INFO:
NB Class:        {task.get('NBClass', 'N/A')}
NB QSlot:        {task.get('NBQSlot', 'N/A')}
NB Pool:         {task.get('CA_nb_pool', 'N/A')}
Flow:            {task.get('CA_flow', 'N/A')}
"""
        # Insert text (must insert BEFORE setting to DISABLED)
        text_widget.insert('1.0', details)
        text_widget.config(state=tk.DISABLED)
        # Bottom buttons
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(bottom_frame, text="Close", command=popup.destroy).pack(side=tk.RIGHT)
        # Center popup on parent window
        popup.transient(self.root)
        popup.update_idletasks()  # Make sure window is fully created
        popup.grab_set()
        print("DEBUG: Popup window with buttons created and displayed")
    def show_csv_viewer(self, csv_file: str, title: str = "CSV Viewer"):
        """Display CSV file in a built-in viewer window."""
        import csv
        # Create viewer window
        viewer = tk.Toplevel(self.root)
        viewer.title(title)
        viewer.geometry("1200x700")
        # Title label
        title_frame = ttk.Frame(viewer)
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(title_frame, text=f"File: {csv_file}", font=('Arial', 10, 'bold')).pack(anchor='w')
        # Search frame
        search_frame = ttk.Frame(viewer)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(search_frame, text="Search:", font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 5))
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=40, font=('Arial', 10))
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(search_frame, text="(case-insensitive, searches all columns)", 
                 font=('Arial', 9, 'italic')).pack(side=tk.LEFT)
        # Create frame for treeview with scrollbars
        tree_frame = ttk.Frame(viewer)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        # Read CSV file
        try:
            with open(csv_file, 'r') as f:
                csv_reader = csv.reader(f)
                rows = list(csv_reader)
            if not rows:
                messagebox.showwarning("Empty File", "CSV file is empty")
                viewer.destroy()
                return
            # First row as headers
            headers = rows[0]
            data_rows = rows[1:]
            # Create Treeview
            tree = ttk.Treeview(tree_frame, columns=headers, show='headings',
                               yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            vsb.config(command=tree.yview)
            hsb.config(command=tree.xview)
            # Configure columns
            for i, col in enumerate(headers):
                tree.heading(col, text=col, command=lambda c=col: self.sort_csv_column(tree, c, False))
                # Set column width based on content
                max_width = len(col) * 10
                for row in data_rows[:100]:  # Check first 100 rows for width
                    if i < len(row):
                        max_width = max(max_width, len(str(row[i])) * 8)
                tree.column(col, width=min(max_width, 300))
            # Store all data for filtering
            all_data = []
            for row in data_rows:
                # Pad row if it has fewer columns than headers
                padded_row = row + [''] * (len(headers) - len(row))
                all_data.append(padded_row[:len(headers)])
            
            # Create info label FIRST (before filter_data function)
            info_frame = ttk.Frame(viewer)
            info_frame.pack(fill=tk.X, padx=10, pady=5)
            info_label = ttk.Label(info_frame, text=f"Total Rows: {len(data_rows)} | Columns: {len(headers)}",
                     font=('Arial', 9))
            info_label.pack(side=tk.LEFT)
            
            # Function to filter and display data
            def filter_data(*args):
                # Clear existing items
                for item in tree.get_children():
                    tree.delete(item)
                search_term = search_var.get().lower().strip()
                displayed_count = 0
                for row in all_data:
                    # If no search term, show all rows
                    if not search_term:
                        tree.insert('', tk.END, values=row)
                        displayed_count += 1
                    else:
                        # Search in all columns (case-insensitive)
                        match_found = False
                        for cell in row:
                            if search_term in str(cell).lower():
                                match_found = True
                                break
                        if match_found:
                            tree.insert('', tk.END, values=row)
                            displayed_count += 1
                # Update info label
                if search_term:
                    info_label.config(text=f"Showing {displayed_count} of {len(all_data)} rows | Columns: {len(headers)} | Filter: '{search_var.get()}'")
                else:
                    info_label.config(text=f"Total Rows: {len(all_data)} | Columns: {len(headers)}")
            
            # Initial display
            filter_data()
            
            # Bind search to trigger filtering
            search_var.trace('w', filter_data)
            
            # Grid layout
            tree.grid(row=0, column=0, sticky='nsew')
            vsb.grid(row=0, column=1, sticky='ns')
            hsb.grid(row=1, column=0, sticky='ew')
            tree_frame.grid_rowconfigure(0, weight=1)
            tree_frame.grid_columnconfigure(0, weight=1)
            # Close button
            ttk.Button(viewer, text="Close", command=viewer.destroy).pack(pady=5)
            # Center window
            viewer.transient(self.root)
            viewer.update_idletasks()
            viewer.grab_set()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV file:\n{str(e)}")
            logger.error(f"Failed to read CSV file {csv_file}: {e}")
            viewer.destroy()

    def show_about(self):
        """Show about dialog."""
        about_text = """
Netbatch Status Viewer
Version 1.0

Author: Shyam Sunder Kushwaha
Email: shyam.sunder.kushwaha@intel.com
Date: November 2, 2025

Features:
• Load XML files or live nbstatus data
• Filter by Block, Config, Status
• Search across multiple fields
• View detailed task information
• Analytics dashboard
• Export to CSV

© 2025 Intel Corporation
        """
        messagebox.showinfo("About", about_text)




