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

def __getOpenFiles(view):
  allViews=view.window().views()
  openFiles=[]
  for v in allViews:
    if v.file_name() is not None:
      openFiles.append(v.file_name())

  return openFiles

def __getViewPath(view):
  folders=view.window().folders()
  files=__getOpenFiles(view)
  searchpath=__commonprefix(folders+files)
  for root, dirs, files in os.walk(searchpath):
    for name in files:
      if "main.lua"==name:
        return root
    
def getFilesAndPaths(view,extensions=[".lua"],followlinks=False,converttoluapaths=True): 
  luaPaths=[]
  paths=__getProjectPaths(view)
  viewPath=__getViewPath(view)
  if viewPath is not None:
    paths.append(viewPath)
    
  for path in paths:
    for root, dirs, files in os.walk(path,followlinks=followlinks):
      for name in files:
        if any(ext in name.lower() for ext in extensions):
          if converttoluapaths:
            name=os.path.splitext(name)[0]
          relpath=os.path.relpath(os.path.join(root, name),start=path)
          if converttoluapaths:
            relpath=_findBackslash.sub(".",relpath)
          luaPaths.append((name,relpath))
            
    return luaPaths