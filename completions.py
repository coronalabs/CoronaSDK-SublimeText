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
import json

try:
  from . import _corona_utils  # P3
except:
  import _corona_utils  # P2

# We expose the completions to the snippets code
CoronaCompletions = None


#
# Utility functions
#

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
    self.regex1 = re.compile('.*?'.join(map(re.escape, list(pattern))))  # look for characters in pattern in order
    self.regex2 = re.compile('\\b'+re.escape(pattern))  # look for exact prefixes matching pattern

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
  _findWhiteSpace = re.compile("([^,])\s")
  _use_fuzzy_completion = True
  _strip_white_space = False

  def __init__(self):
    _corona_utils.debug("CoronaLabs: __init__")
    global CoronaCompletions
    CoronaCompletions = self
    # Use fuzzy completions (essentially search for the characters in the target even if separated)
    self._use_fuzzy_completion = _corona_utils.GetSetting("corona_sdk_use_fuzzy_completion", True)
    # Remove whitespace in completions to match some coding styles
    self._strip_white_space = _corona_utils.GetSetting("corona_sdk_completions_strip_white_space", False)


  # Called by the snippets module to make sure completions are loaded
  def initialize(self):
    self.load_completions(_corona_utils.GetSetting("corona_sdk_use_docset", "public"))


  # If we're running ST2, load completions from file
  # else, load completions from member of package
  def load_completions(self, docset):
    # Only load once
    if (len(self._completions) == 0):
      source = docset if docset in ['public', 'legacy', 'daily'] else 'public'
      source = "corona.completions-" + source
      if (_corona_utils.SUBLIME_VERSION < 3000):
        comp_path = os.path.join(_corona_utils.PACKAGE_DIR, source)
        json_data = open(comp_path)
        try:
          self._completions = json.load(json_data)
        except Exception as e:
          print("Corona Editor: failed to load {0} ({1})".format(comp_path, str(e)))
        finally:
          json_data.close()

      else:

        self._completions = json.loads(sublime.load_resource(_corona_utils.ST_PACKAGE_PATH + source))

      # _corona_utils.debug(self._completions)
      print("Corona Editor: loaded {0} completions from {1}".format(len(self._completions['completions']), source))

  def setupFuzzyMatch(self, prefix):
    self._fuzzyMatcher = FuzzyMatcher()
    self._fuzzyMatcher.setPattern(prefix)
    self._fuzzyPrefix = prefix

  def fuzzyMatchString(self, s, use_fuzzy_completion):
    if use_fuzzy_completion:
      threshold = 5
      score = self._fuzzyMatcher.score(s)
      if score > threshold:
        # _corona_utils.debug('s: ', s, '; score: ', score)
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
    self.load_completions(_corona_utils.GetSetting("corona_sdk_use_docset", "public"))

    completion_target = self.current_word(view)

    # Because we adjust the prefix to make completions with periods in them work better we may need to
    # trim the part before the period from the returned string (or it will appear to be doubled)
    completion_adjustment = "" if "." not in completion_target else completion_target.partition('.')[0] + '.'

    # _corona_utils.debug('prefix: ', prefix, 'completion_target: ', completion_target, "; completion_adjustment: ", completion_adjustment, "; corona_sdk_complete_periods: ", _corona_utils.GetSetting("corona_sdk_complete_periods", True) )

    self.setupFuzzyMatch(completion_target)

    # Sample:
    #   { "trigger": "audio.stopWithDelay()", "contents": "audio.stopWithDelay( ${1:duration}, ${2:[, options ]} )"},
    #   "audio.totalChannels ",

    # This is horrible on a variety of levels but is brought upon us by the fact that
    # ST completion files contain an array that is a mixture of strings and dicts
    comps = []
    for c in self._completions['completions']:
      trigger = ""
      contents = ""
      if isinstance(c, dict):
        if self.fuzzyMatchString(c['trigger'], self._use_fuzzy_completion):
          trigger = c['trigger']
          contents = c['contents']
      elif is_string_instance(c):
        if self.fuzzyMatchString(c, self._use_fuzzy_completion):
          _corona_utils.debug("String match: ", c)
          trigger = c
          contents = c

      if trigger is not "":
        if self._strip_white_space and contents is not "":
           contents = self._findWhiteSpace.sub("\\1", contents)
        # If we do the completion adjustment on completions that aren't functions
        # ST somehow erases the text before the period from the document leaving
        # just the piece after it (it makes no sense).  This fixes that but will
        # almost certainly have to be changed when ST's behavior changes.
        if "(" in contents:
          comps.append((trigger, contents.replace(completion_adjustment, '')))
        else:
          comps.append((trigger, contents))

    # _corona_utils.debug("extract_completions: ", view.extract_completions(completion_target))

    # Add textual completions from the document
    for c in view.extract_completions(completion_target):
      comps.append((c, c))

    # Reorganize into a list
    comps = list(set(comps))
    comps.sort()

    # _corona_utils.debug("comps: ", comps)

    return comps

  def current_word(self, view):
    s = view.sel()[0]

    # Expand selection to current "word"
    start = s.a
    end = s.b

    view_size = view.size()
    terminator = ['\t', ' ', '\"', '\'', ':', '=', '-', '+', '*', '/', '^', ',']

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

  _first_time = True

  def __init__(self, *args, **kw):
    _corona_utils.debug("CoronaLabsCollector: __init__")
    super(CoronaLabsCollector, self).__init__(*args, **kw)
    self.periods_set = {}

  def is_lua_file(self, view):
    # Fairly rigorous test for being a Corona Lua file
    # If the file has not been saved optionally default to being a Corona Lua file
    return view.match_selector(view.sel()[0].a, "source.lua.corona") if view.file_name() else _corona_utils.GetSetting("corona_sdk_default_new_file_to_corona_lua", True)


  # Optionally trigger a "build" when a .lua file is saved.  This is best
  # done by setting the "Relaunch Simulator when project is modified" setting
  # in the Simulator itself but is provided here for cases where that option
  # doesn't work
  def on_post_save(self, view):
    if self.is_lua_file(view):
      auto_build = _corona_utils.GetSetting("corona_sdk_auto_build", False)
      if auto_build:
        _corona_utils.debug("Corona Editor: auto build triggered")
        view.window().run_command("build")


  # When a Lua file is loaded and the "use_periods_in_completion" user preference is set,
  # add period to "auto_complete_triggers" if it's not already there.
  def on_load(self, view):
    use_corona_sdk_completion = _corona_utils.GetSetting("corona_sdk_completion", True)

    if use_corona_sdk_completion and self.is_lua_file(view):
      use_periods_in_completion = _corona_utils.GetSetting("corona_sdk_complete_periods", True)

      # Completion behavior is improved if periods are included in the completion process
      if use_periods_in_completion:
        # If "auto_complete_triggers" for periods is not set for this buffer, set it
        auto_complete_triggers = view.settings().get("auto_complete_triggers")
        self.periods_set[view.file_name()] = False
        for act in auto_complete_triggers:
          if "source.lua.corona" in act["selector"] and "." in act["characters"]:
            self.periods_set[view.file_name()] = True
            break
        if not self.periods_set.get(view.file_name(), False):
          auto_complete_triggers.append({ "selector": "source.lua.corona", "characters": "." })
          view.settings().set("auto_complete_triggers", auto_complete_triggers)
          self.periods_set[view.file_name()] = True
    _corona_utils.debug("on_load view: ", view.file_name(), "periods_set" if self.periods_set.get(view.file_name(), False) else "not set")


  # When a Lua file is closed and we added a period to "auto_complete_triggers", remove it
  def on_close(self, view):
    _corona_utils.debug("on_close view: ", view.file_name(), "periods_set" if self.periods_set.get(view.file_name(), False) else "not set" )
    if view.file_name() is not None and self.periods_set.get(view.file_name(), False):
      auto_complete_triggers = view.settings().get("auto_complete_triggers")
      if { "selector": "source.lua.corona", "characters": "." } in auto_complete_triggers:
        auto_complete_triggers.remove({ "selector": "source.lua.corona", "characters": "." })
        self.periods_set[view.file_name()] = False


  def on_query_completions(self, view, prefix, locations):
    use_corona_sdk_completion = _corona_utils.GetSetting("corona_sdk_completion", True)

    if self._first_time and use_corona_sdk_completion:
      if not self.is_lua_file(view) and view.file_name().lower().endswith(".lua"):
        msg = "Corona Editor: syntax is not set to 'Corona SDK Lua' so completion is inactive"
        sublime.status_message(msg)
        print(msg)
        self._first_time = False

    _corona_utils.debug("on_query_completions: ",  "use_corona_sdk_completion: ", use_corona_sdk_completion, "source.lua.corona - entity: ", view.match_selector(locations[0], "source.lua.corona - entity"))
    if use_corona_sdk_completion and view.match_selector(locations[0], "source.lua.corona - entity"):
      comps = self.find_completions(view, prefix)
      flags = 0  # sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS
      return (comps, flags)
    else:
      return []
