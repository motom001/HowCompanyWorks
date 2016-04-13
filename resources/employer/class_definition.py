#!/usr/bin/python
# -*- coding: utf-8 -*-

import Queue
from threading import Thread
import inspect
import random
import time

from resources.employee import *
from resources.trainee import *

from logging import getLogger
logger = getLogger(__name__)
logger.debug("%s loaded", __name__)


class Employer(Employee):
    max_trainee_budget = 10

    def __init__(self, corridor):
        Employee.__init__(self, corridor)
        self.corridor.lights = 'on'

    def stop_working(self):
        self.corridor.lights = 'off'
        return self.fire_all_trainees()

    def fire_all_trainees(self):
        for i in range(len(self.corridor.trainees)):
            self.fire_one_trainee()
        return len(self.corridor.trainees) is 0

    def fire_one_trainee(self):
        if len(self.corridor.trainees) > 0:
            self.corridor -= self.corridor.trainees[0]
            return True
        else:
            logger.warning("WTF - there are no trainees anymore? Who will work now for me?")
            return False

    def hire_new_trainee(self):
        new_trainee = Trainee(self.corridor)
        self.corridor += new_trainee
        return new_trainee in self.corridor.trainees

    def hire_new_employee(self, employee_type):
        if not issubclass(employee_type, Employee):
            logger.error("WTF - %s is not an employee - go away with this shit!" % employee_type)
            return False
        if issubclass(employee_type, Employer):
            logger.error("WTF - %s is also an employer - we needn't a second employer" % employee_type)
            return False

        new_employee = employee_type(self.corridor)
        self.corridor.crep_sheet += new_employee.skills
        self.corridor += new_employee
        new_employee.start()
        return True

    __del__ = stop_working
