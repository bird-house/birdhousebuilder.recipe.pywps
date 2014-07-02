# -*- coding: utf-8 -*-
# Copyright (C)2014 DKRZ GmbH

"""Recipe pywps"""

import os
from mako.template import Template

from birdhousebuilder.recipe import conda

templ_start_stop = Template(filename=os.path.join(os.path.dirname(__file__), "supervisord"))

class Recipe(object):
    """This recipe is used by zc.buildout"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        b_options = buildout['buildout']
        self.anaconda_home = b_options.get('anaconda-home', conda.anaconda_home)
        bin_path = os.path.join(self.anaconda_home, 'bin')
        lib_path = os.path.join(self.anaconda_home, 'lib')
        self.conda_channels = b_options.get('conda-channels')

        self.host = b_options.get('supervisor-host', 'localhost')
        self.port = b_options.get('supervisor-port', '9001')
        
        self.program = options.get('program', name)

    def install(self):
        installed = []
        installed += list(self.install_supervisor())
        installed += list(self.install_config())
        return installed

    def install_supervisor(self):
        script = conda.Recipe(
            self.buildout,
            self.name,
            {'pkgs': 'supervisor'})
        return script.install()
        
    def install_config(self):
        """
        install supervisor main config file
        """
        result = templ_config.render(
            prefix=self.anaconda_home,
            host=self.host,
            port=self.port)

        output = os.path.join(self.anaconda_home, 'etc', 'supervisor', 'supervisord.conf')
        conda.makedirs(os.path.dirname(output))
                
        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
        return [output]
        
    def update(self):
        return self.install()

def uninstall(name, options):
    pass

