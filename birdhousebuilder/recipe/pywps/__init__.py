# -*- coding: utf-8 -*-
# Copyright (C)2014 DKRZ GmbH

"""Recipe pywps"""

import os
from mako.template import Template

from birdhousebuilder.recipe import conda, supervisor, nginx

templ_pywps = Template(filename=os.path.join(os.path.dirname(__file__), "pywps.cfg"))
templ_app = Template(filename=os.path.join(os.path.dirname(__file__), "wpsapp.py"))
templ_gunicorn = Template(filename=os.path.join(os.path.dirname(__file__), "gunicorn.conf.py"))
templ_cmd = Template(
    "${prefix}/bin/python ${prefix}/bin/gunicorn wpsapp:app -c ${prefix}/etc/pywps/gunicorn.conf.py")

class Recipe(object):
    """This recipe is used by zc.buildout"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        b_options = buildout['buildout']
        self.anaconda_home = b_options.get('anaconda-home', conda.anaconda_home)

        self.hostname = options.get('hostname', 'localhost')
        self.port = options.get('port', '8091')
        self.processes_path = options.get('processesPath')

    def install(self):
        installed = []
        installed += list(self.install_pywps())
        installed += list(self.install_config())
        installed += list(self.install_app())
        installed += list(self.install_gunicorn())
        installed += list(self.install_program())
        installed += list(self.install_nginx())
        return installed

    def install_pywps(self):
        script = conda.Recipe(
            self.buildout,
            self.name,
            {'pkgs': 'pywps gunicorn'})
        return script.install()
        
    def install_config(self):
        """
        install etc/pywps.cfg
        """
        result = templ_pywps.render(
            prefix=self.anaconda_home,
            hostname=self.hostname,
            port=self.port,
            processesPath=self.processes_path,
            )
        output = os.path.join(self.anaconda_home, 'etc', 'pywps', 'pywps.cfg')
        conda.makedirs(os.path.dirname(output))
                
        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
        return [output]

    def install_gunicorn(self):
        """
        install etc/gunicorn.conf.py
        """
        result = templ_gunicorn.render(
            prefix=self.anaconda_home,
            )
        output = os.path.join(self.anaconda_home, 'etc', 'pywps', 'gunicorn.conf.py')
        conda.makedirs(os.path.dirname(output))
                
        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
        return [output]

    def install_app(self):
        """
        install etc/wpsapp.py
        """
        result = templ_app.render(
            prefix=self.anaconda_home,
            )
        output = os.path.join(self.anaconda_home, 'etc', 'pywps', 'wpsapp.py')
        conda.makedirs(os.path.dirname(output))
                
        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
        return [output]

    def install_program(self):
        """
        install supervisor config for pywps
        """
        script = supervisor.Recipe(
            self.buildout,
            self.name,
            {'program': 'pywps',
             'command': templ_cmd.render(prefix=self.anaconda_home),
             'directory': os.path.join(self.anaconda_home, 'etc', 'pywps')
             })
        return script.install()

    def install_nginx(self):
        """
        install nginx for pywps
        """
        script = nginx.Recipe(
            self.buildout,
            self.name,
            {'input': os.path.join(os.path.dirname(__file__), "nginx.conf"),
             'sites': self.name,
             'prefix': self.anaconda_home,
             'port': self.port,
             })
        return script.install()
        
    def update(self):
        return self.install()

def uninstall(name, options):
    pass

