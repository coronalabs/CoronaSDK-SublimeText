import sublime

def getTextToCursor(view):
  cursor=view.sel()[0].begin()
  lineStart=view.text_point(view.rowcol(cursor)[0],0)
  return view.substr(sublime.Region(lineStart,cursor))
