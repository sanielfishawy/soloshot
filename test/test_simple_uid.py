import sys
sys.path.insert(0, '/Users/sani/dev/soloshot')
import unittest
from simple_uid import SimpleID

class TestSimpleID(unittest.TestCase):
    
    def setUp(self):
        self.prefix = 'foo'
        self.si = SimpleID(prefix=self.prefix)

    def test_simple_id_gets_prefix_and_sequential_ids(self):
        self.assertEqual(self.si.get_id(), 'foo0')
        self.assertEqual(self.si.get_id(), 'foo1')
        self.assertEqual(self.si.get_id(), 'foo2')

if __name__ == '__main__':
    unittest.main()