# -*- coding: utf-8 -*-

"""Recipe pywps"""

import os
from mako.template import Template

import zc.recipe.deployment
from birdhousebuilder.recipe import conda, supervisor, nginx

import logging

templ_pywps = Template(filename=os.path.join(os.path.dirname(__file__), "pywps.cfg"))
templ_app = Template(filename=os.path.join(os.path.dirname(__file__), "wpsapp.py"))
templ_gunicorn = Template(filename=os.path.join(os.path.dirname(__file__), "gunicorn.conf_py"))
templ_cmd = Template(
    "${bin_dir}/python ${env_path}/bin/gunicorn wpsapp:application -c ${prefix}/etc/gunicorn/${name}.py")
templ_runwps = Template(filename=os.path.join(os.path.dirname(__file__), "runwps.sh"))

def make_dirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

class Recipe(object):
    """This recipe is used by zc.buildout"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

        self.name = options.get('name', name)
        self.options['name'] = self.name

        self.logger = logging.getLogger(self.name)
        
        b_options = buildout['buildout']

        self.logger.debug("pywps options = %s", self.options)

        deployment = zc.recipe.deployment.Install(buildout, "pywps", {
                                                'prefix': self.options['prefix'],
                                                'user': self.options['user'],
                                                'etc-user': self.options['user']})
        deployment.install()

        self.options['etc-prefix'] = deployment.options['etc-prefix']
        self.options['var-prefix'] = deployment.options['var-prefix']
        self.options['etc-directory'] = deployment.options['etc-directory']
        self.options['lib-directory'] = deployment.options['lib-directory']
        self.options['log-directory'] = deployment.options['log-directory']
        self.options['cache-directory'] = deployment.options['cache-directory']
        self.prefix = self.options['prefix']
        
        self.env_path = conda.conda_env_path(buildout, options)
        self.options['env_path'] = self.env_path
        
        self.options['hostname'] = options.get('hostname', 'localhost')

        # nginx options
        self.options['http_port'] = options.get('http_port', '8091')
        self.options['https_port'] = options.get('https_port', '28091')
        self.options['output_port'] = options.get('output_port','8090')
        
        self.options['user'] = options.get('user', '')

        # gunicorn options
        self.options['workers'] = options.get('workers', '1')
        self.options['worker_class'] = options.get('worker_class', 'gevent')
        self.options['timeout'] = options.get('timeout', '30')
        self.options['loglevel'] = options.get('loglevel', 'info')
        
        processes_path = os.path.join(b_options.get('directory'), 'processes')
        self.options['processesPath'] = options.get('processesPath', processes_path)

        self.options['title'] = options.get('title', 'PyWPS Server')
        self.options['abstract'] = options.get('abstract', 'See http://pywps.wald.intevation.org and http://www.opengeospatial.org/standards/wps')
        self.options['providerName'] = options.get('providerName', '')
        self.options['city'] = options.get('city', '')
        self.options['country'] = options.get('country', '')
        self.options['providerSite'] = options.get('providerSite', '')
        self.options['logLevel'] = options.get('logLevel', 'WARN')
        self.options['maxoperations'] = options.get('maxoperations', '100')
        self.options['maxinputparamlength'] = options.get('maxinputparamlength', '2048')
        self.options['maxfilesize'] = options.get('maxfilesize', '30GB')

        self.bin_dir = b_options.get('bin-directory')
        self.package_dir = b_options.get('directory')

    def install(self, update=False):
        installed = []
        installed += list(self.install_pywps(update))
        installed += list(self.install_config())
        installed += list(self.install_app())
        installed += list(self.install_gunicorn())
        installed += list(self.install_supervisor(update))
        installed += list(self.install_nginx_default(update))
        installed += list(self.install_nginx(update))
        return installed

    def install_pywps(self, update=False):
        script = conda.Recipe(
            self.buildout,
            self.name,
            {'pkgs': 'pywps>=3.2.5 gunicorn gevent eventlet',
             'channels': 'birdhouse'})

        # make dirs
        output_path = os.path.join(self.options['lib-directory'], 'outputs', self.name)
        make_dirs(output_path)
        
        tmp_path = os.path.join(self.options['var-prefix'], 'tmp')
        make_dirs(tmp_path)

        mako_path = os.path.join(self.options['var-prefix'], 'cache', 'mako')
        make_dirs(mako_path)

        return script.install(update)
        
    def install_config(self):
        """
        install pywps config in etc/pywps
        """
        text = templ_pywps.render(**self.options)
        conf_path = os.path.join(self.options['etc-directory'], self.name + '.cfg')

        with open(conf_path, 'wt') as fp:
            fp.write(text)
        return [conf_path]

    def install_gunicorn(self):
        """
        install etc/gunicorn.conf.py
        """
        text = templ_gunicorn.render(
            prefix=self.prefix,
            env_path=self.env_path,
            name=self.name,
            bin_dir=self.bin_dir,
            package_dir=self.package_dir,
            workers = self.options['workers'],
            worker_class = self.options['worker_class'],
            timeout = self.options['timeout'],
            loglevel = self.options['loglevel'],
            )
        conf_path = os.path.join(self.options['etc-prefix'], 'gunicorn', self.name+'.py')
        make_dirs(os.path.dirname(conf_path))
                
        with open(conf_path, 'wt') as fp:
            fp.write(text)
        return [conf_path]

    def install_app(self):
        """
        install etc/wpsapp.py
        """
        text = templ_app.render(prefix=self.prefix)
        conf_path = os.path.join(self.options['etc-directory'], 'wpsapp.py')

        with open(conf_path, 'wt') as fp:
            fp.write(text)
        return [conf_path]

    def install_supervisor(self, update=False):
        """
        install supervisor config for pywps
        """
        script = supervisor.Recipe(
            self.buildout,
            self.name,
            {'prefix': self.options.get('prefix'),
             'user': self.options.get('user'),
             'program': self.name,
             'command': templ_cmd.render(prefix=self.prefix, bin_dir=self.bin_dir, env_path=self.env_path, name=self.name),
             'directory': self.options['etc-directory'],
             'stopwaitsecs': '30',
             'killasgroup': 'true',
             })
        return script.install(update=update)

    def install_nginx_default(self, update=False):
        """
        install nginx for pywps outputs
        """
        script = nginx.Recipe(
            self.buildout,
            'pywps',
            {'prefix': self.options['prefix'],
             'user': self.options['user'],
             'name': 'default',
             'input': os.path.join(os.path.dirname(__file__), "nginx-default.conf"),
             'hostname': self.options.get('hostname'),
             'port': self.options.get('output_port')
             })
        return script.install(update=update)

    def install_nginx(self, update=False):
        """
        install nginx for pywps
        """
        script = nginx.Recipe(
            self.buildout,
            self.name,
            {'prefix': self.options['prefix'],
             'user': self.options['user'],
             'name': self.name,
             'input': os.path.join(os.path.dirname(__file__), "nginx.conf"),
             'hostname': self.options.get('hostname'),
             'http_port': self.options.get('http_port'),
             'https_port': self.options.get('https_port'),
             'group': self.options.get('group')
             })
        return script.install(update=update)
        
    def update(self):
        return self.install(update=True)
    
def uninstall(name, options):
    pass

