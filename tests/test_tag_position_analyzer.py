import sys, unittest, math
sys.path.insert(0, '/Users/sani/dev/soloshot')
import geometry_utils as GU
from tag_position_analyzer import TagPositionAnalyzer
from camera import Camera
from viewable_object import ViewableObject


class TestTagPositionAnalyzer(unittest.TestCase):

    def setUp(self):
        self.num_timestamps = 64
        self.camera_pos = (100,100)
        self.camera = Camera()
        self.camera.set_gps_position(self.camera_pos)

        self.vo = ViewableObject(num_timestamps=self.num_timestamps)

        self.angles = [n * math.pi / 32 for n in range (self.num_timestamps)]
        self.positions = [GU.point_with_angle_and_distance_from_point(self.camera_pos, angle, 100) for angle in self.angles]
        
        self.tag_position_analyzer = TagPositionAnalyzer(self.vo, self.camera)

        for timestamp, pos in enumerate(self.positions):
            self.vo.set_position_at_timestamp(pos, timestamp)

    def test_range_of_angles_between_timestamps(self):
        for i in range(40):
            self.assertAlmostEqual(self.tag_position_analyzer._range_of_angles_between_timestamps(i,i+1), math.pi/32)
            self.assertAlmostEqual(self.tag_position_analyzer._range_of_angles_between_timestamps(i,i+2), 2 * math.pi/32)
            self.assertAlmostEqual(self.tag_position_analyzer._range_of_angles_between_timestamps(i,i+3), 3 * math.pi/32)
        
    def test_first_time_after_timestamp_where_range_exceeds_threshold(self):
        t = self.tag_position_analyzer._first_time_after_timestamp_where_range_of_angles_exceeds_threshold(0, math.pi/32 - 0.01)
        self.assertEqual(t, 1)
    
    def test_range_of_angles_in_frame_just_exeeds_threshold(self):
        for n in range(2, 6):
            frames = self.tag_position_analyzer.get_frames_where_range_exceeds_threshold((n * math.pi / 32) - .01)
            for frame in frames:
                if frame['frame'][1] != None:
                    self.assertEqual(n, frame['frame'][1]-frame['frame'][0])
    
    def test_min_and_max_positions_in_frame(self):
        for n in range(2,6):
            frames = self.tag_position_analyzer.get_frames_where_range_exceeds_threshold((n * math.pi / 32) -.01)
            for frame in frames:
                if frame['frame'][1] != None:
                    self.assertEqual(frame['timestamp_of_min_angle'], frame['frame'][0])
                    self.assertEqual(frame['timestamp_of_max_angle'], frame['frame'][1])

if __name__ == '__main__':
    unittest.main()