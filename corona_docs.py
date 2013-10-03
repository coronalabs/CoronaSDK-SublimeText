#
# Sublime Text plugin to support Corona SDK
#
# Copyright (c) 2013 Corona Labs Inc. A mobile development software company. All rights reserved.
#
# MIT License - see https://raw.github.com/coronalabs/CoronaSDK-SublimeText/master/LICENSE
#

import sublime
import sublime_plugin
import webbrowser
import string
 
 
class CoronaDocsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = self.view.sel()[0]
 
        # Expand selection to current "word"
        start = s.a
        end = s.b
 
        view_size = self.view.size()
        terminator = ['\t', ' ', '\"', '\'', '(']
 
        while (start > 0
                and not self.view.substr(start - 1) in terminator
                and self.view.classify(start) & sublime.CLASS_LINE_START == 0):
            start -= 1
 
        while (end < view_size
                and not self.view.substr(end) in terminator
                and self.view.classify(end) & sublime.CLASS_LINE_END == 0):
            end += 1
 
        # Convert "word" under cursor to Corona Docs link
        url = self.view.substr(sublime.Region(start, end))
        url = url.rstrip(string.punctuation)
        url = url.replace(".", "/");
        # print("URL : " + url)

        use_daily_docs = self.view.settings().get("corona_sdk_use_daily_docs")
        if use_daily_docs:
          docUrl = "http://docs.coronalabs.com/daily/api/library/" + url + ".html";
        else:
          docUrl = "http://docs.coronalabs.com/api/library/" + url + ".html";
        # print("docURL : " + docUrl)
 
        webbrowser.open_new_tab(docUrl)
