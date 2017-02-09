# -*- coding: utf-8 -*-
import unittest

import zc.buildout


class UtilsTestCase(unittest.TestCase):

    def test_extra_options(self):
        from birdhousebuilder.recipe.pywps import parse_extra_options
        # all in one line
        extra_options = parse_extra_options("esmval_root=/path/to/esmval archive_root=/path/to/archive")
        assert extra_options['esmval_root'] == "/path/to/esmval"
        assert extra_options['archive_root'] == "/path/to/archive"
        # multiple lines
        extra_options = parse_extra_options("""
            esmval_root=/path/to/esmval
            archive_root=/path/to/archive
            """)
        assert extra_options['esmval_root'] == "/path/to/esmval"
        assert extra_options['archive_root'] == "/path/to/archive"
        # with spaces ... not working yet
        with self.assertRaises(zc.buildout.UserError):
            parse_extra_options("""
                    esmval_root = /path/to/esmval
                    archive_root  =  /path/to/archive
                    """)


