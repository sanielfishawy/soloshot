#  pylint: disable=C0413
import sys
import os
import numpy as np
import numpy_extensions.numpy_ndarray_extensions # pylint: disable=W0611

sys.path.insert(0, os.getcwd())
from tag import Tag
from base import Base
from legacy_data_pipeline.stable_fov_segmenter import StableFovSegmenter
from tag_position_analyzer import TagPositionAnalyzer


class TagPositionInStableFovSegmentsAnalyzer:
    '''
    Uses StableFovSegmenter to find stable fov segments.
    Uses TagPositionAnalyser to get candidate frames with gps subtended
    angle to base greater than threshold.
    '''

    SEGMENT_START_TAG_IDX = 'segment_start_tag_idx'
    SEGMENT_END_TAG_IDX = 'segment_end_tag_idx'
    FRAME_CONTAINED_IN_STABLE_FOV_SEGMENT = 'frame_contained_in_stable_fov_segment'

    def __init__(
            self,
            fov_series: np.ndarray,
            fov_time_series: np.ndarray,
            tag: Tag,
            base: Base,
    ):
        self._fov_series = fov_series
        self._fov_time_series = fov_time_series
        self._tag = tag
        self._base = base

        # helpers
        self._tag_position_analyser = TagPositionAnalyzer(
            tag=self._tag,
            camera=self._base,
        )

        # lazy inits
        self._stable_fov_segments = None
        self._tag_for_entire_span = None
        self._tag_idxs_for_stable_segments = None
        self._frames = None
        self._frames_marked_stable = None

    def _get_stable_fov_segments(self):
        if self._stable_fov_segments is None:
            self._stable_fov_segments = StableFovSegmenter(
                fov_series=self._fov_series,
                fov_time_series=self._fov_time_series,
            ).get_stable_segments()
        return self._stable_fov_segments

    # Fov time returned in stable_segments is assumed to be guardbanded in video time
    def _get_tag_idx_after_fov_time(self, fov_time):
        return self._tag.get_idx_after_video_time(fov_time)

    # Fov time returned in stable_segments is assumed to be guardbanded in video time
    def _get_tag_idx_before_fov_time(self, fov_time):
        return self._tag.get_idx_before_video_time(fov_time)

    def _get_tag_idxs_for_stable_segments(self):
        if self._tag_idxs_for_stable_segments is None:
            self._tag_idxs_for_stable_segments = []
            for stable_segment in self._get_stable_fov_segments():
                if not stable_segment[StableFovSegmenter.TOO_SHORT]:
                    self._tag_idxs_for_stable_segments.append(
                        self._get_tag_idxs_for_stable_segment(stable_segment)
                    )
        return self._tag_idxs_for_stable_segments

    def _get_tag_idxs_for_stable_segment(self, stable_segment):
        start_fov_time = stable_segment[StableFovSegmenter.START_GUARDED_FOV_TIME]
        end_fov_time = stable_segment[StableFovSegmenter.END_GUARDED_FOV_TIME]
        return {
            self.__class__.SEGMENT_START_TAG_IDX: self._get_tag_idx_after_fov_time(start_fov_time),
            self.__class__.SEGMENT_END_TAG_IDX: self._get_tag_idx_before_fov_time(end_fov_time),
        }

    def _get_complete_frames(self, angle_threshold_rad):
        return self._tag_position_analyser.get_complete_frames_where_range_exceeds_threshold(angle_threshold_rad) # pylint: disable=C0301

    def _get_frames_marked_with_contained_in_stable_fov(self, angle_threshold_rad):
        frames = self._get_complete_frames(angle_threshold_rad)
        for frame in frames:
            frame[self.__class__.FRAME_CONTAINED_IN_STABLE_FOV_SEGMENT] = self._is_frame_contained_in_stable_segment(frame) # pylint: disable=C0301
        return frames

    def _is_frame_contained_in_stable_segment(self, frame):
        early_idx = self._tag_position_analyser.get_early_min_max_timestamp(frame)
        late_idx = self._tag_position_analyser.get_late_min_max_timestamp(frame)
        for segment in self._get_tag_idxs_for_stable_segments():
            start_idx = segment[self.__class__.SEGMENT_START_TAG_IDX]
            end_idx = segment[self.__class__.SEGMENT_END_TAG_IDX]
            if early_idx >= start_idx and early_idx <= end_idx and \
               late_idx >= start_idx and late_idx <= end_idx:
                return True
        return False

    def get_frames_in_stable_fovs(self, angle_threshold_rad):
        return [
            frame
            for frame
            in self._get_frames_marked_with_contained_in_stable_fov(angle_threshold_rad)
            if frame[self.__class__.FRAME_CONTAINED_IN_STABLE_FOV_SEGMENT]
        ]
