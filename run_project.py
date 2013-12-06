#
# Sublime Text plugin to support Corona Editor
#
# Copyright (c) 2013 Corona Labs Inc. A mobile development software company. All rights reserved.
#
# MIT License - see https://raw.github.com/coronalabs/CoronaSDK-SublimeText/master/LICENSE

import sublime
import sublime_plugin

try:
  from . import _corona_utils  # P3
except:
  import _corona_utils  # P2


class ToggleBuildPanelCommand(sublime_plugin.WindowCommand):

  def run(self):
    output_panel = self.window.get_output_panel("exec")
    if output_panel.window():
      self.window.run_command("hide_panel", {"panel": "output.exec"})
    else:
      self.window.run_command("show_panel", {"panel": "output.exec"})

  def description(self):
    output_panel = self.window.get_output_panel("exec")
    if output_panel.window():
      return "Hide Build Panel"
    else:
      return "Show Build Panel"


class RunProjectCommand(sublime_plugin.WindowCommand):

  # find a main.lua file to start the Simulator with or failing that, any open Lua
  # file we can use as a place to start looking for a main.lua
  def findLuaFile(self):
    filename = self.window.active_view().file_name()
    if filename is None or not filename.endswith(".lua"):
      filename = None
      # No current .lua file, see if we have one open
      for view in self.window.views():
        if view.file_name() and view.file_name().endswith(".lua"):
          filename = view.file_name()
    return filename

  def is_enabled(self):
    return self.findLuaFile() is not None

  def run(self):
    cmd = []

    filename = self.findLuaFile()

    if filename is None:
      sublime.error_message("Can't find an open '.lua' file to determine the location of 'main.lua'")
      return
    mainlua = _corona_utils.ResolveMainLua(filename)
    if mainlua is None:
      sublime.error_message("Can't locate 'main.lua' for this project (try opening it in an editor tab)")
      return

    simulator_path, simulator_flags = _corona_utils.GetSimulatorCmd(mainlua)

    cmd = [simulator_path]
    cmd += simulator_flags
    cmd.append(mainlua)

    print(_corona_utils.PACKAGE_NAME + ": Running: " + str(cmd))

    # Save our changes before we run
    self.window.run_command("save")

    self.window.run_command('exec', {'cmd': cmd})
