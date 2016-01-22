#!/bin/bash
export PYWPS_CFG=${prefix}/etc/pywps/${sites}.cfg

${bin_dir}/wps.py $@

exit 0
