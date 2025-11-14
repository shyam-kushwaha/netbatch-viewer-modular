#!/usr/intel/pkgs/python3/3.13.2/bin/python3
import UsrIntel.R1
"""
Netbatch Data Extractor - Version 3 (Feeder-based)
Gets running feeders for user, then extracts task data from nbstatus
"""

import subprocess
import pandas as pd
import io
import sys
import re


class netbatch_data_extractor:
    """Data extractor using nbstatus feeders and tasks commands"""
    
    def __init__(self):
        """Initialize the extractor"""
        self.nbstatus_path = '/usr/intel/bin/nbstatus'
    
        self.feeders_list = []
        self.feeders_list = []
    def get_running_feeders(self, username):
        """
        Get all running feeders for a user
        
        Args:
            username (str): Username to filter feeders
            
        Returns:
            list: List of feeder names
        """
        try:
            print(f"Fetching running feeders for user: {username}")
            
            # Build command: nbstatus feeders --fields Name --format csv "User=='username' && Status=='Running'"
            filter_expr = f"User=='{username}' && Status=='Running'"
            cmd = [
                self.nbstatus_path, 'feeders', 
                '--fields', 'Name',
                '--format', 'csv',
                filter_expr
            ]
            
            print(f"Running command: {' '.join(cmd)}")
            
            # Execute command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"Error running nbstatus feeders: {result.stderr}")
                return []
            
            # Read CSV output
            df = pd.read_csv(io.StringIO(result.stdout))
            
            if 'Name' in df.columns:
                feeders = df['Name'].dropna().tolist()
                print(f"Found {len(feeders)} running feeders")
                for feeder in feeders:
                    print(f"  - {feeder}")
                return feeders
            else:
                print("No 'Name' column in feeder output")
                return []
                
        except subprocess.TimeoutExpired:
            print("Error: nbstatus feeders command timed out")
            return []
        except Exception as e:
            print(f"Error fetching feeders: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def parse_custom_attributes(self, ca_string):
        """
        Parse CustomAttributes string into dictionary
        
        Args:
            ca_string (str): CustomAttributes string like "key1=val1 key2=val2"
            
        Returns:
            dict: Dictionary with CA_* prefixed keys
        """
        ca_dict = {}
        if not ca_string or pd.isna(ca_string):
            return ca_dict
        
        # Split by space and parse key=value pairs
        pairs = re.findall(r'(\S+?)=(\S+)', ca_string)
        for key, value in pairs:
            # Clean the value to remove any remaining __@@__
            value_cleaned = value.replace('__@@__', ' ')
            ca_dict[f'CA_{key}'] = value_cleaned
            
        return ca_dict
    
    def get_tasks_for_feeders(self, feeders):
        """
        Get tasks for specific feeders using nbstatus
        
        Args:
            feeders (list): List of feeder names
            
        Returns:
            pandas.DataFrame: DataFrame with all task fields
        """
        if not feeders:
            print("No feeders provided, returning empty DataFrame")
            return pd.DataFrame()
        
        all_tasks = []
        
        try:
            print(f"Fetching tasks for {len(feeders)} feeders...")
            
            for feeder in feeders:
                print(f"  Fetching tasks from feeder: {feeder}")
                
                # Build command with --target
                cmd = [
                    self.nbstatus_path, 'tasks',
                    '--target', feeder,
                    '--fields', 'all',
                    '--format', 'csv'
                ]
                
                # Execute command
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode != 0:
                    print(f"    Error getting tasks from {feeder}: {result.stderr}")
                    continue
                
                # Read CSV output into pandas
                try:
                    feeder_df = pd.read_csv(io.StringIO(result.stdout))
                    if not feeder_df.empty:
                        all_tasks.append(feeder_df)
                        print(f"    Found {len(feeder_df)} tasks")
                except Exception as e:
                    print(f"    Error parsing CSV for {feeder}: {str(e)}")
                    continue
            
            if not all_tasks:
                print("No tasks found from any feeder")
                return pd.DataFrame()
            
            # Combine all tasks into single DataFrame
            df = pd.concat(all_tasks, ignore_index=True)
            print(f"\nTotal tasks collected: {len(df)}")
            
            # Parse CustomAttributes to extract CA_* fields
            if 'CustomAttributes' in df.columns:
                print("Parsing CustomAttributes...")
                ca_data = []
                for idx, row in df.iterrows():
                    ca_dict = self.parse_custom_attributes(row['CustomAttributes'])
                    ca_data.append(ca_dict)
                
                # Create CA_* columns DataFrame
                ca_df = pd.DataFrame(ca_data)
                
                # Merge with main DataFrame
                df = pd.concat([df, ca_df], axis=1)
                
                # List extracted CA_* fields
                ca_columns = [col for col in ca_df.columns if col.startswith('CA_')]
                if ca_columns:
                    print(f"Extracted {len(ca_columns)} custom attributes")
            
            print(f"DataFrame created: {len(df)} rows × {len(df.columns)} columns")
            
            return df
            
        except subprocess.TimeoutExpired:
            print("Error: nbstatus tasks command timed out")
            return pd.DataFrame()
        except Exception as e:
            print(f"Error fetching task data: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def get_tasks_for_gui(self, username=None, status_filter=None):
        """
        Main method to get tasks for GUI
        First gets running feeders, then gets tasks from those feeders
        
        Args:
            username (str): Username to filter feeders
            status_filter (str): Filter by status (optional, applied after getting tasks)
            
        Returns:
            pandas.DataFrame: DataFrame with all fields
        """
        if not username:
            print("Error: username is required")
            return pd.DataFrame()
        
        # Step 1: Get running feeders for user
        feeders = self.get_running_feeders(username)
        
        if not feeders:
            print(f"No running feeders found for user: {username}")
            return pd.DataFrame()
        
        # Store feeders list for later use
        self.feeders_list = feeders
        
        print(f"\nFound feeders: {', '.join(feeders[:5])}" + (f" ... and {len(feeders)-5} more" if len(feeders) > 5 else ""))
        
        # Step 2: Get tasks from those feeders
        df = self.get_tasks_for_feeders(feeders)
        
        # Step 3: Apply status filter if provided
        if not df.empty and status_filter and status_filter != "All Status":
            if 'Status' in df.columns:
                df = df[df['Status'] == status_filter]
                print(f"Filtered to {len(df)} tasks with status: {status_filter}")
        
        return df
    
    def get_available_configs(self, df):
        """Get list of unique configs from CA_configid"""
        if 'CA_configid' in df.columns:
            configs = df['CA_configid'].dropna().unique().tolist()
            return sorted(configs)
        return []
    
    def get_available_blocks(self, df):
        """Get list of unique blocks from CA_block"""
        if 'CA_block' in df.columns:
            blocks = df['CA_block'].dropna().unique().tolist()
            return sorted(blocks)
        return []
    
    def get_available_statuses(self, df):
        """Get list of unique statuses"""
        if 'Status' in df.columns:
            statuses = df['Status'].dropna().unique().tolist()
            return sorted(statuses)
        return []
    
    def get_available_feeders(self, df=None):
        """Get list of running feeders (from initial query)"""
        # Return the feeders list obtained from get_running_feeders
        return sorted(self.feeders_list) if self.feeders_list else []
        return []


def main():
    """Test the data extractor"""
    
    extractor = netbatch_data_extractor()
    
    # Get username
    username = sys.argv[1] if len(sys.argv) > 1 else None
    
    if not username:
        print("Usage: python netbatch_data_extractor.py <username>")
        sys.exit(1)
    
    print("=" * 80)
    print("NETBATCH DATA EXTRACTOR V3 TEST (Feeder-based)")
    print(f"User: {username}")
    print("=" * 80 + "\n")
    
    # Get data
    df = extractor.get_all_tasks(username=username)
    
    if not df.empty:
        print("\n" + "=" * 80)
        print("DATA SUMMARY:")
        print("=" * 80)
        print(f"Total tasks: {len(df)}")
        print(f"Total columns: {len(df.columns)}")
        
        # Show first 10 columns
        print(f"\nFirst 10 columns:")
        for col in df.columns[:10]:
            print(f"  - {col}")
        
        # Show CA_* fields
        ca_cols = [col for col in df.columns if col.startswith('CA_')]
        print(f"\nCustom Attributes (CA_*): {len(ca_cols)}")
        for ca in ca_cols[:10]:
            print(f"  - {ca}")
        if len(ca_cols) > 10:
            print(f"  ... and {len(ca_cols) - 10} more")
        
        # Show summary
        configs = extractor.get_available_configs(df)
        blocks = extractor.get_available_blocks(df)
        statuses = extractor.get_available_statuses(df)
        feeders = extractor.get_available_feeders(df)
        
        print(f"\nUnique Configs: {len(configs)}")
        print(f"Unique Blocks: {len(blocks)}")
        print(f"Unique Statuses: {len(statuses)}")
        print(f"Unique Feeders: {len(feeders)}")
    else:
        print("\nNo data found")


if __name__ == "__main__":
    main()
