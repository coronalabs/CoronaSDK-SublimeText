#!/usr/bin/python
#
# Sublime Text plugin to support Corona SDK
#
# Copyright (c) 2013 Corona Labs Inc. A mobile development software company. All rights reserved.
#
# MIT License - see https://raw.github.com/coronalabs/CoronaSDK-SublimeText/master/LICENSE
#

import re
import string
import json
import sys

preamble = """
{
    "scope": "source.lua",

      "completions":
        [
"""

postamble = """
    ]
}
"""

if len(sys.argv) != 2:
  print("Usage: "+ sys.argv[0] + " <raw-completions>")
  sys.exit(1)

fh = open(sys.argv[1])

print(preamble)
output = ""

for line in fh.readlines():
  typeDesc = "unknown"
  line = line.strip()
  # print(line)
  if line.find(':') != -1:
    # We have a type member, since we can't know what the object is called,
    # complete from the semi-colon only
    line = line.partition(':')[2]

  if line.find("\t") != -1:
    # We have a type description after a tab
    typeDesc = line.partition("\t")[2]
    line = line.partition("\t")[0]

  if output != "":
    output += ",\n"

  argListMatch = re.search("\((.*)\)", line)

  if argListMatch != None:
    argsString = argListMatch.groups()[0]
    funcName = line.replace("("+argsString+")", "")
    funcName = funcName.strip()
    args = re.findall("(\[.*?\]|[^\[,]*)", argsString)
    # print("   funcName", funcName)
    # print("   argsString", argsString)
    # print("   args", args)
    argCount = 1
    stCompArgs = ""
    for arg in args:
      arg = arg.strip()
      if arg == "":
        continue
      arg = json.dumps(arg)[1:-1] # escape JSON and remove surrounding quotes
      # if the arg is not optional and includes a comma, add a comma
      if not arg.startswith("[,"):
        stCompArgs += ","
      stCompArgs += " ${"+str(argCount)+":"+arg+"}"
      argCount += 1
    stCompArgs = stCompArgs.lstrip(",");
    # print("stCompArgs: ", stCompArgs)
    output += "{{ \"trigger\": \"{0}()\\t{2}\", \"contents\": \"{0}({1} )\"}}".format(funcName, stCompArgs, typeDesc)
  else:
    output += "{{ \"trigger\": \"{0}\\t{1}\", \"contents\": \"{0}\"}}".format(line, typeDesc)

print(output)
print(postamble)
