# -*- coding: utf-8 -*-

import Queue
from threading import Thread, Lock
import inspect
import random
import time
from copy import deepcopy

from logging import getLogger
logger = getLogger(__name__)
logger.debug("%s loaded", __name__)


class Message:
    @property
    def obsolete(self):
        if self.immortal:
            return False
        else:
            return time.time() > self.start_time + self.validity_period

    def __init__(self, name, source, *args, **kwargs):
        self.name = name
        self.source = source
        self.target = None
        self.start_time = time.time()
        self.validity_period = 5
        self.args = args
        self.kwargs = kwargs
        self.result = None
        self.response = None
        self.priority = 50
        self.immortal = False

    def set(self, key, value):
        if key in self.__dict__:
            self.__dict__[key] = value
        return self

    def __str__(self):
        return "%s: %s from %s to %s with result %s" % (
            self.__class__, self.name, self.source, self.target, self.result
        )

    def __cmp__(self, other):
        return cmp(self.priority, other.priority)


class Event(Message):
    def to_task(self, target, *args, **kwargs):
        return Task.from_event(self, target, args, kwargs)


class Task(Message):
    @staticmethod
    def from_event(event, target, *args, **kwargs):
        new_task = Task(
            event.name,
            event.source,
            event.args + args,
            event.kwargs.update(kwargs)
        )
        new_task.target = target
        return new_task

    def to_result(self, *args, **kwargs):
        return Result.from_task(self, self.execute(args, kwargs), args, kwargs)

    def execute(self, *args, **kwargs):
        try:
            self.result = self.target()
        except Exception as exp:
            logger.exception(exp)

    __call__ = execute


class Result(Message):
    @staticmethod
    def from_task(task, result, *args, **kwargs):
        new_result = Result(
            task.name,
            task.source,
            task.args + args,
            task.kwargs.update(kwargs)
        )
        new_result.target = task.target
        new_result.result = result
        return new_result
