#!/usr/bin/python3
#
# [MTE] Maintenance Task Execution: Task Dispatcher
# @Description: Dispatches Tasks and provides Task framework
#
# @Author: Arne Coomans
# @Contact: @arnecoomans on twitter
# @Version: 0.0
# @Date: 01-01-2021
# @Source: https://github.com/arnecoomans/maintenance/
#
#
# Import system modules
import os
import sys
import importlib

sys.path.append(os.path.dirname(os.path.abspath(__file__) + "../tasks/"))

class TaskDispatcher:
  def __init__(self, core):
    self.core = core
    self.storage = {}
    self.available_tasks = []
    self.inventorize_tasks()
    

  def inventorize_tasks(self):
    # Check for installed tasks on filesystem
    for filename in os.listdir(self.core.get('base_dir') + 'tasks/'):
      if os.path.splitext(filename)[1] == ".py":
        if self.is_marked_as_task(filename):
          self.available_tasks.append(os.path.splitext(filename)[0])
    self.core.log.add("Found available tasks: [" + ", ".join(self.available_tasks) + "].", 5)
  
  def is_marked_as_task(self, filename):
    # Tasks should have "# [MTETASK]" as second line in the file
    # This marks that the file is a task and it should be executed as task.
    # This prevents other files being ran in the task dispatcher.
    f=open(self.core.get('base_dir') + 'tasks/' + filename)
    lines=f.readlines()
    if len(lines) > 2:
      if lines[1].strip() == "# [MTETASK]":
        f.close()
        return True
    else:
      f.close()
      self.core.log.add("File " + filename + " in tasks directory is not a task. File should be removed.", 2)
      return False

  def is_task(self, task):
    if task in self.available_tasks:
      return True
    return False
  
  def get_current_task(self):
    pass
  
  def dispatch(self, task):
    self.core.log.add("Dispatched task: [" + task + "].", 4)
    if self.is_task(task):
      module_task = importlib.import_module(task, package=None)
      task = module_task.Task(self.core, task)
      return True
    else:
      self.core.log.add("Task [" + task + "] not found. Skipping this task.", 1)
      return False

class Task:
  def __init__(self, core, task_name):
    self.core = core
    self.task_name = task_name
    self.storage = {}
    self.queue = []
    self.core.log.add("Loaded task: [" + self.get_task_name() + "].", 5)
    self.execute()

  def get_task_name(self):
    return self.task_name
    