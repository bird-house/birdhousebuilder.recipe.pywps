import os
from pywps.app.Service import Service
from pywps import Process
import logging
logger = logging.getLogger('PYWPS')

# processes need to be installed in PYTHON_PATH
# from processes.sleep import Sleep

import sys
import inspect
import emu.processes
processes = []
for name, clazz in inspect.getmembers(sys.modules['emu.processes'],
                                      inspect.isclass):
    if issubclass(clazz, Process):
        processes.append(clazz())
        logger.info("init process %s", name)

application = Service(processes, [os.environ['PYWPS_CFG']])
