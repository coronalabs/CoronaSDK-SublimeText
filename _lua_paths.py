import os
import re

_findBackslash = re.compile("/")  

# http://rosettacode.org/wiki/Find_common_directory_path#Python
def __commonprefix(*args, sep='/'):
  return os.path.commonprefix(*args).rpartition(sep)[0]

def __getProjectPaths(view):
  project_data=view.window().project_data()
  if project_data is None:
    return []
  
  paths=[]
  if "folders" in project_data:
    folders=project_data["folders"]
    for f in folders:
      if "path" in f and os.path.isabs(f["path"]):
        paths.append(f["path"])
  
  return paths   

def __getViewPath(view):
  searchpath=__commonprefix(view.window().folders())
  for root, dirs, files in os.walk(searchpath):
    for name in files:
      if "main.lua"==name:
        return root
    
def getLuaFilesAndPaths(view,followlinks): 
  luaPaths=[]
  paths=__getProjectPaths(view)
  paths.append(__getViewPath(view)) 

  for path in paths:
    for root, dirs, files in os.walk(path,followlinks=followlinks):
      for name in files:
        if ".lua" in name:
          name=os.path.splitext(name)[0]
          relpath=os.path.relpath(os.path.join(root, name),start=path)
          luaPaths.append((name,_findBackslash.sub(".",relpath)))
            
    return luaPaths