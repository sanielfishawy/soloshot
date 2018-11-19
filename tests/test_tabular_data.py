# pylint: disable=C0413
import sys
import os
import unittest

sys.path.insert(0, os.getcwd())
from tk_canvas_renderers.tabular_data import TabularData

class TestTabularData(unittest.TestCase):

    def setUp(self):
        pass

    def dont_test_visualize(self):
        data = [
            {
                TabularData.LABEL: 'col0 row0',
                TabularData.VALUE: 0,
            },
            {
                TabularData.LABEL: 'col0 row1',
                TabularData.VALUE: 1,
            },
            {
                TabularData.LABEL: 'col2 row0',
                TabularData.COLUMN: 2,
                TabularData.VALUE: 2,
            },
            {
                TabularData.LABEL: 'col1 row0',
                TabularData.COLUMN: 1,
                TabularData.VALUE: 3,
            },
            {
                TabularData.LABEL: 'col0 row3',
                TabularData.VALUE: 4,
            },
            {
                TabularData.LABEL: 'col0 row4',
                TabularData.VALUE: 5,
            },
        ]
        tabular_data = TabularData(data=data)
        tabular_data.run()


if __name__ == '__main__':
    unittest.main()
