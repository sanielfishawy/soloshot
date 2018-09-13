import sys, unittest, math
sys.path.insert(0, '/Users/sani/dev/soloshot')
from shapely.geometry import Point, LineString

class TestShapely(unittest.TestCase):

    def setUp(self):
        pass

    def test_circles_approximation(self):
        c1 = Point((0,0)).buffer(1, resolution=10000).exterior #pylint: disable=no-member
        c2 = Point((1,0)).buffer(1, resolution=10000).exterior #pylint: disable=no-member

        self.assertTrue(c1.intersects(c2))

        m = c1.intersection(c2)
        l = LineString(m)

        self.assertAlmostEqual(l.length, 2*math.sin(math.pi/3))

    def test_circles_segments(self):
        c1 = Point((0,0)).buffer(1, resolution=10000)
        c2 = Point((1,0)).buffer(1, resolution=10000).exterior #pylint: disable=no-member
        i = c1.intersection(c2)
        self.assertAlmostEqual(i.length, 2*math.pi/3)

if __name__ == '__main__':
    unittest.main()