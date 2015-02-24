*****************************
birdhousebuilder.recipe.pywps
*****************************

.. contents::

Introduction
************

``birdhousebuilder.recipe.pywps`` is a `Buildout`_ recipe to install and configure `PyWPS`_ with `Anaconda`_. `PyWPS`_ is a Python implementation of a `Web Processing Service`_ (WPS). ``PyWPS`` will be deployed as a `Supervisor`_ service and is available on a `Nginx`_ web server. 
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

The recipe requires that Anaconda is already installed. It assumes that the default Anaconda location is in your home directory ``~/anaconda``. Otherwise you need to set the ``ANACONDA_HOME`` environment variable or the Buildout option ``anaconda-home``.

It installs the ``pywps`` package from a conda channel in a conda environment named ``birdhouse``. The location of the birdhouse environment is ``.conda/envs/birdhouse``. It setups a `PyWPS`_ output folder in ``~/.conda/envs/birdhouse/var/lib/pywps``. It deploys a `Supervisor`_ configuration for ``PyWPS`` in ``~/.conda/envs/birdhouse/etc/supervisor/conf.d/pywps.conf``. Supervisor can be started with ``~/.conda/envs/birdhouse/etc/init.d/supervisor start``.

The recipe will install the ``nginx`` package from a conda channel and deploy a Nginx site configuration for ``PyWPS``. The configuration will be deployed in ``~/.conda/envs/birdhouse/etc/nginx/conf.d/pywps.conf``. Nginx can be started with ``~/.conda/envs/birdhouse/etc/init.d/nginx start``.

By default ``PyWPS`` will be available on http://localhost:8091/wps?service=WPS&version=1.0.0&request=GetCapabilities.

The recipe depends on ``birdhousebuilder.recipe.conda``, ``birdhousebuilder.recipe.supervisor`` and ``birdhousebuilder.recipe.nginx``.

Supported options
=================

The recipe supports the following options:

``anaconda-home``
   Buildout option with the root folder of the Anaconda installation. Default: ``$HOME/anaconda``.
   The default location can also be set with the environment variable ``ANACONDA_HOME``. Example::

     export ANACONDA_HOME=/opt/anaconda

   Search priority is:

   1. ``anaconda-home`` in ``buildout.cfg``
   2. ``$ANACONDA_HOME``
   3. ``$HOME/anaconda``

``hostname``
   The hostname of the ``PyWPS`` service (nginx). Default: ``localhost``

``port``
   The port of the ``PyWPS`` service (nginx). Default: ``8091``

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

  $ cd /home/myself/.conda/envs/birdhouse
  $ etc/init.d/supervisord start  # start|stop|restart
  $ etc/init.d/nginx start        # start|stop|restart
  $ bin/supervisorctl status      # check that pycsw is running
  $ less var/log/pywps/myproject.log  # check log file

Open your browser with the following URL:: 

  http://localhost:8091/wps?service=WPS&version=1.0.0&request=GetCapabilities





