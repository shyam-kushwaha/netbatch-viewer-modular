# Task Actions Module - Refactored Structure

## Overview
The `TaskActionsMixin` class has been split into separate files for easier maintenance. Each method is now in its own file.

## Directory Structure
```
src/taskactions/
├── __init__.py                    # Combines all methods using multiple inheritance
├── open_ward.py                   # Opens ward directory
├── open_nbflow_gui.py             # Opens NBFlow GUI
├── open_report_dir.py             # Opens report directory
├── open_stage_csv.py              # Opens stage CSV
├── open_log_viewer.py             # Opens log viewer
├── view_qor_data.py               # Views QoR data with HTTP server
├── load_design_for_review.py      # Design review entry point
├── _show_load_design_popup.py     # NetBatch parameters popup (largest file)
├── run_interactively.py           # Runs task interactively
└── open_log.py                    # Opens log file in gvim
```

## Usage

### Importing (No Changes Required)
```python
# Same as before - imports work automatically
from src.taskactions import TaskActionsMixin
```

### Modifying a Method
1. Find the method file in `src/taskactions/`
2. Edit only that specific file
3. Changes won't affect other methods
4. Test: `python3 -m py_compile <filename>.py`

### Example: Modifying open_ward
```bash
# Edit only the specific file
vim src/taskactions/open_ward.py

# Test syntax
python3 -m py_compile src/taskactions/open_ward.py

# Test import
python3 -c "from taskactions import TaskActionsMixin; print('OK')"
```

## Benefits

### ✓ Easy Navigation
- Find methods quickly by filename
- No scrolling through 700+ lines

### ✓ Independent Modification
- Change one method without touching others
- Reduce merge conflicts in version control

### ✓ Cleaner Git Diffs
- Changes show in individual files
- Easier to review pull requests

### ✓ Better Organization
- Each file is 1-15KB (was 35KB total)
- Related code grouped together

## File Sizes
| File | Size | Lines |
|------|------|-------|
| _show_load_design_popup.py | 15KB | 269 |
| view_qor_data.py | 4.2KB | 88 |
| open_log.py | 3.8KB | 69 |
| open_log_viewer.py | 3.5KB | 64 |
| open_nbflow_gui.py | 3.0KB | 45 |
| run_interactively.py | 2.9KB | 49 |
| open_stage_csv.py | 2.6KB | 35 |
| open_report_dir.py | 2.4KB | 32 |
| open_ward.py | 1.9KB | 26 |
| load_design_for_review.py | 1.2KB | 16 |

## Backup & Restore

### Backup Location
`src/taskactions.py.backup` - Original 722-line file

### To Restore Original
```bash
cd src
cp taskactions.py.backup taskactions.py
rm -rf taskactions/
```

## Technical Details

### How It Works
1. Each file defines `TaskActionsMixin` with one method
2. `__init__.py` imports all classes with aliases
3. Creates combined class using multiple inheritance
4. `taskactions.py` re-exports for backward compatibility

### Multiple Inheritance Chain
```python
class TaskActionsMixin(
    OpenWardMixin,
    OpenNbflowGuiMixin,
    OpenReportDirMixin,
    # ... all other mixins
):
    pass
```

## Testing

### Verify All Files
```bash
cd src/taskactions
python3 << 'PYEOF'
import py_compile
import os

for f in [f for f in os.listdir('.') if f.endswith('.py')]:
    py_compile.compile(f, doraise=True)
    print(f"✓ {f}")
PYEOF
```

### Test Import
```bash
cd src
python3 -c "from taskactions import TaskActionsMixin; \
            print('Methods:', len([m for m in dir(TaskActionsMixin) if not m.startswith('_')]))"
```

## Contributing

When adding new methods:
1. Create new file: `src/taskactions/new_method.py`
2. Define class with single method:
   ```python
   class TaskActionsMixin:
       def new_method(self, task):
           # implementation
   ```
3. Add import to `__init__.py`:
   ```python
   from .new_method import TaskActionsMixin as NewMethodMixin
   ```
4. Add to inheritance list in `__init__.py`
5. Test syntax and imports

## Questions?
See `REFACTORING_SUMMARY.txt` for detailed refactoring information.

---

## Recent Updates

### open_ward.py - November 12, 2025
**Enhancement**: Added automatic setup file sourcing when opening ward terminal.

**Changes**:
- Simplified to search for single setup file pattern: `{block}_apr_fc_preFlowEnvDump.csh`
- Search location: `{wardarea}/setup/{block}_apr_fc_preFlowEnvDump.csh`
- Displays setup file path in xterm before sourcing
- Shows success message after sourcing
- Falls back to opening ward without setup if file not found

**Behavior**:
- If setup file found: Sources it automatically and displays confirmation
- If setup file not found: Opens ward terminal without sourcing (with warning in log)

**Task Attributes Used**:
- `CA_ward` - Ward area directory path
- `CA_block` - Partition/block name (used to locate setup file)

**Example**:
If task has `CA_block` = "parts" and `CA_ward` = "/path/to/ward"
- Searches for: `/path/to/ward/setup/parts_apr_fc_preFlowEnvDump.csh`
