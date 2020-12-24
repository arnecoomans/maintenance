#!/usr/bin/python3
#
# [MTE] Maintenance Task Execution: Filesystem processor
# @Description: 
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
import pathlib # https://docs.python.org/3/library/pathlib.html


class Filesystem:
  def __init__(self, core):
    self.core = core


  # Create Directory
  # @requires: target (pathlib.PosixPath object or string)
  # @optional: task
  # Creates the requested directory. If parent does not exist, parent is
  # created before proceeding. If sudo can be used to create directory,
  # the highest to-be-created directory is created using sudo and 
  # ownership is set to the runtime user and group.
  def create_directory(self, target, task=''):
    # Expect target to be pathlib.PosixPath object.
    # If it is not, create it.
    # If it is, use it.
    if type(target) is not pathlib.PosixPath:
      target = pathlib.Path(target)
    # 
    # Check if directory exists
    if target.exists():
      # Directory already exists
      if os.access(target, os.W_OK):
        # Directory is writable for current user.
        return True
      else:
        # Directory is not writable for current user.
        # Do not make changes to existing directories, this is a fatal error.
        self.core.log.add('Directory [' + str(target.absolute()) + '] already exists, but write access is denied. Please resolve.', 1)
        self.core.panic()
    # Directory does not yet exist
    else:
      # Check if parent exists
      if not  target.parent.exists():
        # Parent directory does not exist, create it before proceeding
        self.create_directory(target.parent, task)
      # Parent now exists.
      # Can runtime user write in parent directory?
      # If yes, runtime user can create the directory
      if os.access(target.parent, os.W_OK):
        # Yes
        self.core.log.add('Creating directory [' + str(target.absolute()) + '].', 4)
        command = 'mkdir ' + str(target.absolute())
        create_process = os.popen(command)
        response = create_process.read().strip().split("\n")
        return True
      # If parent directory is not writable for runtime user, 
      # try to create the directory using sudo.
      else:
        if self.core.use_sudo(task):
          # Create directory using Sudo
          self.core.log.add('Using sudo for creating directory [' + str(target.absolute()) + '] and setting ownership to [' + self.core.get('runtime_user') + '].', 4)
          command = 'sudo mkdir ' + str(target.absolute())
          create_process = os.popen(command)
          response = create_process.read().strip().split("\n")
          # Change ownership of directory to runtime user
          command = 'sudo chown ' + self.core.get('runtime_user_id') + ':' + self.core.get('runtime_group_id') + ' ' + str(target.absolute())
          create_process = os.popen(command)
          response = create_process.read().strip().split("\n")
          return True
        else:
          self.core.log.add('Create Directory: Insufficient user rights to create directory [' + str(target.absolute()) + '].', 1)
          self.core.panic()
    # Done.

  def create_backup(self, source, target, task=''):
    if type(source) is not pathlib.PosixPath:
      source = pathlib.Path(source)
    if type(target) is not pathlib.PosixPath:
      target = pathlib.Path(target)
    # Process Source
    # If Source is a directory, do not process.
    if os.path.isdir(source):
      self.core.log.add('Create Backup: [' + str(source.absolute()) + '] is a directory. Skipping.', 2)
    # If Source does not exist, throw a warning
    elif not os.path.isfile(source):
      self.core.log.add('Create Backup: [' + str(source.absolute()) + '] does not exist. Skipping.', 2)
    # If no reasons are found not to process the file, process it.
    #
    # Process target
    # If target is a directory, append source filename to target
    if target.name == target.stem:
      # Assume a directory is passed
      self.create_directory(target)
      target = target / source.name
    else:
      # Assume a file is passed
      self.create_directory(target.parent)
    # Does target exist?
    if os.access(target.parent, os.W_OK):
      # Backup location exists and is writable
      # Is source readable?
      command = ''
      if not os.access(source, os.R_OK):
        if self.core.use_sudo(task):
          command += 'sudo '
        else:
          self.core.log.add('Create Backup: Insufficient user rights on source file to create backup of [' + str(source.absolute()) + '].', 1)
          return False
          #self.core.panic() # I think one file should not be blocking, should it?
      # Verify target filename
      target = self.get_target_path_and_filename(target, task)
      # Continue bulding command
      command += 'cat ' + str(source.absolute())
      if self.core.use_gzip(task):
        command += ' | gzip '
      command += ' >> ' + str(target.absolute())
      # Execute the command
      backup_process = os.popen(command)
      response = backup_process.read().strip().split("\n")
      #self.core.log.add(command, 1)
      self.core.log.add('Backup: [' + str(source.absolute()) + '] --> [' + str(target.absolute()) + '].', 4)
      return True
    else:
      # This should not happen, should be covered by create_directory
      return False
  
  def get_target_path_and_filename(self, target, task=''):
    # Ensure were working with Pathlib object
    if type(target) is not pathlib.PosixPath:
      target = pathlib.Path(target)
    # Prepend location to target with path as prefix
    #target = target.with_name(str(target.parent).replace('/', '_') + '_' + target.name)
    # If required add datetime to filename
    if self.core.use_datetime(task):
      target = target.with_name(target.stem + '-' + self.core.get_date_time(task) + target.suffix)
    # If required, add .tar.gz to filename
    if self.core.use_gzip(task):
      target = target.with_suffix(target.suffix + '.tar.gz' )
    # return path and filename
    return target