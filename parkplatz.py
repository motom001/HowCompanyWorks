#!/usr/bin/python
# -*- coding: utf-8 -*-

import main

import Queue
from threading import Thread
import inspect
import random
import time

from resources.corridor import *
from resources.crepsheet import *
from resources.employee import *
from resources.employer import *
from resources.messages import *
from resources.trainee import *

# corridor = zentralerSammelpunkt aller Object
# employer = Chef der über alles wacht
# employee = Interface mit Input und Output
# trainee = Läufer
# crip sheet = Verbindung zwischen Output und Input

# employer stellt trainee an
# employer zeigt trainee zentrales crip sheet
# employer stellt trainee auf den corridor

# employer füllt message aus und legt diese in den corridor
# trainee sieht message im corridor
# trainee schaut auf crep sheet was bei dieser message zu tun ist
# trainee sagt anderem employee das und was zu tun ist
# employee arbeitet und gibt ergebnis als message aus und legt diese in den corridor

# neue employee melden sich beim employer
# employee sagt dem employer was sie können
# employee sagt dem employer was was sie brauchen
# employer vermerkt das auf zentralem crep sheet
# employee wartet im office


def dummy_function(message = "test"):
    print "HIER: %s" % message
    return True


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


class Message(object):
    @property
    def obsolete(self):
        return time.time() > self.start_time + self.timeout

    def __init__(self, message):
        self.type = "message"
        self.start_time = time.time()
        self.ask_for_response = False

        if isinstance(message, Task):
            self.result = message
            self.name = self.result.message.name
            self.priority = 50
            self.timeout = 5
        else:
            self.result = None
            self.name = str(message)
            self.priority = 50
            self.timeout = 5

        print 'New message "%s" with priority "%s"' % (self.name, self.priority)

    def __cmp__(self, other):
        return cmp(self.priority, other.priority)


class Task(object):
    def __init__(self, message, *args, **kwargs):
        self.message = message
        self.args = args
        self.kwargs = kwargs
        self.target = None
        self.result = None

    def __call__(self, *args, **kwargs):
        self.args += args
        self.kwargs.update(kwargs)
        self.result = self.target()
        return self

    def __str__(self):
        if self.args and self.kwargs:
            return "%s with %s and %s" % (self.message, self.args, self.kwargs)
        elif self.args:
            return "%s with %s" % (self.message, self.args)
        elif self.kwargs:
            return "%s with %s" % (self.message, self.kwargs)
        else:
            return "%s" % self.message


class CrepSheet(object):
    def __call__(self, message):
        new_task = Task(message)
        new_task.target = dummy_function
        return new_task


class Employee(object):
    @property
    def skills(self):
        return self.input, self.output

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
        self.corridor += Message('TimeTick')

    def wait_to_next_time_tick(self):
        time.sleep(0.5)
        self.corridor += Message('TimeTick')
        return True


class Trainee(object):
    def __init__(self, corridor):
        self.corridor = corridor
        self.status = "new"

    def wait_for_message(self):
        while self.corridor.lights is 'on' and self.status is not "fired":
            self.status = "idle"
            if self.corridor.message_box.empty():
                print "nothing to do - I will wait for next message"
                self.status = "waiting"
                time.sleep(1)
                continue
            else:
                new_message = self.corridor.message_box.get()
                if new_message.obsolete:
                    print "I was not fast enough for this message, sorry"
                    continue
                new_task = self.corridor.crep_sheet(new_message)
                print "this is my new task: ", str(new_task)
                self.status = "busy"
                task_result = Message(new_task())
                if task_result.result.response:
                    self.corridor += task_result

        self.corridor -= self
        return True


class Employer(Employee):
    max_trainee_budget = 5

    def __init__(self, corridor):
        Employee.__init__(self, corridor)
        self.corridor.lights = 'on'

    def start_company_working(self):
        for i in range(self.max_trainee_budget):
            print "hire new trainee was %s" % self.hire_new_trainee()
        return len(self.corridor.trainees) is self.max_trainee_budget

    def stop_company_working(self):
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
            print("WTF - there are no trainees anymore? Who will work now for me?")
            return False

    def hire_new_trainee(self):
        new_trainee = Trainee(self.corridor)
        self.corridor += new_trainee
        return new_trainee in self.corridor.trainees

    def hire_new_employee(self, employee_type):
        if not issubclass(employee_type, Employee):
            print("WTF - %s is not an employee - go away with this shit!" % employee_type)
            return False
        if issubclass(employee_type, Employer):
            print("WTF - %s is also an employer - we needn't a second employer" % employee_type)
            return False

        new_employee = employee_type(self.corridor)
        #self.corridor.crep_sheet += new_employee.skills
        self.corridor += new_employee
        return True

    __del__ = stop_company_working


class Corridor(object):
    def __init__(self):
        self.lights = 'off'
        self.crep_sheet = CrepSheet()
        self.message_box = Queue.PriorityQueue()

        self.employees = []
        self.trainees = []
        self.employer = Employer(self)

    def __add__(self, other):
        print "add new %s to corridor" % other
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
            self.message_box.put(other, block=False, timeout=other.timeout)
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


def main_function():
    main_corridor = Corridor()
    try:
        main_corridor.employer.start_company_working()
        main_corridor.employer.hire_new_employee(EmployeeTimer)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        main_corridor.employer.stop_company_working()

if __name__ == "__main__":
    main_function()





class DoorPi(object):
    def __init__(self):
        return

    def fire_event(self, event_name, *args, **kwargs):
        print "I fire noew the event ", event_name
        print "args: %s" % args
        print "kwargs: %s" % kwargs
        return True

    def register_new_module(self, module_name):
        return True

    def register_new_interface(self, interface_object):
        test = interface_object.__class__


DOORPI = DoorPi()


class InterfaceBase(object):
    def __init__(self):
        DOORPI.register_new_interface(self)


class SipPhone(InterfaceBase):
    def call_number(self, number):
        print "I call now the number ", number


class Keyboard(InterfaceBase):
    def key_pressed(self, key):
        DOORPI.fire_event('key_pressed', {"source": self.__class__, "key": key})


import Queue
import random
import time


class EventDescription:
    fire_sync = True
    sources = []
    target_function = []


event_to_function = {
    "Event1": {

    }
}

keep_running = True
active_workers = dict()
active_workers_status = dict()
worker_queue = Queue.PriorityQueue()


def doorpi_worker(worker_name):
    while keep_running is True:
        active_workers_status[worker_name] = "idle"
        if worker_queue.empty():
            print "nothing to do for ", worker_name
            time.sleep(random.randrange(0, 1, 0.1))
            continue
        target_function = worker_queue.get()


def event_target_function():
    print "fire target function"
    return


class Job(object):
    def __init__(self, target_function, event_source, event_priority=50):
        self.event_priority = 50
        self.event_name = event_name
        self.event_source = event_source
        print 'New Event "%s" from "%s"' % (event_name, event_source)

    def __cmp__(self, other):
        return cmp(self.event_priority, other.event_priority)


# Set up some threads to fetch the enclosures
for i in range(5):
    worker_name = "worker %s" % i
    active_workers[worker_name] = Thread(
        name="worker %s" % i,
        target=doorpi_worker,
        kwargs={
            worker_name: worker_name
        }
    )
    active_workers[worker_name].setDaemon(True)
    active_workers[worker_name].start()

while True:
    if q.empty():
        time.sleep(0.2)
        print "fill queue now"
        for i in range(20):
            priority = random.randrange(0, 101)
            q.put(Job('Event with priority %s' % priority, __name__, priority))

while not q.empty():
    next_job = q.get()
    print 'Processing job "%s" from "%s"' % (next_job.event_name, next_job.event_source)
