bind = 'unix://${prefix}/var/run/pywps.socket'
workers = 3

# environment
raw_env = ["HOME=${prefix}/var/lib/pywps", 
           "PYWPS_CFG=${prefix}/etc/pywps/pywps.cfg", 
           "PATH=${prefix}/bin:/usr/bin:/bin", 
           ]                                                                                                               

# logging

debug = True
errorlog = '-'
loglevel = 'debug'
accesslog = '-'
