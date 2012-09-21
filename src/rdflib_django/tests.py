"""
Unittests and doctests for the rdflib_django app.
"""
import doctest
from django.utils import unittest
import rdflib_django
from rdflib_django import store, tests_store


def suite():
    """
    Generate the test suite.
    """
    s = unittest.TestSuite()
    s.addTest(doctest.DocTestSuite(rdflib_django))
    s.addTest(doctest.DocTestSuite(store))
    s.addTest(unittest.findTestCases(tests_store))
#    s.addTest(unittest.findTestCases(tests_rdflib))
    return s
