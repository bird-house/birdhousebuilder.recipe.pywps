#!/bin/bash
export PYWPS_CFG="${prefix}/etc/pywps/${name}.cfg"
export PATH="${bin_dir}":"${prefix}/bin:/usr/bin:/bin:/usr/local/bin"
export GDAL_DATA="${prefix}/share/gdal"

${bin_dir}/wps.py $@

exit 0
