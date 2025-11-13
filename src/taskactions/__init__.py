"""
Task Actions Module - Split into separate files for easier maintenance
Each file contains one method from the TaskActionsMixin class
"""

# Import all task action methods
from .open_ward import TaskActionsMixin as OpenWardMixin
from .open_nbflow_gui import TaskActionsMixin as OpenNbflowGuiMixin
from .open_report_dir import TaskActionsMixin as OpenReportDirMixin
from .open_stage_csv import TaskActionsMixin as OpenStageCsvMixin
from .open_log_viewer import TaskActionsMixin as OpenLogViewerMixin
from .view_qor_data import TaskActionsMixin as ViewQorDataMixin
from .load_design_for_review import TaskActionsMixin as LoadDesignForReviewMixin
from .run_interactively import TaskActionsMixin as RunInteractivelyMixin
from .open_log import TaskActionsMixin as OpenLogMixin


class TaskActionsMixin(
    OpenWardMixin,
    OpenNbflowGuiMixin,
    OpenReportDirMixin,
    OpenStageCsvMixin,
    OpenLogViewerMixin,
    ViewQorDataMixin,
    LoadDesignForReviewMixin,
    RunInteractivelyMixin,
    OpenLogMixin
):
    """Combined mixin class with all task action methods"""
    pass
