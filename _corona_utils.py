# Note: the leading underscore on the name of this module forces Sublime Text to load it first which
# prevents it being loaded more than once (once when it's first imported, e.g. by about.py, and then
# again when it comes up in the load order)

import sublime
import os

SUBLIME_VERSION = "not set"
PLUGIN_PATH = "not set"
PACKAGE_NAME = "not set"
PACKAGE_DIR = "not set"
ST_PACKAGE_PATH = "not set"

# In Sublime Text 3 most APIs are unavailable until a module level function is called (fortunately
# sublime.version() is available so we can correctly fake things in Sublime Text 2; see about.py)
SUBLIME_VERSION = 3000 if sublime.version() == '' else int(sublime.version())

def debug(*args):
  for arg in args:
    print("Corona Editor: " + str(arg))

def Init():
  print("+++++++++++++++ corona_utils.Init() ++++++++++++++")

  global SUBLIME_VERSION
  global PLUGIN_PATH
  global PACKAGE_NAME
  global PACKAGE_DIR
  global ST_PACKAGE_PATH

  PLUGIN_PATH = os.path.dirname(os.path.realpath(__file__))
  debug("PLUGIN_PATH: " + PLUGIN_PATH)

  PACKAGE_NAME = os.path.basename(PLUGIN_PATH) if SUBLIME_VERSION < 3000 else os.path.basename(PLUGIN_PATH).replace(".sublime-package", "")
  debug("PACKAGE_NAME: " + PACKAGE_NAME)

  # This is the actual package dir on ST2 and the "unpacked" package dir on ST3 ("~/Library/Application Support/Sublime Text 2/Packages")
  PACKAGE_DIR = os.path.join(sublime.packages_path(), PACKAGE_NAME)
  debug("PACKAGE_DIR: " + PACKAGE_DIR)

  # This is the faux path used by various Sublime Text functions ("Packages/CoronaSDK/")
  ST_PACKAGE_PATH = "Packages/" + PACKAGE_NAME + "/"
  debug("ST_PACKAGE_PATH: " + ST_PACKAGE_PATH)

# This is run by ST3 after the plugins have loaded (and the ST API is ready for calls)
def plugin_loaded():
  Init()

# This fakes the above functionality on ST2.
# It's important that this is called from a module that isn't imported by any other modules or
# the code gets run multiple times in ST2
if SUBLIME_VERSION < 3000:
  Init()


# Return the path to the Simulator for the current platform
def GetSimulatorCmd(debug = False):
  platform = sublime.platform()
  arch = sublime.arch()

  simulator_path = ""
  simulator_flags = []

  view = sublime.active_window().active_view()
  if platform == "osx":
    simulator_path = view.settings().get("corona_sdk_simulator_path", "/Applications/CoronaSDK/Corona Simulator.app")
    if simulator_path.endswith(".app"):
      simulator_path += "/Contents/MacOS/Corona Simulator"
    simulator_flags = [ "-singleton", "1" ]
    if debug:
      simulator_flags.append("-debug")
      simulator_flags.append("1")
      simulator_flags.append("-project")
  elif platform == 'windows':
    if arch == "x64":
      simulator_path = view.settings().get("corona_sdk_simulator_path", "C:\\Program Files (x86)\\Corona Labs\\Corona SDK\\Corona Simulator.exe")
    else:
      simulator_path = view.settings().get("corona_sdk_simulator_path", "C:\\Program Files\\Corona Labs\\Corona SDK\\Corona Simulator.exe")
    simulator_flags = [ "/singleton", "/no-console" ]
    if debug:
      simulator_flags.append("/debug")

  # Can we find an executable file at the path
  if not os.path.isfile(simulator_path) or not os.access(simulator_path, os.X_OK):
    sublime.error_message("Cannot find executable Corona Simulator at path '{0}'\n\nYou can set the user preference 'corona_sdk_simulator_path' to the location of the Simulator.".format(simulator_path))
    return None, None

  return simulator_path, simulator_flags

# Given an existing file path or directory, find the likely "main.lua" for this project
def ResolveMainLua(path):

  print("CoronaResolveMainLua: path: "+str(path))
  path = os.path.abspath(path)
  if not os.path.isdir(path):
    path = os.path.dirname(path)

  mainlua = os.path.join(path, "main.lua")
  if mainlua == "/main.lua":
    return None
  elif os.path.isfile(mainlua):
    return mainlua
  else:
    return CoronaResolveMainLua(os.path.join(path, ".."))

