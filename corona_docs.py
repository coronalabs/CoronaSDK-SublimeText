#
# Sublime Text plugin to support Solar2D
#
# Copyright (c) 2020 Solar2D.
#
# MIT License - see https://raw.github.com/coronalabs/CoronaSDK-SublimeText/master/LICENSE
#

import sublime
import sublime_plugin
import webbrowser
import string
import re
import urllib

try:
  from . import _corona_utils  # P3
except:
  import _corona_utils  # P2

SEARCH_URL = "https://www.google.com/cse?cx=009283852522218786394%3Ag40gqt2m6rq&ie=UTF-8&q={search_term}&sa=Search#gsc.tab=0&gsc.q={search_term}&gsc.page=1"

# Note "lfs", "socket", "sqlite3" are omitted because we don't have complete docs for those
LIBRARY_APIS = (
  "ads", "analytics", "audio", "credits", "crypto", "display", "easing",
  "facebook", "gameNetwork", "global", "graphics", "io", "json", "licensing",
  "math", "media", "native", "network", "os", "package", "physics", "sprite",
  "store", "storyboard", "string", "system", "table", "timer", "transition", "widget")


# Python version independent UrlEncode
def UrlEncode(s):
  try:
    return urllib.parse.quote_plus(s)
  except AttributeError:
    return urllib.quote_plus(s)


class CoronaDocsCommand(sublime_plugin.TextCommand):
  def is_visible(self):
    if not len(self.view.sel()):
      return False
    s = self.view.sel()[0]
    return self.view.match_selector(s.a, "source.lua - entity")

  def run(self, edit):
    s = self.view.sel()[0]

    # Expand selection to current "word"
    start = s.a
    end = s.b

    view_size = self.view.size()
    terminator = ['\t', ' ', '\"', '\'', '(', '=']

    while (start > 0
            and not self.view.substr(start - 1) in terminator
            and self.view.classify(start) & sublime.CLASS_LINE_START == 0):
        start -= 1

    while (end < view_size
            and not self.view.substr(end) in terminator
            and self.view.classify(end) & sublime.CLASS_LINE_END == 0):
        end += 1

    # Note if the current point is on a Lua keyword (according to
    # the .tmLanguage definition)
    isLuaKeyword = self.view.match_selector(start,
                                            "keyword.control.lua, support.function.lua, support.function.library.lua")

    use_docset = _corona_utils.GetSetting("corona_sdk_use_docset", "public")
    if use_docset in ['legacy', 'daily']:
      docset = use_docset + "/"
    else:
      docset = ""

    # Convert "word" under cursor to Solar2D Docs link, or a Lua docs link
    page = self.view.substr(sublime.Region(start, end))
    page = page.strip(string.punctuation)

    # Look for an embedded period which, if the class name is one of ours,
    # indicates we should look it up in the "library" section of the docs
    # (unless the class member doesn't start with a lowercase letter in which
    # case it's a constant and we'll have to just default to searching for it)
    if page is None or page == "":
      # Nothing is selected, take them to API home
      docUrl = "https://docs.coronalabs.com/" + docset + "api/index.html"
    elif (re.search("\w+\.[a-z]", page) is not None and
       page.partition(".")[0] in LIBRARY_APIS):
      page = page.replace(".", "/")
      docUrl = "https://docs.coronalabs.com/" + docset + "api/library/" + page + ".html"
    elif isLuaKeyword:
      # Unfortunately, there's no search on the Lua docs site so we need to guess at
      # an anchor (if it's not there, you go to the top of the page)
      docUrl = "https://www.lua.org/manual/5.1/manual.html#pdf-" + page
    else:
      # We don't know what we're on, send them to the Solar2D Documentation search page
      page = UrlEncode(page)
      docUrl = SEARCH_URL.format(search_term=page)

    # print("docURL : " + docUrl)

    webbrowser.open_new_tab(docUrl)
