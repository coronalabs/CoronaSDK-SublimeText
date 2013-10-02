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
        terminator = ['\t', ' ', '\"', '\'']
 
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
        # print "URL : " + url

        docUrl = "http://docs.coronalabs.com/api/library/" + url + ".html";
        # print "docURL : " + docUrl
 
        webbrowser.open_new_tab(docUrl)
