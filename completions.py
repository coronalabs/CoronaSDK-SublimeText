#
# Sublime Text plugin to support Corona Editor
#
# Copyright (c) 2013 Corona Labs Inc. A mobile development software company. All rights reserved.
#
# MIT License - see https://raw.github.com/coronalabs/CoronaSDK-SublimeText/master/LICENSE

import sublime, sublime_plugin, os, re, threading
from os.path import basename, dirname, realpath
import json
from pprint import pprint

try:
    from . import corona_utils # P3
except:
    import corona_utils # P2

# We expose the completions to the snippets code
CoronaCompletions = None

# print('SUBLIME_VERSION: ', SUBLIME_VERSION)

#
# Utility functions
#
def is_lua_file(filename):
  return filename.endswith('.lua') if filename is not None else True

# determine if 'obj' is a string in both Python 2.x and 3.x
def is_string_instance(obj):
  try:
    return isinstance(obj, basestring)
  except NameError:
    return isinstance(obj, str)

class FuzzyMatcher():

  def __init__(self):
    self.prefix_match_tweak = 20
    self.regex1 = ''
    self.regex2 = ''

  def setPattern(self, pattern):
    self.regex1 = re.compile('.*?'.join(map(re.escape, list(pattern)))) # look for characters in pattern in order
    self.regex2 = re.compile('\\b'+pattern) # look for exact prefixes matching pattern

  def score(self, string):
    match = self.regex1.search(string)
    tweak = self.regex2.search(string)
    if match is None:
      return 0
    else:
      return (100.0 / ((1 + match.start()) * (match.end() - match.start() + 1))) + (self.prefix_match_tweak if tweak is not None else 0)

#
# CoronaLabs Class
#
class CoronaLabs:
  _completions = []
  _fuzzyMatcher = None
  _fuzzyPrefix = None

  def __init__(self):
    self.load_completions(True)

  # If we're running ST2, load completions from file
  # else, load completions from member of package
  def load_completions(self, use_daily_docs):
    # Only load once
    if (len(self._completions) == 0):
      source = "corona.completions" + ("-daily" if use_daily_docs else "-public")
      if (SUBLIME_VERSION < 3000):
        comp_path = PLUGIN_DIR # os.path.join(sublime.packages_path(), 'Corona Editor')
        comp_path = os.path.join(comp_path, source)
        json_data = open(comp_path)
        self._completions = json.load(json_data)
        json_data.close()

      else:

        self._completions = json.loads(sublime.load_resource("Packages/Corona Editor/" + source))

      # pprint(self._completions)
      print("Corona Editor: loaded {0} completions from {1}".format(len(self._completions['completions']), source))

    global CoronaCompletions
    CoronaCompletions = self._completions

  def setupFuzzyMatch(self, prefix):
    self._fuzzyMatcher = FuzzyMatcher()
    self._fuzzyMatcher.setPattern(prefix)
    self._fuzzyPrefix = prefix

  def fuzzyMatchString(self, s, use_fuzzy_completion):
    if use_fuzzy_completion:
      threshold = 5
      score = self._fuzzyMatcher.score(s)
      if score > threshold:
        # print('s: ', s, '; score: ', score)
        return True
      else:
        return False
    else:
      if s.startswith(self._fuzzyPrefix):
        return True
      else:
        return False

  # extract completions which match prefix
  # Completions are problematic because Sublime uses the "word_separators" preference to decide where tokens
  # begin and end which, by default, means that periods are not completed properly.  One options is to remove
  # periods from "word_separators" and this works well except that it breaks intra line cursor movement with Alt-arrow.
  # So we jump through some hoops to accommodate periods in the completion process:
  #  * determine the "completion target" ourselves based on the view instead of using the provided prefix
  #  * if there's a period in the "completion target", return only the part following the period in the completions

  def find_completions(self, view, prefix):
    self.load_completions(view.settings().get("corona_sdk_use_daily_docs", False))
    use_fuzzy_completion = view.settings().get("corona_sdk_use_fuzzy_completion", True)

    completion_target = self.current_word(view)

    # print('completion_target: ', completion_target)

    # because we adjust the prefix to make completions with periods in them work better we may need to
    # trim the part before the period from the returned string (or it will appear to be doubled). Of
    # course, if we've removed periods from the word_separators we don't need to do this.
    trim_result = True if '.' in completion_target and view.settings().get("corona_sdk_complete_periods", True) else False

    self.setupFuzzyMatch(completion_target)

    # Sample:
    #   { "trigger": "audio.stopWithDelay()", "contents": "audio.stopWithDelay( ${1:duration}, ${2:[, options ]} )"},
    #   "audio.totalChannels ",

    # This is horrible on a variety of levels but is brought upon us by the fact that
    # ST completion files contain an array that is a mixture of strings and dicts
    comps = []
    for c in self._completions['completions']:
      if isinstance( c, dict ):
        #if c['trigger'].startswith(completion_target):
        if self.fuzzyMatchString(c['trigger'], use_fuzzy_completion):
          comps.append( (c['trigger'], c['contents'] if not trim_result else c['contents'].partition('.')[2]) )
      elif is_string_instance(c):
        # if c.startswith(completion_target):
        if self.fuzzyMatchString(c, use_fuzzy_completion):
          comps.append( (c, c if not trim_result else c.partition('.')[2]) )

    # print("comps: ", comps)
    # print("extract_completions: ", view.extract_completions(completion_target))

    # Add textual completions from the document
    for c in view.extract_completions(completion_target):
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
    terminator = ['\t', ' ', '\"', '\'', ':']

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
      auto_build = view.settings().get("corona_sdk_auto_build", False)
      if auto_build:
        print("Corona Editor: auto build triggered")
        view.window().run_command("build")

  def on_query_completions(self, view, prefix, locations):
    current_file = view.file_name()
    comps = []

    use_corona_sdk_completion = view.settings().get("corona_sdk_completion", True)
    use_periods_in_completion = view.settings().get("corona_sdk_complete_periods", True)

    # Completion behavior is improved if periods are included in the completion process but
    # the only way to do this is to remove the period from the "word_separators" preference.
    # Doing this breaks some intraline cursor movement (like Alt+Arrow) so we make it optional.
    if use_periods_in_completion:
      word_separators = view.settings().get("word_separators")
      word_separators = word_separators.replace('.', '')
      view.settings().set("word_separators", word_separators)

    # We should do something "correct" like checking the selector
    # to determine whether we should use Corona completions but
    # the path of least surprise is just to check the file extension
    # if view.match_selector(locations[0], "source.lua - entity"):
    if is_lua_file(view.file_name()) and use_corona_sdk_completion:
      comps = self.find_completions(view, prefix)
      flags = 0 # sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS
      return (comps, flags)
    else:
      return []
