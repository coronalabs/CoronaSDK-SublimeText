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
import pprint

items = {
    "scope": "source.lua",

    "completions": [ ]
}

if len(sys.argv) != 2:
  print("Usage: "+ sys.argv[0] + " <raw-completions>")
  sys.exit(1)

fh = open(sys.argv[1])

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

  argListMatch = re.search("\((.*)\)", line)

  if argListMatch != None:
    argsString = argListMatch.groups()[0]
    typeDesc = argsString.strip() if typeDesc is "unknown" else typeDesc
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
      # if the arg is not optional and includes a comma, add a comma
      if not arg.startswith("[,"):
        stCompArgs += ","
      stCompArgs += " ${"+str(argCount)+":"+arg+"}"
      argCount += 1
    stCompArgs = stCompArgs.lstrip(",");
    # print({"trigger": "{0}()\t{1}".format(funcName, typeDesc), "contents": "{0}({1} )".format(funcName, stCompArgs)})
    items['completions'].append({"trigger": "{0}()\t{1}".format(funcName, typeDesc), "contents": "{0}({1} )".format(funcName, stCompArgs)})
  else:
    items['completions'].append({"trigger": "{0}\t{1}".format(line, typeDesc), "contents": line})

# pp = pprint.PrettyPrinter(indent = 2)
# pp.pprint(items)
# The string replacements reduce the indented JSON to one item per line
print(json.dumps(items, indent = 2).replace('{\n', '{').replace('", \n', '", ').replace('"\n', '"').replace('  ', ' '))
