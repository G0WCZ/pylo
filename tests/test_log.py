import unittest
from pylo import Log

class TestLog(unittest.TestCase):

    def test_construct(self):
        log = Log()
        self.assertTrue(isinstance(log, Log))