#
# Sublime Text plugin to support Corona Editor
#
# Copyright (c) 2013 Corona Labs Inc. A mobile development software company. All rights reserved.
#
# MIT License - see https://raw.github.com/coronalabs/CoronaSDK-SublimeText/master/LICENSE

import sublime
import sublime_plugin
import os.path
import json
import threading
import re
import zipfile
import tempfile
from xml.dom import minidom

try:
  from . import completions  # P3
except:
  import completions  # P2

try:
  from . import _corona_utils  # P3
except:
  import _corona_utils  # P2


def XMLGetText(nodelist):
  parts = []
  for node in nodelist:
    if node.nodeType == node.TEXT_NODE:
      parts.append(node.data)
  return ''.join(parts)


def UnZIPToDir(zipFilePath, destDir):
  zfile = zipfile.ZipFile(zipFilePath)
  for name in zfile.namelist():
    (dirName, fileName) = os.path.split(name)
    if fileName == '':
      # directory
      newDir = os.path.join(destDir, dirName)
      if not os.path.exists(newDir):
        os.makedirs(newDir)
    else:
      # file
      path = os.path.join(destDir, name)
      # print("Unzip: " + path)
      fd = open(path, 'wb')
      fd.write(zfile.read(name))
      fd.close()
  zfile.close()


class CoronaSnippetFolderIndexer(threading.Thread):
  _initialized = False
  _snippets_dir = None

  def __init__(self):
    threading.Thread.__init__(self)

  def run(self):

    # Wait for _corona_utils initialization to complete
    # print("Waiting for InitializedEvent...")
    _corona_utils.InitializedEvent.wait()

    self._snippets_dir = os.path.join(_corona_utils.PACKAGE_USER_DIR, "Snippets")

    if not os.path.exists(self._snippets_dir):
      os.makedirs(self._snippets_dir)
      print(_corona_utils.PACKAGE_NAME + ": Extracting snippets ...")
      try:
        # In ST3 our ZIP file is not on the filesystem, it's in our package so we have to extract
        # it and unzip from there (to work on Windows the temp file must be closed before it can
        # be reopened to be unzipped)
        zip_bytes = sublime.load_binary_resource(_corona_utils.ST_PACKAGE_PATH + "snippets.zip")
        with tempfile.NamedTemporaryFile(suffix = ".zip", delete=False) as tempzip:
          tempzip.write(zip_bytes)
          tempzip.close()
          UnZIPToDir(tempzip.name, self._snippets_dir)
          os.remove(tempzip.name)
      except:
        # We're on ST2 and the ZIP file is just a file in our package directory
        UnZIPToDir(os.path.join(_corona_utils.PACKAGE_DIR, "snippets.zip"), self._snippets_dir)

    snippetMenuArray = []
    snippetJSON = ""

    if os.path.isdir(self._snippets_dir):
      snippetMenuArray = self.addDirectory(self._snippets_dir)
      snippetJSON = json.dumps(snippetMenuArray, indent=4, separators=(',', ': '))

    if snippetJSON == "":
      print(_corona_utils.PACKAGE_NAME + ": Failed to build Snippets menu")
      return

    # Put our menu into the Main.sublime-menu.template file
    menus = ""
    templatePath = _corona_utils.ST_PACKAGE_PATH + "Main.sublime-menu.template"
    try:
      if _corona_utils.SUBLIME_VERSION < 3000:
        with open(templatePath, "r") as fd:
          menus = fd.read()
      else:
        menus = sublime.load_resource(templatePath)
    except Exception as e:
      menus = ""
      print("snippets exception: " + str(e))

    if menus == "":
      print(_corona_utils.PACKAGE_NAME + ": Failed to load Snippets menu: " + templatePath)
      return

    menus = menus.replace("$corona_snippets", snippetJSON)

    if not os.path.exists(_corona_utils.PACKAGE_DIR):
      os.makedirs(_corona_utils.PACKAGE_DIR)
    if _corona_utils.SUBLIME_VERSION < 3000:
      with open(os.path.join(_corona_utils.PACKAGE_DIR, "Main.sublime-menu"), "w") as fd:
          fd.write("// Generated file - do not edit - modify 'Main.sublime-menu.template' instead\n")
          fd.write(menus)
    else:  # ST3/P3
      with open(os.path.join(_corona_utils.PACKAGE_DIR, "Main.sublime-menu"), "w", encoding='utf-8') as fd:
          fd.write("// Generated file - do not edit - modify 'Main.sublime-menu.template' instead\n")
          fd.write(menus)

  def addDirectory(self, path):
    jsonArray = []
    pathnames = os.listdir(path)
    for pathname in pathnames:
      if pathname.startswith(".") or pathname == "README.md":
        continue
      realpath = os.path.join(path, pathname)
      # _corona_utils.debug("realpath: " + realpath)
      if os.path.isdir(realpath):
        jsonArray.append({"caption": pathname, "children": self.addDirectory(realpath)})
      else:
        # Parse XML snippet file to get the "Description"
        if realpath.endswith(".sublime-snippet"):
          # _corona_utils.debug("Parsing: " + realpath)
          try:
            xmldoc = minidom.parse(realpath)
          except:
            print(_corona_utils.PACKAGE_NAME + ": Invalid XML in " + realpath)
          else:
            desc = XMLGetText(xmldoc.getElementsByTagName('description')[0].childNodes)
            if desc is None:
              desc = path
        else:
          desc = pathname

        jsonArray.append({"caption": desc, "command": "corona_snippet", "args": {"file": realpath}})

    return jsonArray


# This is run automatically after the plugin has loaded in ST3
def plugin_loaded():
  # Index the "snippets" directory in the background
  indexer = CoronaSnippetFolderIndexer()
  indexer.start()

# We need to run it manually in ST2
if _corona_utils.SUBLIME_VERSION < 3000:
  plugin_loaded()


class CoronaSnippetCommand(sublime_plugin.TextCommand):
  _comps = None

  def run(self, edit, **args):

    if 'name' in args:
      trigger = args['name']
    else:
      trigger = args['file']

    if self._comps is None:
      completions.CoronaCompletions.initialize()
      self._comps = completions.CoronaCompletions._completions

    # print("CoronaSnippetCommand:")
    # print(str(self._comps))
    # print(str(len(self._comps['completions'])) + " completions available")

    # print("trigger: " + trigger)
    if trigger.endswith(".sublime-snippet"):
      # The command wants names in the form: "Packages/User/Snippets/foo.sublime-snippet" so we
      # need to remove everything in the path before "Packages" and convert backslashes to slashes
      # (TODO: note that this wont work for a user called "Packages")
      trigger = re.sub(r'.*Packages', "Packages", trigger, 1)
      trigger = trigger.replace('\\', '/')
      _corona_utils.debug("modified trigger: " + trigger)
      self.view.run_command("insert_snippet", {"name": trigger})
    else:
      # Find a completion keyed by the contents of the snippet file
      with open(trigger, "r") as fd:
        lookup = fd.read().strip()

      key = [key for key, item in enumerate(self._comps['completions']) if item['trigger'].lower().startswith(lookup.lower())]
      if key is not None and len(key) != 0:
        self.view.run_command("insert_snippet", {"contents": self._comps['completions'][key[0]]['contents']})
      else:
        self.view.run_command('insert', {'characters': lookup})
