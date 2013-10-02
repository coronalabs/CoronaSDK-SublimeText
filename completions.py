import sublime, sublime_plugin, os, re, threading
from os.path import basename
import json
from pprint import pprint

#
# Method Class
#
class Method:
  _name = ""
  _signature = ""
  _filename = ""
  def __init__(self, name, signature, filename):
    self._name = name
    self._filename = filename;
    self._signature = signature
  def name(self):
    return self._name
  def signature(self):
    return self._signature
  def filename(self):
    return self._filename

#
# CoronaLabs Class
#
def is_lua_file(filename):
  return '.lua' in filename

class CoronaLabs:
  _completions = []
  def load_completions(self):
    if (len(self._completions) == 0):
      print "CoronaLabs::load_completions: "

      comp_path = os.path.join(sublime.packages_path(), 'Old-CoronaLabs') # 'Corona SDK')
      comp_path = os.path.join(comp_path, "corona.completions")

      json_data = open(comp_path)

      self._completions = json.load(json_data)
      # pprint(self._completions)
      print "Loaded {0} completions".format(len(self._completions['completions']))
      json_data.close()

  # extract completions which match prefix
  def find_completions(self, view, prefix):
    print "CoronaLabs::find_completions: ", prefix
    self.load_completions()

    # Sample:
    # { "trigger": "audio.dispose()", "contents": "audio.dispose( ${1:audioHandle} )"},

    comps = []
    for c in self._completions['completions']:
      # print "type: ", type(c)
      if isinstance( c, dict ):
        if c['trigger'].startswith(prefix):
          comps.append( (c['trigger'], c['contents']) )
      elif isinstance(c, unicode):
        if c.startswith(prefix):
          comps.append( (c, c) )

    # print "comps: ", comps
    # print "extract_completions: ", view.extract_completions(prefix)

    # Add textual completions from the document
    for c in view.extract_completions(prefix):
      comps.append((c, c))

    # Reorganize into a list
    comps = list(set(comps))
    comps.sort()

    return comps

  def current_word(self, view):
    s = view.sel()[0]

    # Expand selection to current "word"
    start = s.a
    end = s.b

    view_size = view.size()
    terminator = ['\t', ' ', '\"', '\'']

    while (start > 0
            and not view.substr(start - 1) in terminator
            and view.classify(start) & sublime.CLASS_LINE_START == 0):
        start -= 1

    while (end < view_size
            and not view.substr(end) in terminator
            and view.classify(end) & sublime.CLASS_LINE_END == 0):
        end += 1

    return view.substr(sublime.Region(start, end))

class CoronaLabsCollector(CoronaLabs, sublime_plugin.EventListener):
  # Optionally trigger a "build" when a .lua file is saved.  This is best 
  # done by setting the "Relaunch Simulator when project is modified" setting
  # in the Simulator itself but is provided here for cases where that option
  # doesn't work
  def on_post_save(self, view):
    if is_lua_file(view.file_name()):
      auto_build = view.settings().get("corona_sdk_auto_build")
      if auto_build:
        print "Corona SDK: auto build triggered"
        view.window().run_command("build")

  # For some reason we can't just put the modified "word_separators" in a plugin 
  # specific preferences file so we need to actively modify the preference here
  def on_load(self, view):
    if is_lua_file(view.file_name()):
      word_seps = view.settings().get("word_separators")
      word_seps = word_seps.replace('.', '') # remove periods
      view.settings().set("word_separators", word_seps)
      # print "word_separators: ", view.settings().get("word_separators")

  def on_query_completions(self, view, prefix, locations):
    print "on_query_completions: prefix: ", prefix, locations[0]
    current_file = view.file_name()
    comps = []

    if view.match_selector(locations[0], "source.lua - entity"):
      print "we got a lua file"
      comps = self.find_completions(view, prefix)

    return (comps, sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS)
