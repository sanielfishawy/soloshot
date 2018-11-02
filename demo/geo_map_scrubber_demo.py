# pylint: disable=C0413
import sys
import os
sys.path.insert(0, os.getcwd())
from tests.test_geo_map_scrubber import TestGeoMapScrubber

TestGeoMapScrubber().setUp().visualize()
