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


class Trainee(object):
    def __init__(self, corridor):
        self.corridor = corridor
        self.status = "new"

    def wait_for_message(self):
        while self.corridor.lights is 'on' and self.status is not "fired":
            self.status = "idle"
            if self.corridor.message_box.empty():
                logger.debug("nothing to do - I will wait for next message")
                self.status = "waiting"
                time.sleep(0.1)
                continue
            else:
                new_message = self.corridor.message_box.get()
                logger.debug("I have a new message %s" % new_message)
                if new_message.obsolete:
                    logger.error("I was not fast enough for message %s, sorry" % new_message.name)
                    self.corridor += Event("ObsoleteMessage", __name__, new_message).set('priority', 1)
                elif isinstance(new_message, Event):
                    self.status = "convert event to tasks"
                    tasks = self.corridor.crep_sheet(new_message)
                    if new_message.response is not None:
                        new_message.response(tasks)
                    for i in range(len(tasks)):
                        self.corridor += tasks[i]
                elif isinstance(new_message, Task):
                    self.status = "execute task"
                    self.corridor += new_message.to_result()
                elif isinstance(new_message, Result):
                    if new_message.response is not None:
                        new_message.response(new_message)
                else:
                    print "strange message - I don't know how to handle it..."
                self.corridor.message_box.task_done()

        self.corridor -= self
        return True
