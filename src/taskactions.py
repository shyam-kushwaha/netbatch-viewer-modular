#!/usr/intel/pkgs/python3/3.13.2/bin/python3
import UsrIntel.R1

"""
Task Actions - Actions performed on tasks

This file has been refactored. All methods are now in separate files
under the taskactions/ directory for easier maintenance.

Original file backed up as: taskactions.py.backup
"""

# Import the combined TaskActionsMixin from the taskactions module
from taskactions import TaskActionsMixin

# Re-export for backward compatibility
__all__ = ['TaskActionsMixin']
