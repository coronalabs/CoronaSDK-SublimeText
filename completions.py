import sublime, sublime_plugin, os, re, threading
from os.path import basename

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
class CoronaLabs:
  _functions = []
  MAX_WORD_SIZE = 100
  MAX_FUNC_SIZE = 50
  def clear(self):
    self._functions = []
  def addFunc(self, name, signature, filename):
    self._functions.append(Method(name, signature, filename))
  def get_autocomplete_list(self, word):
    autocomplete_list = []
    for method_obj in self._functions:
      if word in method_obj.name():
        method_str_to_append = method_obj.name() + '(' + method_obj.signature()+ ')'
        method_file_location = method_obj.filename();
        autocomplete_list.append((method_str_to_append + '\t' + method_file_location,method_str_to_append)) 
    return autocomplete_list

def is_lua_file(filename):
  return '.lua' in filename

class CoronaLabsCollector(CoronaLabs, sublime_plugin.EventListener):
  # def on_post_save(self, view):

  # For some reason we can't just put the modified "word_separators" in a plugin 
  # specific preferences file so we need to active modify the preference here
  def on_load(self, view):
    print "view loaded"
    if is_lua_file(view.file_name()):
      word_seps = view.settings().get("word_separators")
      word_seps = word_seps.replace('.', '') # remove periods
      view.settings().set("word_separators", word_seps)
      print "word_separators: ", view.settings().get("word_separators")

  '''
  def on_query_completions(self, view, prefix, locations):
    print "on_query_completions: prefix: ", prefix, locations[0]
    current_file = view.file_name()
    completions = []
    if view.match_selector(locations[0], "source.lua - entity"):
      print "we got lua file"
      completions = [ ("ads.hide()","ads.hide()"), ("ads.init()", "ads.init( ${1:providerName}, ${2:appId} ${3:[, listener]} )"), ("ads.show()", "ads.show( ${1:adUnitType} ${2:[, params]} )"), ]
      completions = list(set(completions))
      completions.sort()
    return (completions,sublime.INHIBIT_WORD_COMPLETIONS)
  '''
