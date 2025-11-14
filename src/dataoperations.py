#!/usr/intel/pkgs/python3/3.13.2/bin/python3
import UsrIntel.R1

"""
Data Operations - Loading, filtering, and processing data
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



class DataOperationsMixin:
    """Mixin class for data loading and processing operations"""
    def load_file(self):
        """Load XML file."""
        filename = filedialog.askopenfilename(
            title="Select Netbatch XML File",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        if filename:
            self.load_data_from_file(filename)

    def load_data_from_file_DISABLED(self, filename: str):
        """Load data from XML file."""
        try:
            self.update_status("Loading file...", "loading")
            self.root.config(cursor="watch")
            self.root.update()
            logger.info(f"Loading file: {filename}")
            # self.df = parse_nbstatus_xml(filename)
            # XML loading disabled - use live API data only
            self.current_file = filename
            self.process_loaded_data()
            self.update_status(f"Loaded {len(self.df)} tasks from {os.path.basename(filename)}", "success")
            logger.info(f"Successfully loaded {len(self.df)} tasks")
        except Exception as e:
            logger.error(f"Error loading file: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
            self.update_status("Error loading file", "error")
        finally:
            self.root.config(cursor="")

    def load_live_data(self):
        """Load data from live Netbatch API."""
        try:
            self.update_status("Fetching data from Netbatch API...", "loading")
            self.root.config(cursor="watch")
            self.root.update()
            logger.info("Loading data via Netbatch API")
            
            # Use API-based data provider instead of subprocess
            # Get current username
            username = os.getenv('USER') or os.getenv('USERNAME')
            self.df = self.data_provider.get_tasks_for_gui(username=username)
            
            if self.df.empty:
                messagebox.showwarning("No Data", "No tasks found")
                self.update_status("No tasks found", "warning")
                return
            
            self.current_file = "Live API Data"
            self.process_loaded_data()
            self.update_status(f"Loaded {len(self.df)} tasks from Netbatch API", "success")
            logger.info(f"Successfully loaded {len(self.df)} tasks via API")
        except Exception as e:
            logger.error(f"Error loading live data: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to load data from API:\n{str(e)}")
            self.update_status("Error loading data", "error")
        finally:
            self.root.config(cursor="")
            self.root.config(cursor="")

    def process_loaded_data(self):
        """Process the loaded DataFrame."""
        if self.df is None:
            return
        # Store current filter values before updating
        current_block = self.filters['block'].get()
        current_config = self.filters['config'].get()
        current_status = self.filters['status'].get()
        current_search = self.filters['search'].get()
        current_jobs_only = self.filters['jobs_only'].get()
        # Add derived columns for easier display using pd.concat to avoid fragmentation
        new_columns = {}
        if 'CA_block' in self.df.columns:
            new_columns['Block'] = self.df['CA_block']
        if 'CA_configid' in self.df.columns:
            new_columns['Config'] = self.df['CA_configid']
        if 'CA_design' in self.df.columns:
            new_columns['Design'] = self.df['CA_design']
        if 'Task' in self.df.columns:
            new_columns['TaskName'] = self.df['Task']
        if 'CA_stagename' in self.df.columns:
            new_columns['Stage'] = self.df['CA_stagename']
        if 'CA_nb_class' in self.df.columns:
            new_columns['NBClass'] = self.df['CA_nb_class']
        if 'CA_nb_qslot' in self.df.columns:
            new_columns['NBQSlot'] = self.df['CA_nb_qslot']
        # TaskID - only add if not already present
        if 'TaskID' not in self.df.columns:
            new_columns['TaskID'] = self.df.index
        # Add all new columns at once using concat
        if 'CA_feeder_name' in self.df.columns:
            new_columns['Feeder'] = self.df['CA_feeder_name']
        import pandas as pd
        if new_columns:
            self.df = pd.concat([self.df, pd.DataFrame(new_columns, index=self.df.index)], axis=1)

        # Apply smart status determination logic
        self._apply_smart_status_logic()
        self.update_filter_dropdowns()
        self.apply_filters()



    def _apply_smart_status_logic(self):
        """Apply intelligent status determination based on ExitStatus and FailedJobs."""
        if self.df is None or self.df.empty:
            return
        # Create a copy of original status for reference
        if 'OriginalStatus' not in self.df.columns:
            self.df['OriginalStatus'] = self.df['Status'].copy()
        # Apply smart status logic
        def determine_smart_status(row):
            original_status = row.get('Status', '')
            exit_status = row.get('ExitStatus', None)
            failed_jobs = row.get('FailedJobs', 0)
            skipped_jobs = row.get('SkippedJobs', 0)
            # Convert numeric fields, handle empty/None values
            try:
                exit_status = int(exit_status) if exit_status not in [None, '', 'N/A'] else None
            except (ValueError, TypeError):
                exit_status = None
            try:
                failed_jobs = int(failed_jobs) if failed_jobs not in [None, '', 'N/A'] else 0
            except (ValueError, TypeError):
                failed_jobs = 0
            try:
                skipped_jobs = int(skipped_jobs) if skipped_jobs not in [None, '', 'N/A'] else 0
            except (ValueError, TypeError):
                skipped_jobs = 0
            # Map original status to display status first
            # Map original status to display status first
            display_status = self.netbatch_to_display_status.get(original_status, original_status)
            # Preserve certain final statuses without applying smart logic
            preserve_statuses = ['Force Completed', 'Canceled', 'Finished']
            if original_status in preserve_statuses:
                return display_status
            # Smart status determination logic:
            # 1. Check for SkippedJobs = 1, set status to "Skipped"
            if skipped_jobs == 1:
                return 'Skipped'
            # 2. If ExitStatus is available and non-zero, prioritize ExitStatus display
            if exit_status is not None and exit_status != 0:
                # Map specific ExitStatus codes to display categories
                if exit_status == 1:
                    return 'ExitStatus1 (1)'
                elif exit_status == 2:
                    return 'ExitStatus2 (2)'
                elif exit_status == 3:
                    return 'ExitStatus3 (3)'
                elif exit_status == 5:
                    return 'ExitStatus5 (5)'
                else:
                    # For other non-zero exit status, use generic failed category
                    return 'Canceled/Stopped'
            # 3. If ExitStatus is not available or is zero, check for other conditions
            if exit_status is None or exit_status == 0:
                # If Status is Completed but FailedJobs > 0, mark as "Completed (failures)"
                if display_status == 'Completed' and failed_jobs > 0:
                    return 'Completed (failures)'
                # Otherwise use mapped display status
                return display_status
            # Default: return display status
            return display_status

        # Apply the smart status logic to create new Status column
        self.df['Status'] = self.df.apply(determine_smart_status, axis=1)
        # Log some examples of status changes
        changed_count = (self.df['Status'] != self.df['OriginalStatus']).sum()
        if changed_count > 0:
            logger.info(f"Smart status logic applied: {changed_count} tasks had status updated")


    def update_filter_dropdowns(self):
        """Update filter dropdown values and restore previous selections."""
        if self.df is None:
            return
        
        # Get current filter values (will be preserved from process_loaded_data)
        current_block = self.filters['block'].get()
        current_config = self.filters['config'].get()
        current_status = self.filters['status'].get()
        
        # Update blocks (handle missing column)
        if 'Block' in self.df.columns:
            blocks = ['All Blocks'] + sorted(self.df['Block'].dropna().unique().tolist())
        else:
            blocks = ['All Blocks']
        self.block_combo['values'] = blocks
        if current_block and current_block in blocks:
            self.filters['block'].set(current_block)
        else:
            self.filters['block'].set('All Blocks')
        
        # Update configs (handle missing column)
        if 'Config' in self.df.columns:
            configs = ['All Configs'] + sorted(self.df['Config'].dropna().unique().tolist())
        else:
            configs = ['All Configs']
        self.config_combo['values'] = configs
        if current_config and current_config in configs:
            self.filters['config'].set(current_config)
        
        # Update feeders (handle missing column)
        if 'Feeder' in self.df.columns:
            feeders = ['All Feeders'] + sorted(self.df['Feeder'].dropna().unique().tolist())
        else:
            feeders = ['All Feeders']
        self.feeder_combo['values'] = feeders
        current_feeder = self.filters.get('feeder')
        if current_feeder and current_feeder.get() and current_feeder.get() in feeders:
            self.filters['feeder'].set(current_feeder.get())
        else:
            self.filters['feeder'].set('All Feeders')
        
        # Update statuses (handle missing column)
        if 'Status' in self.df.columns:
            statuses = ['All Status'] + sorted(self.df['Status'].dropna().unique().tolist())
        else:
            statuses = ['All Status']
        self.status_combo['values'] = statuses
        if current_status and current_status in statuses:
            self.filters['status'].set(current_status)
        else:
            self.filters['status'].set('All Status')


    def on_feeder_changed(self):
        """Handle feeder selection change - update config and block dropdowns to show only relevant items."""
        if self.df is None:
            return
        
        # Check if columns exist
        if 'Feeder' not in self.df.columns:
            self.apply_filters()
            return
        
        selected_feeder = self.filters['feeder'].get()
        
        # Filter data based on selected feeder
        if selected_feeder == 'All Feeders':
            filtered_df = self.df
        else:
            filtered_df = self.df[self.df['Feeder'] == selected_feeder]
        
        # Update configs dropdown
        if 'Config' in self.df.columns:
            configs = ['All Configs'] + sorted(filtered_df['Config'].dropna().unique().tolist())
            current_config = self.filters['config'].get()
            self.config_combo['values'] = configs
            if current_config not in configs:
                self.filters['config'].set('All Configs')
        
        # Update blocks dropdown
        if 'CA_block' in filtered_df.columns:
            blocks = ['All Blocks'] + sorted(filtered_df['CA_block'].dropna().unique().tolist())
            current_block = self.filters['block'].get()
            self.block_combo['values'] = blocks
            if current_block not in blocks:
                self.filters['block'].set('All Blocks')
        
        # Update status dropdown
        if 'Status' in filtered_df.columns:
            statuses = ['All Status'] + sorted(filtered_df['Status'].dropna().unique().tolist())
            current_status = self.filters['status'].get()
            self.status_combo['values'] = statuses
            if current_status not in statuses:
                self.filters['status'].set('All Status')
        
        # Apply filters
        self.apply_filters()
    

    def on_config_changed(self):
        """Handle config selection change - update block dropdown to show only relevant blocks."""
        if self.df is None:
            return
        
        # Check if columns exist
        if 'Block' not in self.df.columns or 'Config' not in self.df.columns:
            self.apply_filters()
            return
        
        selected_feeder = self.filters['feeder'].get()
        selected_config = self.filters['config'].get()
        
        # Filter data based on feeder and config
        filtered_df = self.df
        if selected_feeder != 'All Feeders':
            filtered_df = filtered_df[filtered_df['Feeder'] == selected_feeder]
        if selected_config != 'All Configs':
            filtered_df = filtered_df[filtered_df['Config'] == selected_config]
        
        # Update blocks dropdown
        if 'CA_block' in filtered_df.columns:
            blocks = ['All Blocks'] + sorted(filtered_df['CA_block'].dropna().unique().tolist())
        else:
            blocks = ['All Blocks']
        current_block = self.filters['block'].get()
        self.block_combo['values'] = blocks
        
        # Reset block selection if current block is not in the new list
        if current_block not in blocks:
            self.filters['block'].set('All Blocks')
        
        # Update status dropdown
        if 'Status' in filtered_df.columns:
            statuses = ['All Status'] + sorted(filtered_df['Status'].dropna().unique().tolist())
            current_status = self.filters['status'].get()
            self.status_combo['values'] = statuses
            if current_status not in statuses:
                self.filters['status'].set('All Status')
        
        # Apply filters
        self.apply_filters()

    def on_block_changed(self):
        """Handle block selection change - update status dropdown and apply filters."""
        if self.df is None:
            return
        
        # Check if columns exist
        if 'Status' not in self.df.columns:
            self.apply_filters()
            return
        
        selected_feeder = self.filters['feeder'].get()
        selected_config = self.filters['config'].get()
        selected_block = self.filters['block'].get()
        
        # Filter data based on feeder, config, and block
        filtered_df = self.df
        if selected_feeder != 'All Feeders' and 'Feeder' in self.df.columns:
            filtered_df = filtered_df[filtered_df['Feeder'] == selected_feeder]
        if selected_config != 'All Configs' and 'CA_configid' in self.df.columns:
            filtered_df = filtered_df[filtered_df['CA_configid'] == selected_config]
        if selected_block != 'All Blocks' and 'CA_block' in self.df.columns:
            filtered_df = filtered_df[filtered_df['CA_block'] == selected_block]
        
        # Update status dropdown
        statuses = ['All Status'] + sorted(filtered_df['Status'].dropna().unique().tolist())
        current_status = self.filters['status'].get()
        self.status_combo['values'] = statuses
        if current_status not in statuses:
            self.filters['status'].set('All Status')
        
        # Apply filters
        self.apply_filters()

    def apply_filters(self):
        """Apply filters to the data."""
        if self.df is None:
            return
        
        # Start with full dataset
        filtered = self.df.copy()
        
        # Apply filters in sequence
        # 1. Jobs Only filter - only show tasks where flow=apr_fc AND TaskName is not empty AND Stage is not empty
        if self.filters['jobs_only'].get():
            if 'CA_flow' in filtered.columns and 'TaskName' in filtered.columns and 'Stage' in filtered.columns:
                filtered = filtered[
                    (filtered['CA_flow'] == 'apr_fc') & 
                    (filtered['TaskName'].notna()) & 
                    (filtered['TaskName'] != '') &
                    (filtered['Stage'].notna()) &
                    (filtered['Stage'] != '')
                ]
        
        # 2. Config filter (applied first for cascade)
        if 'Config' in filtered.columns:
            config = self.filters['config'].get()
            if config != 'All Configs':
                filtered = filtered[filtered['Config'] == config]
        
        # 3. Feeder filter (applied after config, before block for cascade)
        if 'Feeder' in filtered.columns:
            feeder = self.filters['feeder'].get()
            if feeder != 'All Feeders':
                filtered = filtered[filtered['Feeder'] == feeder]
        # 4. Block filter (applied after config for cascade)
        if 'Block' in filtered.columns:
            block = self.filters['block'].get()
            if block != 'All Blocks':
                filtered = filtered[filtered['Block'] == block]
        
        # 5. Status filter
        if 'Status' in filtered.columns:
            status = self.filters['status'].get()
            if status != 'All Status':
                filtered = filtered[filtered['Status'] == status]
        
        # 6. Search filter (applied last to search within filtered results)
        search = self.filters['search'].get().strip()
        if search:
            # Search across available columns
            mask = pd.Series([False] * len(filtered), index=filtered.index)
            
            search_columns = ['TaskID', 'Block', 'Config', 'Design', 'TaskName', 'Task', 'Status']
            for col in search_columns:
                if col in filtered.columns:
                    mask |= filtered[col].astype(str).str.contains(search, case=False, na=False)
            
            filtered = filtered[mask]
        
        # Store filtered data and update display
        self.filtered_df = filtered
        self.populate_table()
        self.update_status(f"Showing {len(filtered)} of {len(self.df)} tasks", "info")


    def populate_table(self):
        """Populate the table with filtered data."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if self.filtered_df is None or self.filtered_df.empty:
            return
        
        for idx, row in self.filtered_df.iterrows():
            # Build values tuple - handle missing columns gracefully
            def get_val(col):
                try:
                    if col in row.index:
                        val = row[col]
                        # Handle case where val might be a Series
                        if isinstance(val, pd.Series):
                            val = val.iloc[0] if len(val) > 0 else ""
                        return str(val) if pd.notna(val) else ""
                    return ""
                except Exception as e:
                    return ""
            
            values = (
                get_val('TaskID') or str(idx),  # Use index as fallback for TaskID
                get_val('TaskName') or get_val('Task'),  # Task as fallback
                get_val('Config'),
                get_val('Block'),
                get_val('Design'),
                get_val('Stage'),
                get_val('Status'),
                get_val('Duration'),
                get_val('Started'),
                get_val('NBClass'),
                get_val('NBQSlot'),
                get_val('WorkAreaPercentUsed')
            )
            
            status = get_val('Status')
            # Use the status directly as a tag if it exists in our color scheme
            valid_status_tags = list(self.status_colors.keys()) + ['PASSED', 'FAILED', 'RUNNING', 'PENDING', 'EXIT', 'Fail', 'DONE', 'Completed', 'Skipped', 'Force Completed', 'Finished', 'Canceled']
            tags = (status,) if status in valid_status_tags else ()
            self.tree.insert('', tk.END, values=values, tags=tags)


    def sort_column(self, col):
        """Sort table by column."""
        if self.filtered_df is None or self.filtered_df.empty:
            return
        if not hasattr(self, '_sort_order'):
            self._sort_order = {}
        ascending = self._sort_order.get(col, True)
        self._sort_order[col] = not ascending
        self.filtered_df = self.filtered_df.sort_values(by=col, ascending=ascending)
        self.populate_table()


