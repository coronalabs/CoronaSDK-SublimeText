#!/usr/bin/python

import re
import string

preamble = """
{
    "scope": "source.lua",

      "completions":
        [

"""

postamble = """
        ""
    ]
}
"""

print preamble

fh = open('COMPLETIONS')

for line in fh.readlines():
  line = line.rstrip()
  # print line
  argListMatch = re.search("\((.*)\)", line)
  if argListMatch != None:
    argsString = argListMatch.groups()[0]
    funcName = line.replace("("+argsString+")", "")
    args = re.findall("(\[.*?\]|[^\[,]*)", argsString)
    # print "   funcName", funcName
    # print "   argsString", argsString
    # print "   args", args
    argCount = 1
    stCompArgs = ""
    for arg in args:
      arg = arg.strip()
      if arg == "":
        continue
      stCompArgs += ", ${"+str(argCount)+":"+arg+"}"
      argCount += 1
    stCompArgs = stCompArgs.lstrip(",");
    # print "stCompArgs: ", stCompArgs
    print "{{ \"trigger\": \"{0}()\", \"contents\": \"{0}({1} )\"}},".format(funcName, stCompArgs)
  else:
    print "\"{0} \",".format(line)

print postamble
