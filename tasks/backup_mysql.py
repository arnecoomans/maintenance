#!/usr/bin/python3
# [MTETASK]
#
# [MTE] Maintenance Task: Pass
# @Description: Don't do anything. 
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
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__) + "../.app/"))

import mte_task_dispatcher


class Task(mte_task_dispatcher.Task):
  def __init__(self, core, task_name):
    self.command_line_commands = {
      'get_list_of_all_databases': 'mysql -e \'show databases\' -s --skip-column-names',
      'dump_database': 'mysqldump %database% %gzip% > %target%%filename%'
    }
    super().__init__(core, task_name)
    

  def execute(self):
    # Creating a backup of all databases
    self.core.log.add('Getting list of databases to be backed up', 5)
    databases = self.remove_ignored_databases_from_list(self.get_list_of_all_databases())
    self.core.log.add('Found databases: [' + ', '.join(databases) + '].', 5)
    for database in databases:
      self.dump_database(database)  
  def get_list_of_all_databases(self):
    return self.core.run_command(self.command_line_commands['get_list_of_all_databases'], self.get_task_name())
  
  def remove_ignored_databases_from_list(self, list):
    result = []
    for database in list:
      if database not in self.core.config.get('ignored_databases', [self.get_task_name()]).split(", ") and len(database) > 0:
        result.append(database)
    return result
  
  def dump_database(self, database):
    # process command
    command = self.command_line_commands['dump_database']
    command = command.replace('%database%', database)
    command = command.replace('%gzip%', self.core.get_gzip(self.get_task_name()))
    command = command.replace('%target%', self.core.get_target(self.get_task_name()))
    # Filename
    filename = database
    now = datetime.now()
    # Check if task configuration holds date_time_format
    if self.core.config.get('date_time_format', self.get_task_name()):
      filename += '_'
      filename += datetime.now().strftime(self.core.config.get('date_time_format', self.get_task_name()))
    # Check if main configuration holds date_time_format
    elif self.core.config.get('date_time_format'):
      filename += '_'
      filename += datetime.now().strftime(self.core.config.get('date_time_format'))
    filename += '.sql'
    if len(self.core.get_gzip(self.get_task_name())) > 0:
      filename += '.tar.gz'
    command = command.replace('%filename%', filename)
    self.core.run_command(command, self.get_task_name())
    
