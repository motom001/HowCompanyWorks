#!/usr/bin/python
# -*- coding: utf-8 -*-

import main
import logging
import logging.handlers

from resources.corridor import *
from resources.crepsheet import *
from resources.employee import *
from resources.employer import *
from resources.messages import *
from resources.trainee import *

from logging import getLogger

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]  \t[%(name)s] %(message)s')
logger = getLogger(__name__)
logger.debug("%s loaded", __name__)


def dummy_function(message = "test"):
    logger.info("HIER: %s" % message)
    return True


def main_function():
    main_corridor = Corridor()
    try:
        main_corridor.employer.start_working()
        main_corridor.employer.hire_new_employee(EmployeeTimer)
        while True:
            time.sleep(1)
            main_corridor.employer.check_trainees()
    except KeyboardInterrupt:
        main_corridor.employer.stop_working()

if __name__ == "__main__":
    main_function()
