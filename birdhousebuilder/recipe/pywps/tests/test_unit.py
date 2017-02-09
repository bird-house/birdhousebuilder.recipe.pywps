# -*- coding: utf-8 -*-
import unittest


class UtilsTestCase(unittest.TestCase):

    def test_extra_options(self):
        from birdhousebuilder.recipe.pywps import parse_extra_options
        extra_options = parse_extra_options("esmval_root=/path/to/esmval archive_root=/path/to/archive")
        assert extra_options['esmval_root'] == "/path/to/esmval"
        assert extra_options['archive_root'] == "/path/to/archive"


