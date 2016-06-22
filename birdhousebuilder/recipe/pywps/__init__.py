# -*- coding: utf-8 -*-

"""Recipe pywps"""

import os
from mako.template import Template

import zc.recipe.deployment
import birdhousebuilder.recipe.conda
from birdhousebuilder.recipe import supervisor, nginx

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
        b_options = buildout['buildout']

        self.name = options.get('name', name)
        self.options['name'] = self.name

        self.logger = logging.getLogger(self.name)
        
        # deployment layout
        self.deployment = zc.recipe.deployment.Install(buildout, "pywps", {
                                                'prefix': self.options['prefix'],
                                                'user': self.options['user'],
                                                'etc-user': self.options['user']})

        self.options['etc-prefix'] = self.deployment.options['etc-prefix']
        self.options['var-prefix'] = self.deployment.options['var-prefix']
        self.options['etc-directory'] = self.deployment.options['etc-directory']
        self.options['lib-directory'] = self.deployment.options['lib-directory']
        self.options['log-directory'] = self.deployment.options['log-directory']
        self.options['cache-directory'] = self.deployment.options['cache-directory']
        self.prefix = self.options['prefix']

        # conda environment
        self.options['env'] = self.options.get('env', '')
        self.options['pkgs'] = self.options.get('pkgs', 'pywps>=3.2.5 gunicorn gevent eventlet')
        self.options['channels'] = self.options.get('channels', 'defaults birdhouse')
        
        self.conda = birdhousebuilder.recipe.conda.Recipe(self.buildout, self.name, {
            'env': self.options['env'],
            'pkgs': self.options['pkgs'],
            'channels': self.options['channels']})
        self.env_path = self.conda.options['env-path']
        self.options['env-path'] = self.options['env_path'] = self.env_path

        # nginx options
        self.options['hostname'] = self.options.get('hostname', 'localhost')
        self.options['http-port'] = self.options['http_port'] = self.options.get('http-port', '8091')
        self.options['https-port'] = self.options['https_port'] =self.options.get('https-port', '28091')
        self.options['output-port'] = self.options['output_port'] = self.options.get('output-port','8090')
        
        # gunicorn options
        self.options['workers'] = options.get('workers', '1')
        self.options['worker-class'] = options.get('worker-class', 'gevent')
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

        # make dirs
        output_path = os.path.join(self.options['lib-directory'], 'outputs', self.name)
        make_dirs(output_path)
        
        tmp_path = os.path.join(self.options['var-prefix'], 'tmp')
        make_dirs(tmp_path)

        mako_path = os.path.join(self.options['var-prefix'], 'cache', 'mako')
        make_dirs(mako_path)

    def install(self, update=False):
        installed = []
        if not update:
            installed += list(self.deployment.install())
        installed += list(self.conda.install(update))
        installed += list(self.install_config())
        installed += list(self.install_app())
        installed += list(self.install_gunicorn())
        installed += list(self.install_supervisor(update))
        installed += list(self.install_nginx_default(update))
        installed += list(self.install_nginx(update))
        return installed

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
            name=self.name,
            prefix=self.prefix,
            env_path=self.env_path,
            bin_dir=self.bin_dir,
            package_dir=self.package_dir,
            workers = self.options['workers'],
            worker_class = self.options['worker-class'],
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
            'default',
            {'prefix': self.options['prefix'],
             'user': self.options['user'],
             'name': 'default',
             'input': os.path.join(os.path.dirname(__file__), "nginx-default.conf"),
             'hostname': self.options.get('hostname'),
             'port': self.options.get('output-port')
             })
        return script.install(update=update)

    def install_nginx(self, update=False):
        """
        install nginx for pywps
        """
        script = nginx.Recipe(
            self.buildout,
            self.name,
            {'name': self.name,
             'prefix': self.options['prefix'],
             'user': self.options['user'],
             'input': os.path.join(os.path.dirname(__file__), "nginx.conf"),
             'hostname': self.options.get('hostname'),
             'http_port': self.options['http-port'],
             'https_port': self.options['https-port'],
             })
        return script.install(update=update)
        
    def update(self):
        return self.install(update=True)
    
def uninstall(name, options):
    pass

