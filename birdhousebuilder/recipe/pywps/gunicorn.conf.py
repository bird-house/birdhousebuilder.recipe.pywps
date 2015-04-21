bind = 'unix://${prefix}/var/run/${sites}.socket'
workers = 3

def python_path():
    """Generates PYTHONPATH from sys.path"""
    import sys
    ppath = ['${package_dir}']
    for path in sys.path:
        if '${package_dir}/eggs/' in path:
            # add buildout eggs
            ppath.append(path)
    return ':'.join(ppath)

# environment
raw_env = ["PYWPS_CFG=${prefix}/etc/pywps/${sites}.cfg", 
           "PATH=${bin_dir}:${prefix}/bin:/usr/bin:/bin:/usr/local/bin",
           "GDAL_DATA=${prefix}/share/gdal",
           "PYTHONPATH=%s" % python_path(),
           ]                                                                                                               

# logging

debug = True
errorlog = '-'
loglevel = 'debug'
accesslog = '-'
