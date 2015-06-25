# -*- coding: utf-8 -*-

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
        
        self.prefix = self.options.get('prefix', conda.prefix())
        self.options['prefix'] = self.prefix
        
        self.sites = options.get('sites', self.name)
        self.options['sites'] = self.sites
        self.options['hostname'] = options.get('hostname', 'localhost')

        self.options['http_port'] = options.get('http_port', '8091')
        self.options['https_port'] = options.get('https_port', '28091')
        self.options['output_port'] = options.get('output_port','8090')
        
        self.options['user'] = options.get('user', '')
        
        processes_path = os.path.join(b_options.get('directory'), 'processes')
        self.options['processesPath'] = options.get('processesPath', processes_path)

        self.options['title'] = options.get('title', 'PyWPS Server')
        self.options['abstract'] = options.get('abstract', 'See http://pywps.wald.intevation.org and http://www.opengeospatial.org/standards/wps')
        self.options['providerName'] = options.get('providerName', '')
        self.options['city'] = options.get('city', '')
        self.options['country'] = options.get('country', '')
        self.options['providerSite'] = options.get('providerSite', '')
        self.options['logLevel'] = options.get('logLevel', 'WARN')

        self.bin_dir = b_options.get('bin-directory')
        self.package_dir = b_options.get('directory')

    def install(self):
        installed = []
        installed += list(self.install_pywps())
        installed += list(self.install_config())
        installed += list(self.install_app())
        installed += list(self.install_gunicorn())
        installed += list(self.install_supervisor())
        installed += list(self.install_nginx_default())
        installed += list(self.install_nginx())
        return tuple()

    def install_pywps(self, update=False):
        script = conda.Recipe(
            self.buildout,
            self.name,
            {'pkgs': 'pywps gunicorn'})
        
        mypath = os.path.join(self.prefix, 'var', 'lib', 'pywps', 'outputs', self.sites)
        conda.makedirs(mypath)

        # cache path
        mypath = os.path.join(self.prefix, 'var', 'cache', 'pywps')
        conda.makedirs(mypath)

        mypath = os.path.join(self.prefix, 'var', 'tmp')
        conda.makedirs(mypath)

        mypath = os.path.join(self.prefix, 'var', 'log', 'pywps')
        conda.makedirs(mypath)

        mypath = os.path.join(self.prefix, 'var', 'cache', 'mako')
        conda.makedirs(mypath)

        if update == True:
            return script.update()
        else:
            return script.install()
        
    def install_config(self):
        """
        install pywps config in etc/pywps
        """
        result = templ_pywps.render(**self.options)
        output = os.path.join(self.prefix, 'etc', 'pywps', self.sites + '.cfg')
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
            prefix=self.prefix,
            sites=self.sites,
            bin_dir=self.bin_dir,
            package_dir=self.package_dir,
            )
        output = os.path.join(self.prefix, 'etc', 'pywps', 'gunicorn.'+self.sites+'.py')
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
            prefix=self.prefix,
            )
        output = os.path.join(self.prefix, 'etc', 'pywps', 'wpsapp.py')
        conda.makedirs(os.path.dirname(output))
                
        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
        return [output]

    def install_supervisor(self, update=False):
        """
        install supervisor config for pywps
        """
        script = supervisor.Recipe(
            self.buildout,
            self.sites,
            {'user': self.options.get('user'),
             'program': self.sites,
             'command': templ_cmd.render(prefix=self.prefix, bin_dir=self.bin_dir, sites=self.sites),
             'directory': os.path.join(self.prefix, 'etc', 'pywps'),
             'stopwaitsecs': '30',
             'killasgroup': 'true',
             })
        if update == True:
            return script.update()
        else:
            return script.install()

    def install_nginx_default(self, update=False):
        """
        install nginx for pywps outputs
        """
        script = nginx.Recipe(
            self.buildout,
            self.name,
            {'input': os.path.join(os.path.dirname(__file__), "nginx-default.conf"),
             'sites': 'default',
             'user': self.options.get('user'),
             'prefix': self.prefix,
             'hostname': self.options.get('hostname'),
             'port': self.options.get('output_port')
             })
        if update == True:
            return script.update()
        else:
            return script.install()

    def install_nginx(self, update=False):
        """
        install nginx for pywps
        """
        script = nginx.Recipe(
            self.buildout,
            self.name,
            {'input': os.path.join(os.path.dirname(__file__), "nginx.conf"),
             'sites': self.sites,
             'prefix': self.prefix,
             'user': self.options.get('user'),
             'hostname': self.options.get('hostname'),
             'http_port': self.options.get('http_port'),
             'https_port': self.options.get('https_port'),
             'user': self.options.get('user'),
             'group': self.options.get('group')
             })
        if update == True:
            return script.update()
        else:
            return script.install()
        
    def update(self):
        self.install_pywps(update=True)
        self.install_config()
        self.install_app()
        self.install_gunicorn()
        self.install_supervisor(update=True)
        self.install_nginx_default(update=True)
        self.install_nginx(update=True)
        
        return tuple()

def uninstall(name, options):
    pass

