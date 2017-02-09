# -*- coding: utf-8 -*-
import unittest


class UtilsTestCase(unittest.TestCase):

    def test_extra_options(self):
        from birdhousebuilder.recipe.pywps import parse_extra_options
        parse_extra_options()


