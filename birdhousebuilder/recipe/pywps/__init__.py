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
    "${bin_dir}/python ${prefix}/bin/gunicorn wpsapp:app -c ${prefix}/etc/pywps/gunicorn.${sites}.py")

class Recipe(object):
    """This recipe is used by zc.buildout"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        b_options = buildout['buildout']
        
        self.anaconda_home = b_options.get('anaconda-home', conda.anaconda_home)
        
        self.options['sites'] = options.get('sites', self.name)
        self.options['prefix'] = self.anaconda_home
        self.options['hostname'] = options.get('hostname', 'localhost')

        self.port = options.get('port', '8091')
        self.options['port'] = self.port
        
        processes_path = os.path.join(b_options.get('directory'), 'processes')
        self.options['processesPath'] = options.get('processesPath', processes_path)

        self.options['abstract'] = options.get('abstract', 'See http://pywps.wald.intevation.org and http://www.opengeospatial.org/standards/wps')
        self.options['providerName'] = options.get('providerName', '')
        self.options['city'] = options.get('city', '')
        self.options['country'] = options.get('country', '')
        self.options['providerSite'] = options.get('providerSite', '')
        self.options['logLevel'] = options.get('logLevel', 'DEBUG')

        self.bin_dir = b_options.get('bin-directory')

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
        install pywps config in etc/pywps
        """
        result = templ_pywps.render(**self.options)
        output = os.path.join(self.anaconda_home, 'etc', 'pywps', self.name + '.cfg')
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
            sites=self.name,
            bin_dir=self.bin_dir,
            )
        output = os.path.join(self.anaconda_home, 'etc', 'pywps', 'gunicorn.'+self.name+'.py')
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
            {'program': self.name,
             'command': templ_cmd.render(prefix=self.anaconda_home, bin_dir=self.bin_dir, sites=self.name),
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

