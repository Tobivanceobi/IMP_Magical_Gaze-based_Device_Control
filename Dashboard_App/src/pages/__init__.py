from .analysis import PageAnalysis
from .gaze_cls import PageGazeCls
from .recorder import PageRecorder
from .object_detection import PageObjectDetection
from ..utils import Page
from typing import Dict, Type


PAGE_MAP: Dict[str, Type[Page]] = {
    PageAnalysis.NAME: PageAnalysis,
    PageGazeCls.NAME: PageGazeCls,
    PageRecorder.NAME: PageRecorder,
    PageObjectDetection.NAME: PageObjectDetection,
}

__all__ = ["PAGE_MAP"]