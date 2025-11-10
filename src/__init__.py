"""
Netbatch Viewer GUI - Modular Components
Author: Shyam Sunder Kushwaha
Email: shyam.sunder.kushwaha@intel.com

This package contains mixin classes for the Netbatch Viewer GUI.
Each mixin provides a specific set of functionality.
"""

from .uicomponents import UIComponentsMixin
from .dataoperations import DataOperationsMixin
from .taskactions import TaskActionsMixin
from .popupwindows import PopupWindowsMixin
from .fileoperations import FileOperationsMixin
from .utils import UtilsMixin

__all__ = [
    'UIComponentsMixin',
    'DataOperationsMixin',
    'TaskActionsMixin',
    'PopupWindowsMixin',
    'FileOperationsMixin',
    'UtilsMixin'
]

__version__ = '2.0.0'
