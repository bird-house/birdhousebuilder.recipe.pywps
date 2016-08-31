import os
from pywps.app.Service import Service

from emu.processes import processes

application = Service(processes, [os.environ['PYWPS_CFG']])
