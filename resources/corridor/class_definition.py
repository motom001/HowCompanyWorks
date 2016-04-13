# -*- coding: utf-8 -*-

import Queue
from threading import Thread

from resources.crepsheet import *
from resources.employer import *

from logging import getLogger
logger = getLogger(__name__)
logger.debug("%s loaded", __name__)


class Corridor(object):
    def __init__(self):
        self.lights = 'off'
        self.crep_sheet = CrepSheet()
        self.message_box = Queue.PriorityQueue()

        self.employees = []
        self.trainees = []
        self.employer = Employer(self)

    def __add__(self, other):
        logger.debug("add new %s to corridor" % other)
        if isinstance(other, Trainee):
            self.trainees.append(other)
            new_trainee = Thread(
                name="trainee nr. %s" % len(self.trainees),
                target=other.wait_for_message
            )
            new_trainee.setDaemon(True)
            new_trainee.start()
        elif isinstance(other, Employee):
            self.employees.append(other)
            other.start()
        elif isinstance(other, Message):
            self.message_box.put(other, block=True)
        else:
            raise Exception("unknown object added in corridor")
        return self

    def __sub__(self, other):
        if isinstance(other, Trainee):
            if other in self.trainees:
                other.status = "fired"
                self.trainees.remove(other)
        elif isinstance(other, Employee):
            other.status = "fired"
            self.employees.remove(other)
        else:
            raise Exception("unknown object can't removed from corridor")
        return self
