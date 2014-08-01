*****************************
birdhousebuilder.recipe.pywps
*****************************

.. contents::

Introduction
************

``birdhousebuilder.recipe.pywps`` is a `Buildout`_ recipe to install and configure `PyWPS`_ with `Anaconda`_. `PyWPS`_ is a Python implementation of a `Web Processing Service`_ (WPS). ``PyWPS`` will be deployed as a `Supervisor`_ service and is available on a `Nginx`_ web server. 

Birdhousebuilder recipes are used to build Web Processing Service components (Phoenix, Malleefowl, Nighthawk, FlyingPigeon, ...) of the ClimDaPs project. All Birdhousebuilder recipes need an existing `Anaconda`_ installation.  

.. _`Buildout`: http://buildout.org/
.. _`Anaconda`: http://continuum.io/
.. _`Supervisor`: http://supervisord.org/
.. _`Nginx`: http://nginx.org/
.. _`PyWPS`: https://github.com/geopython/PyWPS
.. _`Web Processing Service`: https://en.wikipedia.org/wiki/Web_Processing_Service


Usage
*****

The recipe requires that Anaconda is already installed. It assumes that Anaconda is installed at the default location in your home directory ``~/anaconda``. Otherwise you need to set the Buildout option ``anaconda-home`` to the correct location.

It installs the ``pywps`` package from a conda channel and setups a `PyWPS`_ output folder in ``~/anaconda/var/lib/pywps``. It deploys a `Supervisor`_ configuration for ``PyWPS`` in ``~/anaconda/etc/supervisor/conf.d/pywps.conf``. Supervisor can be started with ``~/anaconda/etc/init.d/supervisor start``.

The recipe will install the ``nginx`` package from a conda channel and deploy a Nginx site configuration for ``PyWPS``. The configuration will be deployed in ``~/anaconda/etc/nginx/conf.d/pywps.conf``. Nginx can be started with ``~/anaconda/etc/init.d/nginx start``.

By default ``PyWPS`` will be available on http://localhost:8091/wps?service=WPS&version=1.0.0&request=GetCapabilities.

The recipe depends on ``birdhousebuilder.recipe.conda``, ``birdhousebuilder.recipe.supervisor`` and ``birdhousebuilder.recipe.nginx``.

Supported options
=================

The recipe supports the following options:

``anaconda-home``
   Buildout option with the root folder of the Anaconda installation. Default: ``$HOME/anaconda``.

``hostname``
   The hostname of the pycsw service (nginx). Default: ``localhost``

``port``
   The port of the pycsw service (nginx). Default: ``8091``

``sites``
   The name of your WPS project (used for config names and folder path).

``processesPath``
   Path the ``PyWPS`` processes.
   
``title``
   Title used for your WPS service.

``abstract``
   Description of your WPS service.


Example usage
=============

The following example ``buildout.cfg`` installs ``PyWPS`` with Anaconda::

  [buildout]
  parts = pywps

  anaconda-home = /home/myself/anaconda

  [pywps]
  recipe = birdhousebuilder.recipe.pywps
  sites = myproject
  hostname = localhost
  port = 8091

  # pywps options
  processesPath = ${buildout:directory}/myproject/processes
  title = MyProject ...
  abstract = MyProject does ...

After installing with Buildout start the ``PyWPS`` service with::

  $ cd /home/myself/anaconda
  $ etc/init.d/supervisord start  # start|stop|restart
  $ etc/init.d/nginx start        # start|stop|restart
  $ bin/supervisorctl status      # check that pycsw is running
  $ less var/log/pywps/myproject.log  # check log file

Open your browser with the following URL:: 

  http://localhost:8091/csw?service=WPS&version=1.0.0&request=GetCapabilities





