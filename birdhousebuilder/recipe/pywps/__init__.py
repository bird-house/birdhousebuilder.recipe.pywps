# -*- coding: utf-8 -*-

"""Recipe pywps"""

import os
import pwd
from mako.template import Template

import zc.recipe.deployment
from zc.recipe.deployment import Configuration
from zc.recipe.deployment import make_dir
import birdhousebuilder.recipe.conda
from birdhousebuilder.recipe import supervisor, nginx

import logging

templ_pywps_cfg = Template(filename=os.path.join(os.path.dirname(__file__),
                           "pywps.cfg"))
templ_app = Template(filename=os.path.join(os.path.dirname(__file__),
                     "wpsapp.py"))
templ_gunicorn = Template(filename=os.path.join(os.path.dirname(__file__),
                          "gunicorn.conf_py"))
templ_cmd = Template(
    "${bin_directory}/python ${conda_prefix}/bin/gunicorn ${name}_app:application -c ${prefix}/etc/gunicorn/${name}.py")
# templ_runwps = Template(filename=os.path.join(os.path.dirname(__file__),
#                         "runwps.sh"))


def make_dirs(name, user):
    etc_uid, etc_gid = pwd.getpwnam(user)[2:4]
    created = []
    make_dir(name, etc_uid, etc_gid, 0o755, created)


class Recipe(object):
    """This recipe is used by zc.buildout"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        b_options = buildout['buildout']

        self.name = options.get('name', name)
        self.options['name'] = self.name

        self.logger = logging.getLogger(self.name)

        # deployment layout
        def add_section(section_name, options):
            if section_name in buildout._raw:
                raise KeyError("already in buildout", section_name)
            buildout._raw[section_name] = options
            buildout[section_name]  # cause it to be added to the working parts

        self.prefix = self.options.get('prefix', '')
        if not self.prefix:
            self.prefix = b_options['parts-directory']
        self.options['prefix'] = self.prefix

        user = self.options.get('user', '')
        if not user:
            user = os.environ['USER']
        self.options['user'] = user

        etc_user = self.options.get('etc-user', '')
        if not etc_user:
            etc_user = user
        self.options['etc-user'] = etc_user

        self.deployment_name = self.name + "-pywps-deployment"
        self.deployment = zc.recipe.deployment.Install(buildout, self.deployment_name, {
            'name': "pywps",
            'prefix': self.options['prefix'],
            'user': self.options['user'],
            'etc-user': self.options['etc-user']})
        add_section(self.deployment_name, self.deployment.options)

        self.options['etc-prefix'] = self.deployment.options['etc-prefix']
        self.options['var-prefix'] = self.options['var_prefix'] = self.deployment.options['var-prefix']
        self.options['etc-directory'] = self.deployment.options['etc-directory']
        self.options['lib-directory'] = self.options['lib_directory'] = self.deployment.options['lib-directory']
        self.options['log-directory'] = self.options['log_directory'] = self.deployment.options['log-directory']
        self.options['run-directory'] = self.options['run_directory'] = self.deployment.options['run-directory']
        self.options['cache-directory'] = self.options['cache_directory'] = self.deployment.options['cache-directory']
        self.prefix = self.options['prefix']

        # conda environment
        self.options['env'] = self.options.get('env', '')
        self.options['pkgs'] = self.options.get('pkgs', 'pywps gunicorn gevent')
        self.options['channels'] = self.options.get('channels', 'defaults birdhouse')

        self.conda = birdhousebuilder.recipe.conda.Recipe(self.buildout, self.name, {
            'env': self.options['env'],
            'pkgs': self.options['pkgs'],
            'channels': self.options['channels']})
        self.options['conda-prefix'] = self.options['conda_prefix'] = self.conda.options['prefix']

        # nginx options
        self.options['hostname'] = self.options.get('hostname', 'localhost')
        self.options['http-port'] = self.options['http_port'] = self.options.get('http-port', '8091')
        self.options['https-port'] = self.options['https_port'] = self.options.get('https-port', '28091')
        self.options['output-port'] = self.options['output_port'] = self.options.get('output-port','8090')

        # gunicorn options
        self.options['workers'] = options.get('workers', '1')
        self.options['worker-class'] = self.options['worker_class'] = options.get('worker-class', 'gevent')
        self.options['timeout'] = options.get('timeout', '30')
        self.options['loglevel'] = options.get('loglevel', 'info')

        processes_path = os.path.join(b_options.get('directory'), 'processes')
        self.options['processes_path'] = options.get('processes_path',
                                                     processes_path)

        self.options['title'] = options.get('title', 'PyWPS Server')
        self.options['abstract'] = options.get(
            'abstract', 'See http://pywps.org/')
        self.options['provider_name'] = options.get('provider_name', '')
        self.options['city'] = options.get('city', '')
        self.options['country'] = options.get('country', '')
        self.options['provider_url'] = options.get('provider_url', '')
        self.options['loglevel'] = options.get('loglevel', 'WARN')
        self.options['maxoperations'] = options.get('maxoperations', '30')
        self.options['maxinputparamlength'] = options.get(
            'maxinputparamlength', '1024')
        self.options['maxsingleinputsize'] = options.get(
            'maxsingleinputsize', '30mb')
        self.options['maxrequestsize'] = options.get(
            'maxrequestsize', '30mb')

        self.options['bin-directory'] = self.options['bin_directory'] = b_options.get('bin-directory')
        self.options['directory'] = b_options.get('directory')

        # make dirs
        output_path = os.path.join(
            self.options['lib-directory'], 'outputs', self.name)
        make_dirs(output_path, self.options['user'])

        tmp_path = os.path.join(
            self.options['lib-directory'], 'tmp', self.name)
        make_dirs(tmp_path, self.options['user'])

        cache_path = os.path.join(
            self.options['lib-directory'], 'cache', self.name)
        make_dirs(cache_path, self.options['user'])

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

        # fix permissions for var/run
        os.chmod(os.path.join(self.options['var-prefix'], 'run'), 0o755)

        return installed

    def install_config(self):
        """
        install pywps config in etc/pywps/
        """
        text = templ_pywps_cfg.render(**self.options)
        config = Configuration(self.buildout, self.name + '.cfg', {
            'deployment': self.deployment_name,
            'text': text})
        return [config.install()]

    def install_gunicorn(self):
        """
        install gunicorn config in etc/gunicorn/
        """
        text = templ_gunicorn.render(**self.options)
        config = Configuration(self.buildout, self.name+'.py', {
            'deployment': self.deployment_name,
            'directory': os.path.join(self.options['etc-prefix'], 'gunicorn'),
            'text': text})
        return [config.install()]

    def install_app(self):
        """
        install etc/pywps/my_app.py
        """
        text = templ_app.render(prefix=self.prefix)
        config = Configuration(self.buildout, self.name+'_app.py', {
            'deployment': self.deployment_name,
            'text': text})
        return [config.install()]

    def install_supervisor(self, update=False):
        """
        install supervisor config for pywps
        """
        script = supervisor.Recipe(
            self.buildout,
            self.name,
            {'prefix': self.options.get('prefix'),
             'user': self.options.get('user'),
             'etc-user': self.options.get('etc-user'),
             #'env': 'birdhouse',
             'program': self.name,
             'command': templ_cmd.render(**self.options),
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
             'etc-user': self.options.get('etc-user'),
             #'env': 'birdhouse',
             'name': 'default',
             'input': os.path.join(os.path.dirname(__file__),
                                   "nginx-default.conf"),
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
             'etc-user': self.options.get('etc-user'),
             #'env': 'birdhouse',
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
