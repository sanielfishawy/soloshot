# pylint: disable=C0413
import sys
import os
sys.path.insert(0, os.getcwd())
from tests.test_scrubber import TestScrubber
from tk_canvas_renderers.scrub_picker import ScrubPicker

# TestScrubber().setUp(selector_type=ScrubPicker.SELECT_SINGLE_IMAGE).visualize()
TestScrubber().setUp(selector_type=ScrubPicker.SELECT_RANGE).visualize()
