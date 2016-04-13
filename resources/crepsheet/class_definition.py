# -*- coding: utf-8 -*-

import main

from resources.messages import *
from resources.employee import *

from logging import getLogger
logger = getLogger(__name__)
logger.debug("%s loaded", __name__)


class CrepSheet(object):
    event_mapping = {}

    def __add__(self, other):
        logger.debug("get some new skills %s" % other)
        if isinstance(other, list):
            for single in other:
                return self.__add__(single)
        elif isinstance(other, EmployeeInput):
            logger.debug("get new input skill %s" % other.name)
            if other.name in self.event_mapping:
                if other not in self.event_mapping[other.name]:
                    self.event_mapping[other.name].append(other)
            else:
                self.event_mapping[other.name] = [other]
        logger.debug("event_mapping ist now: %s", self.event_mapping)
        return self

    def __call__(self, message):
        tasks = []
        if message.name in self.event_mapping.keys():
            for target in self.event_mapping[message.name]:
                tasks.append(message.to_task(target.contact))
        return tasks
