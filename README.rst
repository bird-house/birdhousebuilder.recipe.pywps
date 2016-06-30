*****************************
birdhousebuilder.recipe.pywps
*****************************

.. image:: https://travis-ci.org/bird-house/birdhousebuilder.recipe.pywps.svg?branch=master
   :target: https://travis-ci.org/bird-house/birdhousebuilder.recipe.pywps
   :alt: Travis Build

Introduction
************

``birdhousebuilder.recipe.pywps`` is a `Buildout`_ recipe to install and configure `PyWPS`_ with `Anaconda`_. `PyWPS`_ is a Python implementation of a `Web Processing Service`_ (WPS). ``PyWPS`` will be deployed as a `Supervisor`_ service and is available behind a `Nginx`_ web server. 
This recipe is used by the `Birdhouse`_ project. 

.. _`Buildout`: http://buildout.org/
.. _`Anaconda`: http://continuum.io/
.. _`Supervisor`: http://supervisord.org/
.. _`Nginx`: http://nginx.org/
.. _`PyWPS`: https://github.com/geopython/PyWPS
.. _`Web Processing Service`: https://en.wikipedia.org/wiki/Web_Processing_Service
.. _`Birdhouse`: http://bird-house.github.io/


Usage
*****

The recipe requires that Anaconda is already installed. You can use the buildout option ``anaconda-home`` to set the prefix for the anaconda installation. Otherwise the environment variable ``CONDA_PREFIX`` (variable is set when activating a conda environment) is used as conda prefix. 

It installs the ``pywps`` package from a conda channel in a conda environment defined by ``CONDA_PREFIX``. The location of the intallation is given by the ``prefix`` buildout option. It setups a `PyWPS`_ output folder in ``${prefix}/var/lib/pywps``. It deploys a `Supervisor`_ configuration for ``PyWPS`` in ``${prefix}/etc/supervisor/conf.d/pywps.conf``. Supervisor can be started with ``${prefix}/etc/init.d/supervisor start``.

The recipe will install the ``nginx`` package from a conda channel and deploy a Nginx site configuration for ``PyWPS``. The configuration will be deployed in ``${prefix}/etc/nginx/conf.d/pywps.conf``. Nginx will be started by supervisor.

By default ``PyWPS`` will be available on http://localhost:8091/wps?service=WPS&version=1.0.0&request=GetCapabilities.

The recipe depends on: 

* ``birdhousebuilder.recipe.conda``, 
* ``birdhousebuilder.recipe.supervisor``, 
* ``birdhousebuilder.recipe.nginx`` and 
* ``zc.recipe.deployment``.

Supported options
=================

The recipe supports the following buildout options:

**anaconda-home**
   Buildout option pointing to the root folder of the Anaconda installation. Default: ``$HOME/anaconda``.

Buildout options for ``pywps``:

**prefix**
  Deployment option to set the prefix of the installation folder. Default: ``/``

**user**
  Deployment option to set the run user.

**etc-user**
  Deployment option to set the user of the ``/etc`` directory. Default: ``root``

**name**
   The name of your WPS project (used for config names and folder path).

**hostname**
   The hostname of the ``PyWPS`` service (nginx). Default: ``localhost``

**http-port**
   The http port of the ``PyWPS`` service (nginx). Default: ``8091``

**https-port**
   The https port of the ``PyWPS`` service (nginx). Default: ``28091``

**output-port**
   The http port of the ``PyWPS`` output file service (nginx). Default: ``8090``

**workers**
   The number of gunicorn workers for handling requests. Default: 1

**processesPath**
   Path the ``PyWPS`` processes.
   
**title**
   Title used for your WPS service.

**abstract**
   Description of your WPS service.

**logLevel**
   Logging level for ``PyWPS``. Default: ``WARN``

**maxoperations**
   Maximum number of parallel WPS operations. Default: 100

**maxfilesize**
   Maximal file size accepted in WPS process. Default: 30GB
 

Example usage
=============

The following example ``buildout.cfg`` installs ``PyWPS`` with Anaconda::

  [buildout]
  parts = pywps

  anaconda-home = /opt/anaconda

  [pywps]
  recipe = birdhousebuilder.recipe.pywps
  name = myproject
  prefix = /
  user = www-data
  hostname = localhost
  http-port = 8091
  https-port = 28091

  # pywps options
  processesPath = ${buildout:directory}/myproject/processes
  title = MyProject ...
  abstract = MyProject does ...

After installing with Buildout start the ``PyWPS`` service with::

  $ cd ${prefix}
  $ etc/init.d/supervisord start  # start|stop|restart
  $ etc/init.d/nginx start        # start|stop|restart
  $ bin/supervisorctl status      # check that pycsw is running
  $ less var/log/pywps/myproject.log  # check log file

Open your browser with the following URL:: 

  http://localhost:8091/wps?service=WPS&version=1.0.0&request=GetCapabilities





