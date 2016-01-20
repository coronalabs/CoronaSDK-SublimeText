#
# Sublime Text plugin to support Corona Editor
#
# Copyright (c) 2013 Corona Labs Inc. A mobile development software company. All rights reserved.
#
# MIT License - see https://raw.github.com/coronalabs/CoronaSDK-SublimeText/master/LICENSE

# Note: the leading underscore on the name of this module forces Sublime Text to load it first which
# prevents it being loaded more than once (once when it's first imported, e.g. by about.py, and then
# again when it comes up in the load order)

import sublime
import os
import re
import threading
import io
import subprocess
import sys

# Define "check_output" for Python <= 2.6 (ST2 uses this)
if "check_output" not in dir( subprocess ):
  def f(*popenargs, **kwargs):
    if 'stdout' in kwargs:
      raise ValueError('stdout argument not allowed, it will be overridden.')
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
      cmd = kwargs.get("args")
      if cmd is None:
        cmd = popenargs[0]
      raise subprocess.CalledProcessError(retcode, cmd)
    return output
  subprocess.check_output = f

SUBLIME_VERSION = "not set"
PLUGIN_PATH = "not set"
PACKAGE_NAME = "not set"
PACKAGE_DIR = "not set"
PACKAGE_USER_DIR = "not set"
ST_PACKAGE_PATH = "not set"
_corona_sdk_debug = False

# In Sublime Text 3 most APIs are unavailable until a module level function is called (fortunately
# sublime.version() is available so we can correctly fake things in Sublime Text 2; see about.py)
SUBLIME_VERSION = 3000 if sublime.version() == '' else int(sublime.version())


def GetSetting(key,default=None):
  # repeated calls to load_settings return same object without further disk reads
  debug("GetSetting: " + str(key) + " (default: " + str(default) + ")")
  settings = sublime.load_settings('Corona Editor.sublime-settings')
  debug("GetSetting: value from CE settings: " + str(settings.get(key, default)))
  # If we don't have a value for this preference in the Corona Editor settings, look in the view for a value
  # (this happens if the preference is set in the main Sublime Text preference file instead of the Corona Editor file)
  if not settings.get(key, default) and sublime and sublime.active_window() and sublime.active_window().active_view():
    debug("GetSetting: getting value from view: " + str(sublime.active_window().active_view()))
    settings = sublime.active_window().active_view().settings()

  value = settings.get(key, default)

  if not value:
    debug("GetSetting: no value for preference '" + str(key) + "' found (using default '"+ str(default) + "')")

  return value


def debug(*args):
  global _corona_sdk_debug
  if _corona_sdk_debug:
    print("Corona Editor: ", '\t'.join(map(str, args)))


InitializedEvent = threading.Event()


def Init():
  global SUBLIME_VERSION
  global PLUGIN_PATH
  global PACKAGE_NAME
  global PACKAGE_DIR
  global PACKAGE_USER_DIR
  global ST_PACKAGE_PATH
  global _corona_sdk_debug

  # Always look for "corona_sdk_debug" in 'Corona Editor.sublime-settings'
  settings = sublime.load_settings('Corona Editor.sublime-settings')
  _corona_sdk_debug = settings.get("corona_sdk_debug", False)

  print("Corona Editor: Init")
  debug("Python: " + str(sys.version))

  PLUGIN_PATH = os.path.dirname(os.path.realpath(__file__))
  if PLUGIN_PATH.lower().endswith('coronasdk-sublimetext'):
    if SUBLIME_VERSION < 3000:
      PLUGIN_PATH = os.path.expanduser('~/Library/Application Support/Sublime Text 2/Packages/Corona Editor')
    else:
      PLUGIN_PATH = os.path.expanduser('~/Library/Application Support/Sublime Text 3/Packages/Corona Editor')
  debug("PLUGIN_PATH: " + PLUGIN_PATH)

  PACKAGE_NAME = os.path.basename(PLUGIN_PATH) if SUBLIME_VERSION < 3000 else os.path.basename(PLUGIN_PATH).replace(".sublime-package", "")
  debug("PACKAGE_NAME: " + PACKAGE_NAME)

  # This is the actual package dir on ST2 and the "unpacked" package dir on ST3 ("~/Library/Application Support/Sublime Text 2/Packages")
  PACKAGE_DIR = os.path.join(sublime.packages_path(), PACKAGE_NAME)
  debug("PACKAGE_DIR: " + PACKAGE_DIR)

  # This is the user dir on ST
  PACKAGE_USER_DIR = os.path.join(sublime.packages_path(), 'User', PACKAGE_NAME)
  debug("PACKAGE_USER_DIR: " + PACKAGE_USER_DIR)

  # This is the faux path used by various Sublime Text functions ("Packages/CoronaSDK/")
  ST_PACKAGE_PATH = "Packages/" + PACKAGE_NAME + "/"
  debug("ST_PACKAGE_PATH: " + ST_PACKAGE_PATH)

  # This allows other threads to wait until this code has run
  InitializedEvent.set()


# This is run by ST3 after the plugins have loaded (and the ST API is ready for calls)
def plugin_loaded():
  Init()

# This fakes the above functionality on ST2
if SUBLIME_VERSION < 3000:
  Init()


# Return the path to the Simulator for the current project and platform
# First we look in any build.settings file in the project, then we look
# for a user preference, then we pick a platform appropriate default
def GetSimulatorCmd(mainlua=None, debug=False):
  platform = sublime.platform()
  arch = sublime.arch()
  view = sublime.active_window().active_view()

  simulator_path = ""
  simulator_flags = []
  simulator_version = GetSetting("corona_sdk_version", None)

  if mainlua is not None:
    simulator_path = GetSimulatorPathFromBuildSettings(mainlua)
    if simulator_path is None:
      simulator_path = GetSetting("corona_sdk_simulator_path", None)

  if platform == "osx":
    if simulator_path is None:
      simulator_path = GetLatestDailyBuildSimulatorPath()
    if simulator_path is None:
      simulator_path = "/Applications/CoronaSDK/Corona Simulator.app"
    if simulator_path.endswith(".app"):
      simulator_path += "/Contents/MacOS/Corona Simulator"
    simulator_flags = ["-singleton", "1"]
    if not GetSetting("corona_sdk_simulator_show_console", False):
      simulator_flags += ["-no-console", "1"]
    if debug:
      simulator_flags.append("-debug")
      simulator_flags.append("1")
      simulator_flags.append("-project")
    if os.path.isfile(simulator_path) and os.access(simulator_path, os.X_OK):
      simulator_version = str(subprocess.check_output(['defaults', 'read', os.path.join(os.path.dirname(simulator_path), '../Info.plist'), 'CFBundleVersion'], stderr=subprocess.STDOUT).decode('utf8').strip())
  elif platform == 'windows':
    if simulator_path is None:
      if arch == "x64":
        simulator_path = "C:\\Program Files (x86)\\Corona Labs\\Corona SDK\\Corona Simulator.exe"
      else:
        simulator_path = "C:\\Program Files\\Corona Labs\\Corona SDK\\Corona Simulator.exe"
    simulator_flags = ["/singleton"]
    if not GetSetting("corona_sdk_simulator_show_console", False):
      simulator_flags += ["/no-console"]
    if debug:
      simulator_flags.append("/debug")

  # Can we find an executable file at the path
  if not os.path.isfile(simulator_path) or not os.access(simulator_path, os.X_OK):
    sublime.error_message("Cannot find executable Corona Simulator at path '{0}'\n\nYou can set the user preference 'corona_sdk_simulator_path' to the location of the Simulator.".format(simulator_path))
    return None, None, None

  return simulator_path, simulator_flags, simulator_version


# Find the highest numbered CoronaSDK directory in /Applications
def GetLatestDailyBuildSimulatorPath():
  dirs = os.listdir("/Applications")

  # Find the highest numbered Daily Build
  maxBuildNum = 0
  buildNum = 0
  latestSDK = ""
  for entry in dirs:
    if entry.startswith("CoronaSDK-"):
      result = re.findall(r'\d+', entry)
      if len(result) > 0:
        buildNum = int(re.findall(r'\d+', entry)[0])
      if buildNum > maxBuildNum:
        maxBuildNum = buildNum
        latestSDK = "/Applications/" + entry

  if len(latestSDK) > 0:
    return  latestSDK + "/Corona Simulator.app"
  else:
    return None


# Given a path to a main.lua file, see if there's a "corona_sdk_simulator_path" setting in
# the corresponding build.settings file
def GetSimulatorPathFromBuildSettings(mainlua):
  simulator_path = None
  project_path = os.path.dirname(mainlua)
  build_settings = os.path.join(project_path, "build.settings")
  bs_contents = None
  if os.path.isfile(build_settings):
    try:
      try: # see if we're in P3
        with open(build_settings, "r", encoding="utf-8") as bs_fd:
          bs_contents = bs_fd.read()
      except: # nope, try a P2 idiom
        with io.open(build_settings, "r", encoding="utf-8") as bs_fd:
          bs_contents = bs_fd.read()
    except IOError:
      pass  # we don't care if the file doesn't exist

  # debug("bs_contents: ", str(bs_contents))
  if bs_contents is not None:
    # Remove comments
    bs_contents = re.sub(r'--.*', '', bs_contents)
    # Note we can't use a Python r'' string here because we then can't escape the single quotes
    bs_matches = re.findall('corona_sdk_simulator_path\s*=\s*["\'](.*)["\']', bs_contents)
    if bs_matches is not None and len(bs_matches) > 0:
      # Last one wins
      simulator_path = bs_matches[-1]
      print("Corona Editor: corona_sdk_simulator_path set from "+str(build_settings))

  return simulator_path


# Given an existing file path or directory, find the likely "main.lua" for this project
def ResolveMainLua(path):
  # debug("ResolveMainLua: path: "+str(path))
  path = os.path.abspath(path)
  if not os.path.isdir(path):
    path = os.path.dirname(path)

  mainlua = os.path.join(path, "main.lua")
  if mainlua == "/main.lua" or mainlua == "\\main.lua":
    return None
  elif os.path.isfile(mainlua):
    return mainlua
  else:
    return ResolveMainLua(os.path.join(path, ".."))

