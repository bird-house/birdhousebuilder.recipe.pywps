bind = 'unix://${prefix}/var/run/${sites}.socket'
workers = 3

# environment
raw_env = ["HOME=${prefix}/var/lib/pywps", 
           "PYWPS_CFG=${prefix}/etc/pywps/${sites}.cfg", 
	   "PATH=${bin_dir}:${prefix}/bin:/usr/bin:/bin:/usr/local/bin", 
           ]                                                                                                               

# logging

debug = True
errorlog = '-'
loglevel = 'debug'
accesslog = '-'
