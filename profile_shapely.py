from shapely.geometry import Polygon, Point, LineString
import random
import cProfile, pstats, io 

pr = cProfile.Profile()

poly = Polygon([(0,0), (100,0), (100,100), (0,100)])
print(poly)

def random_point():
    x = random.random() * 200
    y = random.random() * 200

    return Point(x,y)


def test_contains(p):
    return poly.contains(p)

def run_test(n):
    for _ in range(0,n):
        test_contains(random_point())
        LineString([random_point(), random_point()])

pr.enable()
run_test(1000)
pr.disable()

s = io.StringIO()
sortby = 'cumulative'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print(s.getvalue())
