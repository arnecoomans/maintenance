#!/usr/bin/python3
#
#
# [MTE] Maintenance Task Execution: Entry Point
# @Description: Centralized entry point for extenable maintenance
#               tasks.
#
# @Author: Arne Coomans
# @Contact: @arnecoomans on twitter
# @Version: 0.2.0
# @Date: 01-01-2021
# @Source: https://github.com/arnecoomans/maintenance/
#
#
# Import system modules
import os
import sys

# Add local shared script directory to import path
#   Local function library
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/.app/")
import mte_core as mte_core

#   Tasks storage library
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/tasks-enabled/")

# Load Core
#   Core handles basic functionality such as runtime argument processing.
#   Core loads Logging, Configuration and Dispatching classes
core = mte_core.Core()
# Dispatch tasks
for task in core.tasks:
  core.dispatcher.dispatch(task)
