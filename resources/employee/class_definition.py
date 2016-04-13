# -*- coding: utf-8 -*-

import Queue
from threading import Thread
import inspect
import random
import time

from resources.messages import *

from logging import getLogger
logger = getLogger(__name__)
logger.debug("%s loaded", __name__)


class EmployeeInput(object):
    def __init__(self, contact, name, **conditions):
        self.contact = contact
        self.name = name
        self.conditions = conditions


class EmployeeOutput(object):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs


class Employee(object):
    @property
    def skills(self):
        return [self.input, self.output]

    def __init__(self, corridor):
        self.corridor = corridor
        self.status = "new"
        self.input = []
        self.output = []


class EmployeeTimer(Employee):
    def __init__(self, corridor):
        Employee.__init__(self, corridor)

        self.input = [
            EmployeeInput(self.wait_to_next_time_tick, "TimeTick")
        ]
        self.output = [
            EmployeeOutput("TimeTick")
        ]

    def start(self):
        self.corridor += Event('TimeTick', str(self))

    def wait_to_next_time_tick(self):
        time.sleep(0.5)
        self.corridor += Event('TimeTick', __name__).set('priority', 5).set('immortal', True)
        self.corridor += Event('Quatsch', __name__).set('priority', 90)
        self.corridor += Event('Quatsch', __name__).set('priority', 90)
        self.corridor += Event('Quatsch', __name__).set('priority', 90)
        self.corridor += Event('Quatsch', __name__).set('priority', 90)
        self.corridor += Event('Quatsch', __name__).set('priority', 90)
        self.corridor += Event('Quatsch', __name__).set('priority', 90)
        self.corridor += Event('Quatsch', __name__).set('priority', 90)
        self.corridor += Event('Quatsch', __name__).set('priority', 90)
        return True
