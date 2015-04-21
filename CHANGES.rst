Change History
**************

0.2.2 (2015-04-21)
==================

* do not set ``HOME`` environment variable in gunicorn.

0.2.1 (2015-03-24)
==================

* added mako_cache to pywps config.

0.2.0 (2015-02-24)
==================

* installing in conda enviroment ``birdhouse``.
* using ``$ANACONDA_HOME`` environment variable.
* separation of anaconda-home and installation prefix.

0.1.11 (2014-12-08)
===================

* changed default log level.

0.1.10 (2014-12-06)
===================

* Don't update conda on buildout update.
* Sets PYTHONPATH in gunicon.conf.py. Used in PyWPS async processes.

0.1.9 (2014-11-26)
==================

* Added cache section to pywps.cfg template.

0.1.8 (2014-11-03)
==================

* GDAL_DATA added to environment in gunicorn.conf.py template.

0.1.7 (2014-08-27)
==================

* phoenix option added for wpsoutputs.

0.1.6 (2014-08-26)
==================

* Fixed proxy config for wpsoutputs.

0.1.5 (2014-08-23)
==================

added cache path to nginx configuration.

0.1.4 (2014-08-17)
==================

added /usr/local/bin to gunicorn path (needed for brew on macosx)

0.1.3 (2014-08-01)
==================

Updated documentation.

0.1.2 (2014-07-24)
==================

Fixed hostname in nginx template.

0.1.1 (2014-07-11)
==================

Fixed HOME env in gunicorn template.

0.1.0 (2014-07-10)
==================

Initial Release.
