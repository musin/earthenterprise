#!/usr/bin/python2.6
#
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Utility methods."""

import os
import pexpect
import pexpect.fdpexpect
import subprocess
import sys


class OsCommandError(Exception):
  """Thrown if os command fails."""
  pass


def ExecuteCmd(os_cmd, use_shell=False):
  """Execute os command and log results."""
  print "Executing: {}".format(os_cmd if use_shell else ' '.join(os_cmd))
  process = None
  try:
    process = subprocess.Popen(os_cmd, stdin=None, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, bufsize=0, shell=use_shell)
    stdout_stream = pexpect.fdpexpect.fdspawn(process.stdout)
    stderr_stream = pexpect.fdpexpect.fdspawn(process.stderr)
    # process.returncode is None until the subprocess completes. Then, it gets
    # filled in with the subprocess exit code.
    while process.returncode is None:
      if stdout_stream.isalive():
        try:
          stdout_chunk = stdout_stream.read_nonblocking(timeout=0)
          sys.stdout.write(stdout_chunk)
        except (pexpect.TIMEOUT, pexpect.EOF):
          pass
      if stderr_stream.isalive():
        try:
          stderr_chunk = stderr_stream.read_nonblocking(timeout=0)
          sys.stderr.write(stderr_chunk)
        except (pexpect.TIMEOUT, pexpect.EOF):
          pass
      process.poll()
    if process.returncode: # Assume a non-zero exit code means error:
      return "Unable to execute %s" % os_cmd
    return process.returncode
  except Exception, e:
    print "FAILED: %s" % e.__str__()
    raise OsCommandError()
  finally:
    # Terminate sub-process on keyboard interrupt or other exception:
    if process is not None and process.returncode is None:
      process.terminate()
