# Netbatch Viewer GUI - Modular Edition

A modular, maintainable Tkinter-based GUI for viewing and managing Netbatch tasks with real-time monitoring capabilities.

## �� Features

- **Real-time Task Monitoring**: Live data updates from Netbatch API
- **Smart Filtering**: Cascading filters (Feeder → Config → Block)
- **Task Management**: Ward terminal, NBflow GUI, log viewing, QOR reports
- **Job Details**: Multi-tab detailed view with status, technical data, and raw XML
- **Data Export**: CSV export functionality
- **Auto-refresh**: Configurable automatic data refresh
- **Modular Architecture**: Clean, organized codebase using mixin pattern

## 📁 Project Structure

```
netbatch_viewer_modular/
├── netbatch_viewer_gui.py          # Main application (124 lines)
├── gui_data_provider.py            # Data provider module (199 lines)
├── src/                            # Mixin modules directory
│   ├── __init__.py                 # Package initialization
│   ├── uicomponents.py             # UI setup (6 functions, 200 lines)
│   ├── dataoperations.py           # Data operations (12 functions, 434 lines)
│   ├── taskactions.py              # Task actions (8 functions, 454 lines)
│   ├── popupwindows.py             # Popup windows (8 functions, 542 lines)
│   ├── fileoperations.py           # File operations (2 functions, 53 lines)
│   └── utils.py                    # Utilities (8 functions, 110 lines)
└── README.md                       # This file

Total: 1,943 lines of organized, maintainable code
```

## 🏗️ Architecture

### Mixin Pattern
The application uses **multiple inheritance** with mixin classes to organize functionality while maintaining shared state:

```python
class NetbatchViewerGUI(
    UIComponentsMixin,
    DataOperationsMixin,
    TaskActionsMixin,
    PopupWindowsMixin,
    FileOperationsMixin,
    UtilsMixin
):
    def __init__(self, root: tk.Tk):
        # All mixin methods automatically available
        # Shared state (self.df, self.tree, self.filters, etc.)
```

### Module Responsibilities

#### 1. **UIComponentsMixin** (`src/uicomponents.py`)
Handles all GUI setup and widget creation:
- `setup_window()` - Configure main window properties
- `create_menu()` - Create menu bar with File/View/Tools/Help
- `create_toolbar()` - Create toolbar with filter dropdowns
- `create_main_area()` - Create main content area with notebook
- `create_status_bar()` - Create bottom status bar
- `create_tasks_tab()` - Create tasks table with columns

#### 2. **DataOperationsMixin** (`src/dataoperations.py`)
Manages all data loading, processing, and filtering:
- `load_file()` - Load XML files
- `load_live_data()` - Fetch live data from Netbatch API
- `process_loaded_data()` - Process and prepare DataFrame
- `_apply_smart_status_logic()` - Intelligent status determination
- `update_filter_dropdowns()` - Update filter options dynamically
- `on_feeder_changed()` - Handle feeder filter changes
- `on_config_changed()` - Handle config filter changes
- `on_block_changed()` - Handle block filter changes
- `apply_filters()` - Apply all active filters
- `populate_table()` - Populate table with filtered data
- `sort_column()` - Sort table by column header

#### 3. **TaskActionsMixin** (`src/taskactions.py`)
Implements all task-related actions:
- `open_ward()` - Launch Ward terminal
- `open_nbflow_gui()` - Launch NBflow GUI
- `open_report_dir()` - Open report directory in file browser
- `open_stage_csv()` - Open stage CSV file
- `open_log_viewer()` - Open log viewer utility
- `view_qor_data()` - View QOR data report
- `open_ndm()` - Open NDM interface
- `open_log()` - Open task log file

#### 4. **PopupWindowsMixin** (`src/popupwindows.py`)
Creates all dialog windows and popups:
- `show_job_details()` - Show comprehensive job details dialog
- `_populate_status_tab()` - Populate status information tab
- `_populate_technical_tab()` - Populate technical details tab
- `_populate_custom_tab()` - Populate custom attributes tab
- `_populate_raw_tab()` - Populate raw XML data tab
- `show_task_details()` - Show quick task details popup
- `show_csv_viewer()` - Show CSV viewer window
- `show_about()` - Show about dialog

#### 5. **FileOperationsMixin** (`src/fileoperations.py`)
Handles file operations:
- `export_to_csv()` - Export current view to CSV
- `sort_csv_column()` - Sort CSV viewer columns

#### 6. **UtilsMixin** (`src/utils.py`)
Provides utility functions:
- `clear_filters()` - Clear all active filters
- `refresh_view()` - Refresh current data view
- `update_status()` - Update status bar message
- `on_refresh_interval_changed()` - Handle auto-refresh changes
- `parse_interval()` - Parse refresh interval string
- `start_auto_refresh()` - Start auto-refresh timer
- `stop_auto_refresh()` - Stop auto-refresh timer
- `auto_refresh_callback()` - Auto-refresh callback

## 🚀 Getting Started

### Prerequisites

```bash
python3 >= 3.8
tkinter (usually comes with Python)
pandas
```

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd netbatch_viewer_modular

# Install dependencies (if needed)
pip3 install pandas
```

### Running the Application

```bash
python3 netbatch_viewer_gui.py
```

## 🎯 Usage

### Loading Data

1. **Load from File**: `File → Load from File` (Ctrl+O)
2. **Load Live Data**: `File → Load Live Data` (Ctrl+L)

### Filtering Data

Use the toolbar dropdowns to filter by:
- **Feeder**: Top-level hierarchy
- **Config**: Configuration within feeder
- **Block**: Block within config
- **Status**: Task status (Passed, Failed, Running, etc.)

Filters cascade automatically (selecting Feeder updates Config options, etc.)

### Task Actions

Right-click on any task or use toolbar buttons:
- **Ward**: Open Ward terminal for task
- **NBflow GUI**: Launch NBflow GUI
- **Report Dir**: Open report directory
- **Log**: View task log file
- **QOR Data**: View quality-of-results report

### Auto-refresh

Set automatic data refresh interval:
- `View → Auto-refresh` or use toolbar dropdown
- Options: Off, 30s, 1m, 5m, 10m, 30m

## 🛠️ Development

### Adding New Features

1. **Choose appropriate mixin** based on functionality
2. **Add method to mixin class**
3. **Method automatically available** in main GUI class

Example - Adding a new task action:

```python
# In src/taskactions.py
class TaskActionsMixin:
    def open_new_tool(self):
        """Open a new tool for selected task"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a task")
            return
        
        # Your implementation here
```

### Creating a New Mixin

```python
# In src/newmixin.py
import tkinter as tk
from tkinter import ttk

class NewMixin:
    """Description of mixin purpose"""
    
    def new_method(self):
        """Method description"""
        # Implementation
```

Update `src/__init__.py`:
```python
from .newmixin import NewMixin
__all__ = [..., 'NewMixin']
```

Update main class inheritance:
```python
class NetbatchViewerGUI(..., NewMixin):
    pass
```

## 📊 Code Metrics

- **Total Lines**: 1,943 across 8 files
- **Main File**: 124 lines (vs 1,616 monolithic)
- **Reduction**: 92% in main file
- **Functions**: 45 total, logically organized
- **Average Module Size**: 270 lines
- **Largest Module**: popupwindows.py (542 lines)
- **Smallest Module**: fileoperations.py (53 lines)

## 🔍 Benefits of Modular Architecture

1. **Better Organization**: Functions grouped by purpose
2. **Easier Maintenance**: Smaller, focused files
3. **Improved Readability**: Clear separation of concerns
4. **Easier Testing**: Individual mixins can be tested
5. **Flexible**: Easy to add/remove functionality
6. **Shared State**: All mixins access same GUI state via `self`
7. **Scalable**: Add new features without bloating main file

## 📝 Version History

- **v2.0.0** (Nov 2024) - Modular mixin-based architecture
- **v1.0.0** - Original monolithic version

## 🤝 Contributing

When contributing:
1. Follow existing code style
2. Add functions to appropriate mixin
3. Update documentation
4. Test thoroughly before committing

## 👤 Author

**Shyam Sunder Kushwaha**  
Email: shyam.sunder.kushwaha@intel.com

## 📜 License

Intel Internal Use

## 🐛 Known Issues

None currently. Report issues via email.

## 📚 Additional Documentation

- See inline code comments for detailed explanations
- Each mixin has comprehensive docstrings
- Module-level documentation in `src/__init__.py`

---

**Note**: This modular version maintains 100% feature parity with the original monolithic version while providing significantly better code organization and maintainability.
