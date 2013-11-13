import sublime
import os

SUBLIME_VERSION = 3000 if sublime.version() == '' else int(sublime.version())
PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))
# print("PLUGIN_DIR: " + PLUGIN_DIR)
PACKAGE_NAME = os.path.basename(PLUGIN_DIR) if SUBLIME_VERSION < 3000 else os.path.basename(PLUGIN_DIR).replace(".sublime-package", "")
# print("PACKAGE_NAME: " + PACKAGE_NAME)
