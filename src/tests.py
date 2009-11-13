#!/usr/bin/python3

import unittest
import programs
from oosh import Droplet

class TestPrograms(unittest.TestCase):
    # all programs return a list of Droplets
    def test_echo(self):
        expected = [Droplet({'a':'a value', 'b':'b value'})]
        actual = programs.do_echo('"a":"a value" "b":"b value"', [])
        self.compare_droplets(expected, actual)

    def compare_droplets(self, x, y):
        for i in range(len(x)):
            for j in range(len(y)):
                self.assertEqual(x[i].entries, y[i].entries)

if __name__ == '__main__':
    unittest.main()
