#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
"""TODO"""


import unittest
import logging
from .tests import TestDefaultSection

LOG = logging.getLogger('tests')
LOG.info("loading tests")


def get_all_tests():
    """TODO"""
    loader = unittest.TestLoader()
    suites = unittest.TestSuite()
    suites.addTest(loader.loadTestsFromTestCase(TestDefaultSection))
    return suites

if __name__ == '__main__':
    SUITE = get_all_tests()
    unittest.TextTestRunner(verbosity=2).run(SUITE)
