#
# Sublime Text plugin to support Corona Editor
#
# Copyright (c) 2013 Corona Labs Inc. A mobile development software company. All rights reserved.
#
# MIT License - see https://raw.github.com/coronalabs/CoronaSDK-SublimeText/master/LICENSE

import sublime
import sublime_plugin
import os
import re
import threading
import subprocess
import datetime
import sys
import socket
import traceback

try:
  import queue  # P3
  coronaQueue = queue
except:
  import Queue  # P2
  coronaQueue = Queue

consoleOutputQ = None
variablesOutputQ = None
luaStackOutputQ = None
debuggerCmdQ = None

try:
  from . import _corona_utils  # P3
except:
  import _corona_utils  # P2


# determine if 'obj' is a string in both Python 2.x and 3.x
def is_string_instance(obj):
  try:
    return isinstance(obj, basestring)
  except NameError:
    return isinstance(obj, str)


statusRegion = None

# We change our behavior to avoid complications with certain CoronaSDK releases
corona_sdk_version = None
# Getting settings in certain threads locks up Sublime Text so do it just once
corona_sdk_debug = _corona_utils.GetSetting("corona_sdk_debug", False)

debugFP = None

def debug(s):
  global debugFP
  global corona_sdk_debug
  try:
    if not debugFP and corona_sdk_debug:
      if not os.path.isdir(_corona_utils.PACKAGE_USER_DIR):
        os.makedirs(_corona_utils.PACKAGE_USER_DIR)
      debugFP = open(os.path.normpath(os.path.join(_corona_utils.PACKAGE_USER_DIR, "debug.log")), "w", 1)
  except:
    pass

  # <CoronaDebuggerThread(Thread-5, started 4583960576)>
  thread_id = re.sub(r'.*\(([^,]*),.*', r'\1', str(threading.current_thread()))
  log_line = str(datetime.datetime.now()) + " (" + str(thread_id) + "): " + str(s)
  if debugFP:
    debugFP.write(log_line + "\n")
  _corona_utils.debug(log_line)


def debug_with_stacktrace(s):
  debug(s)
  for line in traceback.format_list(traceback.extract_stack()):
    debug("    "+line.strip())

HOST = ''    # Symbolic name meaning all available interfaces
PORT = 8171  # Arbitrary non-privileged port, matches Simulator

coronaDbg = None
coronaDbgThread = None
coronaBreakpointsSettings = None
coronaBreakpoints = {}


class CoronaDebuggerThread(threading.Thread):

  def __init__(self, projectDir, completionCallback, threadID=1):
    threading.Thread.__init__(self)
    self.threadID = threadID
    self.projectDir = projectDir
    self.completionCallback = completionCallback
    self.debugger_running = False
    self.conn = None
    self.socket = None
    self.recvFP = None
    self.sendFP = None

  def stop(self):
    # debug_with_stacktrace("CoronaDebuggerThread: stop")
    self.debugger_running = False

  def isRunning(self):
    # debug("CoronaDebuggerThread: isRunning (" + str(self.debugger_running) + ")")
    return self.debugger_running

  def setup(self):

    self.debugger_running = True
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    debug('Socket created')

    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    debug('Socket options set')

    try:
      self.socket.bind((HOST, PORT))
    except socket.error as msg:
      debug('Bind: ' + str(msg))
      sublime.error_message("Cannot connect to Corona Simulator (" + str(msg) + ")\n\nPerhaps there is another debugger running.\n\nTry restarting Sublime Text and stopping any Simulators.")
      return False
    else:
      debug('Socket bind complete')

    self.socket.listen(1)
    debug('Socket now listening')

    return True

  def initPUTComms(self):
    if _corona_utils.SUBLIME_VERSION < 3000:
      self.recvFP = self.conn.makefile('r', 1)
      self.sendFP = self.conn.makefile('w', 1)
    else:
      self.recvFP = self.conn.makefile(mode='rb', buffering=0, newline='\n')
      self.sendFP = self.conn.makefile(mode='wb', buffering=0, newline='\n')

  def closePUTComms(self):
    if self.sendFP is not None:
      self.sendFP.close()
      self.sendFP = None
    if self.recvFP is not None:
      self.recvFP.close()
      self.recvFP = None

  def writeToPUT(self, s):
    try:
      return self.sendFP.write(str.encode(s, 'utf-8'))
    except TypeError:
      return self.sendFP.write(s)

  def readFromPUT(self, n=None):
    try:
      if n is not None:
        result = self.recvFP.read(n)
      else:
        result = self.recvFP.readline()
    except Exception as e:
      debug("readFromPUT: " + str(e))
    else:
      return result.decode('utf-8')

  def run(self):

    # wait to accept a connection - set a short timeout so we can be interrupted if plans change
    self.socket.settimeout(1)
    debug("Socket about to accept")
    while self.socket is not None:
      try:
        self.conn, addr = self.socket.accept()
        self.conn.settimeout(None)  # Revert to no timeout once things are established
      except socket.error as msg:
        debug('Accept: ' + str(msg))
      else:
        debug('Socket accepted')
        break

    if self.socket is None:
      return

    # display client information
    debug('Connected with ' + addr[0] + ':' + str(addr[1]))

    self.initPUTComms()

    self.writeToPUT("STEP\n")

    data = self.readFromPUT()  # response like '200 OK'
    debug('data: ' + str(data))

    bpResponse = self.readFromPUT()  # response like '202 Paused /path/to/project/main.lua 3\n'
    debug('bpResponse: ' + bpResponse)

    bpMatches = re.search(r'^202 Paused\s+(.+?)\s+(\d+)$', bpResponse.strip())

    # Handle the response to the STEP command we just issued to start the PUT
    if bpMatches is not None:
      filename = bpMatches.group(1)
      line = bpMatches.group(2)

      debug("run: filename {0}, line {1}".format(filename, line))

      if not filename.endswith("main.lua"):  # we get a pause in "init.lua" if there's a syntax error in main.lua
        debugger_status("Error running main.lua")
        on_main_thread(lambda: sublime.error_message("There was an error running main.lua.\n\nCheck Console for error messages."))
        # self.writeToPUT("RUN\n") # this leaves the Simulator is a deterministic state
      else:
        debugger_status("Paused at line {0} of {1}".format(line, filename))
        on_main_thread(lambda: self.showSublimeContext(filename, int(line)))
    else:
      errMatches = re.search(r'^401 Error in Execution (\d+)$', bpResponse.strip())
      if errMatches is not None:
        size = errMatches.group(1)
        console_output("Error in remote application: ")
        console_output(self.readFromPUT(size))
      else:
        print("Corona Editor Error: ", bpResponse)
        on_main_thread(lambda: sublime.error_message("Unexpected response from Simulator:\n\n" + str(bpResponse) + "\n\nCheck Console for error messages."))

    # Restore any breakpoint we have saved (breakpoints can only be set when
    # we are running the debugger though we allow the user to think they are
    # setting breakpoints before it's started)
    on_main_thread(lambda: self.restore_breakpoints())

    self.doCommand('backtrace')
    # Skip displaying local variables on problematic releases (if we know what it is)
    if corona_sdk_version and ( int(corona_sdk_version) >= 2489 and int(corona_sdk_version) < 2517 ):
      variables_output("Local variable display disabled with this version of Corona SDK ("+corona_sdk_version+").  Try a build after 2515")
    else:
      self.doCommand('locals')

    while self.debugger_running:
      cmd = debuggerCmdQ.get()
      self.performCommand(cmd)
      debuggerCmdQ.task_done()

    # clean up on PUT termination
    on_main_thread(lambda: self.completionCallback(self.threadID))

    debug('CoronaDebuggerThread: ends')

  def restore_breakpoints(self):
    global coronaBreakpointsSettings
    if coronaBreakpointsSettings is None:
      coronaBreakpointsSettings = sublime.load_settings(_corona_utils.PACKAGE_NAME + ".breakpoints")
    if coronaBreakpointsSettings is not None:
      debug("coronaBreakpointsSettings: "+str(coronaBreakpointsSettings))
      if coronaBreakpointsSettings.get('breakpoints') is not None:
        # Restore previously set breakpoints(use a local rather than "coronaBreakpoints"
        # so we don't toggle any existing ones off again)
        breakpoints = coronaBreakpointsSettings.get('breakpoints')
        debug("breakpoints: "+str(breakpoints))
        for filename in breakpoints:
          for view in sublime.active_window().views():
            debug("view.name: " + str(view.file_name()) + "; filename: " + filename)
            if view.file_name() == filename:
              breakpoints[filename] = sorted(set(breakpoints[filename]))  # sort and unique
              for line in breakpoints[filename]:
                sublime.active_window().run_command("corona_debugger", {"cmd": "setb", "arg_filename": filename, "arg_lineno": line, "arg_toggle": False})

  def getBreakpointParameters(self, cmdLine):
    cmd = ""
    filename = ""
    linenum = 0

    bpMatches = re.search(r'^(\w+)\s+(.+?)\s+(\d+)$', cmdLine)
    if bpMatches is not None:
      cmd = bpMatches.group(1)
      filename = bpMatches.group(2)
      linenum = bpMatches.group(3)
    else:
      debugger_status("Could not parse breakpoint expression: " + cmdLine)

    return cmd, filename, linenum

  def getParameters(self, cmdLine):
    cmd = ""
    parameter = ""

    cmdMatches = re.search(r'^(\w+)\s*(.*)$', cmdLine)
    if cmdMatches is not None:
      cmd = cmdMatches.group(1)
      parameter = cmdMatches.group(2)
    else:
      debugger_status("Could not parse command: " + cmdLine)

    return cmd, parameter

  def getAck(self, cmd):
    ack = None
    try:
      self.writeToPUT(cmd.upper() + "\n")
      ack = self.readFromPUT().strip()
    except Exception as e:
      debug("Exception reading network: "+str(e))
    else:
      debug("getAck: " + ack)
      if ack != "200 OK":
        debug("*** Sent '{0}' got unexpected '{1}'".format(cmd, ack))

    return ack

  def doCommand(self, cmd):
    debuggerCmdQ.put(cmd, 1)

  def performCommand(self, cmd):
    try:
      verb = cmd.partition(" ")[0].lower()
      if verb in ["run", "step", "over"]:
        self.doContinue(cmd)
      elif verb in ["backtrace", "locals"]:
        self.doGetData(cmd)
      elif verb in ["setb", "delb"]:
        self.doSetBreakpoint(cmd)
      elif verb in ["dump"]:
        self.doDump(cmd)
      elif verb in ["exit"]:
        self.doExit(cmd)
      elif verb in ["frame"]:
        debugger_status("Command '" + verb + "' not implemented")
      else:
        debugger_status("Unhandled command: {0}".format(cmd))
    except Exception as e:
      debug("Exception performing command: "+str(e))
      type_, value_, traceback_ = sys.exc_info()
      for line in traceback.format_tb(traceback_):
        debug("    "+line.strip())

  def doDump(self, cmd):
    cmdtype, variable_name = self.getParameters(cmd)
    debug("doDump: "+cmdtype+" "+variable_name)
    if variable_name:
      # Note the space after "return" matters
      # self.writeToPUT("EXEC return (" + variable_name + ")\n")
      self.writeToPUT("DUMP return (" + variable_name + ")\n")
      dmpResponse = self.readFromPUT().strip()
      debug("dmpResponse: " + dmpResponse)
      dataMatches = re.search(r'^(\d+)[^0-9]*(\d+)$', dmpResponse)
      if dataMatches is not None:
        status = dataMatches.group(1)
        length = int(dataMatches.group(2))
        if status == "200":
          if length == 0:
            debugger_status("No "+cmd)
          else:
            dataStr = ""
            while len(dataStr) < length:
              dataStr += self.readFromPUT(int(length - len(dataStr)))

            dataStr = dataStr
            debug('dmpData: ' + dataStr)
            sublime.message_dialog(dataStr)
      else:
        debugger_status("Error getting variable value: " + dmpResponse)
    else:
      debugger_status("Usage: DUMP variable")

  def doSetBreakpoint(self, cmd):
    global coronaBreakpoints
    cmdtype, filename, linenum = self.getBreakpointParameters(cmd)
    if filename and linenum:
      self.writeToPUT(cmdtype.upper() + " " + filename + " " + linenum + "\n")
      bpResponse = self.readFromPUT().strip()
      debug("bpResponse: " + bpResponse)
      if bpResponse == "200 OK":
        action = "set" if cmdtype.upper() == "SETB" else "removed"
        debugger_status("Breakpoint {2} at {0}:{1}".format(filename, linenum, action))
      else:
        debugger_status("Error setting breakpoint: " + bpResponse)
    else:
      debugger_status("Usage: [SETB|DELB] filename linenum")

  def doExit(self, cmd):
    debug("CoronaDebugger: doExit")
    try:
      # self.closePUTComms()
      if self.conn is not None:
        # debug("doExit: conn.close")
        self.conn.close()
        self.conn = None
      if self.socket is not None:
        # debug("doExit: socket.close")
        # self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        self.socket = None
    except Exception as e:
      debug("Exception closing down coprocess: "+str(e))
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(exc_type, fname, exc_tb.tb_lineno)

  def doGetData(self, cmd):
    # backtrace and locals overload the 200 response with a length so we need
    # to send them manually rather than use getAck()
    self.writeToPUT(cmd.upper() + "\n")
    dataResponse = self.readFromPUT().strip()
    debug("dataResponse: " + dataResponse)
    dataMatches = re.search(r'^(\d+)[^0-9]*(\d+)$', dataResponse)
    if dataMatches is not None:
      status = dataMatches.group(1)
      length = int(dataMatches.group(2))
      if status == "200":
        if length == 0:
          debugger_status("No "+cmd)
        else:
          dataStr = ""
          while len(dataStr) < length:
            dataStr += self.readFromPUT(int(length - len(dataStr)))
          if cmd == 'backtrace':
            # Tidy up backtrace
            if dataStr.find('platform/resources/init.lua:') != -1 or dataStr.find('?:0') != -1:
              # Stopped in internal code
              dataStr = re.sub(r' at .*platform/resources/init\.lua:[0-9]*', ' at <internal location>', dataStr)
              dataStr = re.sub(r' at \?:0', ' at <internal location>', dataStr)
            # Elide the project directory from any frames that contain it
            # debug("projectDir: " + self.projectDir + os.path.sep)
            dataStr = re.sub("(?i)" + re.escape('@' + self.projectDir + os.path.sep), '', dataStr)
            stack_output(cmd.title() + ":\n" + dataStr)
          else:
            dataStr = re.sub("(?i)" + re.escape('@' + self.projectDir + os.path.sep), '', dataStr)
            variables_output(cmd.title() + ":\n" + dataStr)
      else:
        debugger_status("Error response from '" + cmd + "' (" + dataResponse + ")")
    else:
      debugger_status("Unparsable response from '" + cmd + "' (" + dataResponse + ")")

  def activateViewWithFile(self, filename, line):
    debug("activateViewWithFile: "+str(filename) + ":" + str(line))
    window = sublime.active_window()
    for view in window.views():
      if view.name() == filename:
        window.focus_view(view)
        break

    if window.active_view().file_name() != filename:
      # didn't find an existing view, open a new one
      filename = filename + ":" + str(line)
      view = window.open_file(filename, sublime.ENCODED_POSITION)
      window.focus_view(view)

  def showSublimeContext(self, filename, line):
    debug("showSublimeContext: "+str(filename) + " : " + str(line))
    console_output("@@@ Stopped at "+str(filename.replace(self.projectDir+"/", "")) + ":" + str(line) +" @@@")
    window = sublime.active_window()
    if window:
      window.focus_group(0)
      view = window.active_view()
      # debug("showSublimeContext: view: " + str(view) + "; size: " + str(view.size()))
      # testing that "view" is not None is insufficient here
      if view is not None and view.size() >= 0:
        filename = os.path.join(self.projectDir, filename)
        if view.file_name() != filename:
          self.activateViewWithFile(filename, line)

        window.run_command("goto_line", {"line": line})
        # view might have changed
        view = window.active_view()
        mark = [view.line(view.text_point(line - 1, 0))]
        view.erase_regions("current_line")  # removes it if we change files
        view.add_regions("current_line", mark, "current_line", "dot", sublime.DRAW_OUTLINED)  # sublime.HIDDEN | sublime.PERSISTENT)
      else:
        debug("No current view")

  # Handle category of commands that move the execution pointer ("run", "step", "over")
  def doContinue(self, cmd):
    if cmd == "run":
      stack_output("Running ...")
      variables_output("Running ...")
      debugger_status("Running ...")
      on_main_thread(lambda: sublime.active_window().active_view().erase_regions("current_line"))  # we wont be back to erase the current line marker so do it here
      on_main_thread(lambda: console_output("@@@ Running - Shift+F10 to stop @@@"))

    self.getAck(cmd)
    response = self.readFromPUT()
    if response is None or response == "":
      debugger_status("Program finished")
      self.debugger_running = False
      return

    statusMatches = re.search(r'^(\d+)', response.strip())
    status = statusMatches.group(0)
    debug("Status: " + status)
    if status == "202":
      bpMatches = re.search(r'^202 (\w+)\s+(.+)\s+(\d+)$', response)
      if bpMatches is not None:
        label = bpMatches.group(1)
        filename = bpMatches.group(2)
        line = bpMatches.group(3)
        debug("doContinue: label: {0}, filename {1}, line {2} ({3})".format(label, filename, line, response))
        if label == "Error":
          label = "Runtime script error"
        if filename and line:
          if filename == "=?" or filename == "init.lua" or filename == "shell.lua":
            debugger_status(label + " at internal location")
          else:
            debugger_status(label + " at line " + line + " of " + filename)
            on_main_thread(lambda: self.showSublimeContext(filename, int(line)))
        else:
          debugger_status(label + " response: " + response)
      else:
        debugger_status("Unexpected 202 response: " + response)
    elif status == "203":
      bpwMatches = re.search(r'^203 Paused\s+(.+)\s+(\d+)\s+(\d+)$', response)
      if bpwMatches is not None:
        file = bpwMatches.group(1)
        line = bpwMatches.group(2)
        watchIndex = bpwMatches.group(3)
        if file and line and watchIndex:
          print(_corona_utils.PACKAGE_NAME + ": watches not implemented")
          # debugger_status("Paused at file " + file + " line " + line + " (watch expression " + watchIndex + ": [" + watches[watchIndex] + "])")
      else:
        debugger_status("Unexpected 203 response: " + response)
    elif status == "401":
      errMatches = re.search(r'^401 Error in Execution (\d+)$', response)
      if errMatches:
        size = errMatches.group(1)
        if size:
          console_output("Error in remote application: ")
          console_output(self.readFromPUT(int(size)))

  def doRun(self):
    self.doContinue("RUN")

  def doStep(self):
    self.doContinue("STEP")


class CoronaDebuggerListener(sublime_plugin.EventListener):
  def on_post_save(self, view):
    debug("CoronaDebuggerListener:on_post_save: " + view.file_name())
    if (coronaDbg is not None and coronaDbg.isRunning()) and view.file_name().endswith(".lua"):
      if sublime.ok_cancel_dialog(view.file_name() + " has changed.  Do you want to restart the Debugger?", "Restart"):
        sublime.set_timeout(lambda: sublime.active_window().run_command("corona_debugger", {"cmd": "restart"}), 0)


class CoronaDebuggerCommand(sublime_plugin.WindowCommand):

  view = None

  # def __init__(self, *args, **kw):
  #  self.closeWindowPanes()

  def is_enabled(self):
    view = self.window.active_view()
    if view is not None:
      s = view.sel()[0]
      return view.match_selector(s.a, "source.lua - entity")
    else:
      return False

  def run(self, cmd=None, arg_filename=None, arg_lineno=None, arg_toggle=True):
    debug("CoronaDebuggerCommand: " + cmd)
    global coronaDbg
    global corona_sdk_version
    global corona_sdk_debug
    self.view = self.window.active_view()

    if self.view is None:
      sublime.error_message("Cannot find an active view.  You may need to restart Sublime Text.")
      return

    # if we aren't started yet and a step is asked for, do a start
    if (coronaDbg is None or not coronaDbg.isRunning()) and cmd in ['run', 'step', 'over']:
      cmd = "start"

    if cmd == "start":
      if corona_sdk_debug:
        # Show Sublime Console
        self.window.run_command("show_panel", {"panel": "console"})
        # sublime.log_commands(True)

      # Hide the build panel (since the "Console" pane duplicates it)
      self.window.run_command("hide_panel", {"panel": "output.exec"})

      if coronaDbg is not None:
        debug("Cleaning up debugger thread")
        coronaDbg.join()
        coronaDbg = None

      self.saved_layout = self.window.get_layout()

      # Figure out where the PUT and the Simulator are
      filename = self.window.active_view().file_name()
      if filename is None or not filename.endswith(".lua"):
        filename = None
        # No current .lua file, see if we have one open
        for view in self.window.views():
          if view.file_name() and view.file_name().endswith(".lua"):
            if filename is None or not filename.endswith("main.lua"):  # prefer a 'main.lua' if there is one
              filename = view.file_name()

      if filename is None:
        sublime.error_message("Can't find an open '.lua' file to determine the location of 'main.lua'")
        return
      mainlua = _corona_utils.ResolveMainLua(filename)
      if mainlua is None:
        sublime.error_message("Can't locate 'main.lua' for this project (try opening it in an editor tab)")
        return
      self.window.open_file(mainlua)  # make sure main.lua is open as that's the first place we'll stop
      projectDir = os.path.dirname(mainlua)
      if not projectDir:
        sublime.error_message("Cannot find 'main.lua' for '"+self.view.file_name()+"'.  This does not look like a Corona SDK app")
        return

      dbg_path, dbg_flags, dbg_version = _corona_utils.GetSimulatorCmd(mainlua, True)
      dbg_cmd = [dbg_path]
      dbg_cmd += dbg_flags
      dbg_cmd.append(mainlua)
      debug("debugger cmd: " + str(dbg_cmd))

      debug("dbg_version: " + str(dbg_version))
      if dbg_version:
        corona_sdk_version = dbg_version.rpartition(".")[2]
        debug("corona_sdk_version: " + str(corona_sdk_version))

      global consoleOutputQ, variablesOutputQ, luaStackOutputQ, debuggerCmdQ
      consoleOutputQ = coronaQueue.Queue()
      variablesOutputQ = coronaQueue.Queue()
      luaStackOutputQ = coronaQueue.Queue()
      debuggerCmdQ = coronaQueue.Queue()

      coronaDbg = CoronaDebuggerThread(projectDir, self.debuggerFinished)
      if coronaDbg.setup():
        if self.window.num_groups() == 1:
          self.initializeWindowPanes()
        else:
          # Clear the existing windows
          variables_output(' ')
          stack_output(' ')
        self.window.focus_group(0)
        RunSubprocess(dbg_cmd, self.window)
        coronaDbg.start()

    elif cmd == "restart":
      if coronaDbg is not None:
        self.window.run_command("corona_debugger", {"cmd": "exit"})
      sublime.set_timeout(lambda: self.window.run_command("corona_debugger", {"cmd": "start"}), 0)

    elif cmd == "exit":
      debugger_status("exiting debugger...")
      StopSubprocess()
      if coronaDbg is None:
        self.closeWindowPanes()
      else:
        coronaDbg.doCommand(cmd)
        coronaDbg.stop()
        coronaDbg.join()
        coronaDbg = None
    elif cmd in ["run", "step", "over"]:
      coronaDbg.doCommand(cmd)
      coronaDbg.doCommand('backtrace')
      if not corona_sdk_version or ( int(corona_sdk_version) < 2489 or int(corona_sdk_version) > 2515 ):
        coronaDbg.doCommand('locals')
    elif cmd == "dump":
      self.dumpVariable()
    elif cmd == "setb":
      # toggle a breakpoint at the current cursor position
      if arg_filename is None:
        filename = self.view.file_name()
        (lineno, col) = self.view.rowcol(self.view.sel()[0].begin())
        lineno += 1
      else:
        filename = arg_filename
        lineno = int(arg_lineno)

      if self.toggle_breakpoint(filename, lineno, arg_toggle):
        cmd = "setb"
      else:
        cmd = "delb"

      cmd += " " + '"' + filename + '"'
      cmd += " " + str(lineno)
      debug("setb: " + cmd)

      if coronaDbg is not None:
        coronaDbg.doCommand(cmd)

    else:
      print("CoronaDebuggerCommand: Unrecognized command: " + cmd)

  def debuggerFinished(self, threadId):
    debug("debuggerFinished: threadId: " + str(threadId))
    self.closeWindowPanes()
    # self.window.run_command("corona_debugger", {"cmd": "exit"})

  def dumpVariable(self):
    # If something's selected use that, otherwise prompt the user for a variable name
    selection = self.view.sel()[0]
    if selection:
      selected_word = self.view.substr(self.view.word(selection))
      if selected_word and selected_word != "":
        self.doDumpVariable(selected_word)
    else:
      self.window.show_input_panel("Variable name or expression:", "", self.doDumpVariable, None, None)

  def doDumpVariable(self, variable_name):
      if coronaDbg is not None:
        coronaDbg.doCommand("dump " + variable_name)
      else:
        sublime.error_message("Corona Debugger is not running")

  def toggle_breakpoint(self, filename, lineno, toggle=True):
    global coronaBreakpointsSettings
    global coronaBreakpoints
    result = True

    if coronaBreakpointsSettings is None:
      coronaBreakpointsSettings = sublime.load_settings(_corona_utils.PACKAGE_NAME + ".breakpoints")

    bpId = self.new_breakpoint_id(filename, lineno)
    debug("bpId: " + bpId)
    if filename not in coronaBreakpoints:
      coronaBreakpoints[filename] = []
    if lineno in coronaBreakpoints[filename] and toggle:
      # we're unsetting the breakpoint
      debug("toggle_breakpoint: unsetting breakpoint")
      coronaBreakpoints[filename].remove(lineno)
      view = self.view_for_file(filename)
      if view is not None:
        view.erase_regions(bpId)
      result = False
    else:
      debug("toggle_breakpoint: setting breakpoint in '"+filename+"' at "+str(lineno) )
      if lineno not in coronaBreakpoints[filename]:
        coronaBreakpoints[filename].append(int(lineno))
      view = self.view_for_file(filename)
      if view is not None:
        mark = [view.line(view.text_point(lineno - 1, 0))]
        if _corona_utils.SUBLIME_VERSION < 3000:
          # Path for icons is "Packages/Theme - Default/"
          view.add_regions(bpId, mark, "breakpoint", "../"+_corona_utils.PACKAGE_NAME+"/CoronaBP", sublime.HIDDEN)
        else:
          view.add_regions(bpId, mark, "breakpoint", "Packages/"+_corona_utils.PACKAGE_NAME+"/CoronaBP.png", sublime.HIDDEN)
      result = True

    # Save the breakpoints for posterity
    debug("coronaBreakpoints: " + str(coronaBreakpoints))
    coronaBreakpointsSettings.set("breakpoints", coronaBreakpoints)
    sublime.save_settings(_corona_utils.PACKAGE_NAME + ".breakpoints")

    return result

  def view_for_file(self, filename):
    for view in sublime.active_window().views():
      if view.file_name() == filename:
        return view
    return None

  def new_breakpoint_id(self, filename, lineno):
    return filename + str(lineno)

  def initializeWindowPanes(self):
    self.window.set_layout({"cols":[0,0.6,1],"rows":[0,0.5,0.7,1],"cells":[[0,0,2,1],[0,1,2,2],[0,2,1,3],[1,2,2,3]]})

    self.window_panes = [{'group': 0, 'tag': 'code', 'title': ''},
                         {'group': 1, 'tag': 'console', 'title': 'Console'},
                         {'group': 2, 'tag': 'variables', 'title': 'Variables'},
                         {'group': 3, 'tag': 'stack', 'title': 'Lua Stack'}]

    for w in self.window_panes:
      views = self.window.views_in_group(w['group'])
      if len(views) is 0:
        view = self.window.new_file()
        view.set_name(w['title'])
        view.settings().set('word_wrap', True)
        view.settings().set('_corona_debugger_pane', True)
        if view.name() != 'Console':
          # Set the syntax coloring for the Variables and Stack panes
          # to CoronaSDKLua as that works well
          view.set_syntax_file('Packages/' + _corona_utils.PACKAGE_NAME + '/CoronaSDKLua.tmLanguage')
        view.set_read_only(True)
        view.set_scratch(True)
        view.run_command("toggle_setting", {"setting": "line_numbers"})
        self.window.set_view_index(view, w['group'], 0)
        # outputToPane(w['title'], "this is " + w['title'])

  def closeWindowPanes(self):
    closed_panes = False # try to only close panes we created
    if self.window.num_groups() > 1:
      for view in self.window.views():
        if not view.settings().get('_corona_debugger_pane'):
          continue
        closed_panes = True
        group, index = self.window.get_view_index(view)
        if group > 0:
          debug("Closing: " + view.name())
          self.window.focus_view(view)
          self.window.run_command("close_file")
      if closed_panes:
        # print("saved_layout: " + str(self.saved_layout))
        self.window.run_command("set_layout", {"cells": [[0, 0, 1, 1]], "cols": [0.0, 1.0], "rows": [0.0, 1.0]})
      # Always do this, debugger may have been running in one pane
      self.view.erase_regions("current_line")


def debugger_status(msg):
  debug("debugger_status: " + msg)
  sublime.set_timeout(lambda: sublime.status_message(msg), 0)


def on_main_thread(callee):
  sublime.set_timeout(callee, 0)


def console_output(text):
  if consoleOutputQ is not None:
    # if the line doesn't end with a newline, add one
    if text[-1] != "\n":
      text += "\n"
    # Remove cruft from Simulator output (also CRs which are coming from somewhere)
    text = re.sub(r'Corona Simulator\[\d+:\d+\] ', '', text.replace("\r", ""), 1)
    consoleOutputQ.put(text, 1)
    sublime.set_timeout(lambda: outputToPane('Console', None, False), 0)


def variables_output(text):
  if variablesOutputQ is not None:
    # if the line doesn't end with a newline, add one
    if text[-1] != "\n":
      text += "\n"
    variablesOutputQ.put(text, 1)
    sublime.set_timeout(lambda: outputToPane('Variables', None, True), 0)


def stack_output(text):
  if luaStackOutputQ is not None:
    # if the line doesn't end with a newline, add one
    if text[-1] != "\n":
      text += "\n"
    luaStackOutputQ.put(text, 1)
    sublime.set_timeout(lambda: outputToPane('Lua Stack', None, True), 0)


def outputToPane(name, text, erase=True):
  debug("outputToPane: name: '" + name + "' text: " + str(text))
  global statusRegion
  queueing = False
  if text is None:
    if name == "Variables":
      subProcOutputQ = variablesOutputQ
    elif name == "Lua Stack":
      subProcOutputQ = luaStackOutputQ
    else:
      subProcOutputQ = consoleOutputQ
    text = subProcOutputQ.get()
    queueing = True
  debug("outputToPane: name: '" + name + "' text: " + text)
  window = sublime.active_window()
  for view in window.views():
    # only reload view if text has changed
    if view.name() == name and view.substr(sublime.Region(0, view.size())) != text:
      view.set_read_only(False)
      # Remove the last status we output
      if statusRegion and "@@@ " in text:
          view.sel().clear()
          view.sel().add(view.full_line(statusRegion))
          view.run_command("right_delete")
          statusRegion = None
      if _corona_utils.SUBLIME_VERSION < 3000:
        edit = view.begin_edit()
        # print("name: ", name, "size: ", view.size())
        if erase:
          view.erase(edit, sublime.Region(0, view.size()))
          view.insert(edit, 0, text)
        else:
          view.insert(edit, view.size(), text)
        view.end_edit(edit)
      else:  # It's ST3
        if erase:
          view.run_command("select_all")
          view.run_command("right_delete")
        view.run_command('append', {'characters': text})

      view.set_read_only(True)
      # view.set_viewport_position((0, view.size())) # scroll to the end
      view.show(view.size(), True)  # scroll to the end, works better on Windows

      # Highlight status line and remember where it is so it can be removed later
      if "@@@ " in text:
        line = view.rowcol(view.size())[0]
        pt = view.text_point(line-1, 0)
        statusRegion = view.line(sublime.Region(pt))
        view.sel().clear()
        view.sel().add(view.line(statusRegion))
        mark = [sublime.Region(view.size() - 1, view.size())]
        if _corona_utils.SUBLIME_VERSION < 3000:
          # Path for icons is "Packages/Theme - Default/"
          view.add_regions('dbg', mark, "debugger", "../"+_corona_utils.PACKAGE_NAME+"/CoronaBP", sublime.HIDDEN)
        else:
          view.add_regions('dbg', mark, "debugger", "Packages/"+_corona_utils.PACKAGE_NAME+"/CoronaBP.png", sublime.HIDDEN)
  if queueing:
    subProcOutputQ.task_done()


class CoronaSubprocessThread(threading.Thread):

  def __init__(self, cmd, completionCallback=None, window=None, threadID=1):
    threading.Thread.__init__(self)
    self.threadID = threadID
    self.cmd = cmd
    self.completionCallback = completionCallback
    self.window = window
    self.proc = None

  def terminate(self):
    if self.proc.poll() is None:
      self.proc.terminate()

  def run(self):
    debug("Running: " + str(self.cmd))
    if sublime.platform() == "windows":
      closeFDs = False
    else:
      closeFDs = True

    self.proc = subprocess.Popen(self.cmd, bufsize=0, close_fds=closeFDs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while self.proc.poll() is None:
        try:
          data = self.proc.stdout.readline().decode('UTF-8')
          # this isn't the same as "print()": sys.stdout.write(data)
          # print("Read: " + data)
          console_output(data)
        except IndexError as e:
          break  # we get this when the child process has terminated
        except Exception as e:
          console_output("Exception reading from coprocess: "+str(e))

    on_main_thread(lambda: self.completionCallback(self.threadID, self.window))

    debug("CoronaSubprocessThread: ends (proc.poll(): " + str(self.proc.poll()) + ")")


def CompleteSubprocess(threadID, window):
  debug("CompleteSubprocess: called (" + str(threadID) + ")")
  # debug("CompleteSubprocess: window " + str(window))
  # window.run_command("corona_debugger", {"cmd": "exit"})


def RunSubprocess(cmd, window):
  global coronaDbgThread
  coronaDbgThread = CoronaSubprocessThread(cmd, CompleteSubprocess, window)
  coronaDbgThread.start()


def StopSubprocess():
  global coronaDbgThread
  debug("StopSubprocess: " + str(coronaDbgThread))
  if coronaDbgThread is not None and coronaDbgThread.is_alive():
    coronaDbgThread.terminate()
    coronaDbgThread.join()
