#!/usr/intel/pkgs/python3/3.13.2/bin/python3
import UsrIntel.R1
"""
Netbatch GUI Data Provider - Version 2 (Shell Command Based)
Uses nbstatus shell command instead of Python API to avoid field validation issues
"""

import subprocess
import pandas as pd
import io
import sys
import re


class GUIDataProvider:
    """Data provider using nbstatus shell command"""
    
    def __init__(self):
        """Initialize the provider"""
        pass
    
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
        
        # Remove __@@__ markers if present
        #ca_string_cleaned = str(ca_string).replace('__@@__', '')
            
            
        # Split by space and parse key=value pairs
        pairs = re.findall(r'(\S+?)=(\S+)', ca_string)
        for key, value in pairs:
            # Clean the value to remove any remaining __@@__
            value_cleaned = value.replace('__@@__', ' ')
            ca_dict[f'CA_{key}'] = value_cleaned
            
        return ca_dict
    
    def get_tasks_for_gui(self, username=None, status_filter=None):
        """
        Get tasks using nbstatus shell command
        
        Args:
            username (str): Filter by username (optional)
            status_filter (str): Filter by status (optional)
            
        Returns:
            pandas.DataFrame: DataFrame with all fields
        """
        try:
            print("Fetching task data using nbstatus command...")
            
            # Build command
            cmd = ['nbstatus', 'tasks', '--fields', 'all', '--format', 'csv']
            
            # Add filters if needed
            if username or (status_filter and status_filter != "All Status"):
                filters = []
                if username:
                    filters.append(f"User=='{username}'")
                if status_filter and status_filter != "All Status":
                    filters.append(f"Status=='{status_filter}'")
                
                cmd.extend(['--free', '&&'.join(filters)])
            
            # Execute command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"Error running nbstatus: {result.stderr}")
                return pd.DataFrame()
            
            # Read CSV output into pandas
            df = pd.read_csv(io.StringIO(result.stdout))
            
            print(f"Found {len(df)} tasks")
            
            if len(df) == 0:
                return pd.DataFrame()
            
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
                    print(f"Extracted {len(ca_columns)} custom attributes: {', '.join(ca_columns[:10])}...")
            
            # Keep TaskID as a regular column (don't set as index for GUI compatibility)
            # if 'TaskID' in df.columns:
            #     df = df.set_index('TaskID')
            
            print(f"DataFrame created: {len(df)} rows × {len(df.columns)} columns")
            
            return df
            
        except subprocess.TimeoutExpired:
            print("Error: nbstatus command timed out")
            return pd.DataFrame()
        except Exception as e:
            print(f"Error fetching data: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
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
    
    def get_available_feeders(self, df):
        """Get list of unique feeders from CA_feeder_name"""
        if 'CA_feeder_name' in df.columns:
            feeders = df['CA_feeder_name'].dropna().unique().tolist()
            return sorted(feeders)
        return []


def main():
    """Test the data provider"""
    import os
    
    provider = GUIDataProvider()
    
    # Get username
    username = sys.argv[1] if len(sys.argv) > 1 else None
    
    print("=" * 80)
    print("GUI DATA PROVIDER V2 TEST (Shell Command Based)")
    if username:
        print(f"User: {username}")
    print("=" * 80 + "\n")
    
    # Get data
    df = provider.get_tasks_for_gui(username=username)
    
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
        
        # Show configs and blocks
        configs = provider.get_available_configs(df)
        blocks = provider.get_available_blocks(df)
        statuses = provider.get_available_statuses(df)
        
        print(f"\nUnique Configs: {len(configs)}")
        print(f"Unique Blocks: {len(blocks)}")
        print(f"Unique Statuses: {len(statuses)}")
    else:
        print("\nNo data found")


if __name__ == "__main__":
    main()
