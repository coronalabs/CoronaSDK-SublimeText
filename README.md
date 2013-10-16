Corona Editor
=============

Corona Editor is the official ***Corona SDK*** plugin for ***Sublime Text***.  Designed to make building apps even easier by adding functionality to ***Sublime Text*** to improve developer productivity.

### Corona Editor Plugin Installation Instructions

1. Install the ***Sublime Text*** **Package Control** plugin if you don't already have it: [https://sublime.wbond.net/installation](https://sublime.wbond.net/installation)
1. Choose: **Tools** > **Command Palette...** > **Package Control: Install Package**
1. Find **Corona Editor** by typing in the search field, click on it to install it
1. Restart ***Sublime Text*** or reopen any .lua files to see the new features

Alternatively, if you are comfortable doing manual installs of Sublime Text plugins, you can download the plugin from [https://github.com/coronalabs/CoronaSDK-SublimeText/archive/master.zip](here).

### Using the Plugin

After restarting ***Sublime Text*** you'll have the following features available when editing .lua files:

 * Completion works for all API calls and constants (correctly handling periods in the name)
 * Documentation can be called up by placing the cursor on an API call (or selecting it) and either hitting **F1** or choosing **Corona SDK Docs** from the context menu.  Lua keywords will be looked up in the Lua documentation.  If the context of something isn't recognized, a search of the Corona SDK documentation will be initiated
 * The current app can be run in the Simulator by pressing Ctrl+B (Windows) or Cmd+B (MacOSX).  Debug output appears in the "build" window in ***Sublime Text***
 * Syntax highlighting of Lua with Corona SDK calls is done (choose **View > Syntax > Corona SDK Lua** to enable this)

You can set a ***Sublime Text*** User Preference called "corona\_sdk\_use\_daily\_docs" to true to have documentation lookups go to the Daily Build documentation.

### Current Gotchas

 * The order of items in the completions popup seems a little odd but is due to Sublime's "fuzzy" matching
 * Note that right clicking on an item wont move the cursor there so you can't right click on a term that's not at the insertion point and then pick "Corona SDK Docs" from the context menu as it's the position of the text cursor that determines what's looked up (left click on the item first)
 * Using Ctrl+B or Cmd+B to "build" the app by running it in the Simulator works well the first time you use it but unless you quit the Simulator before using it again you will soon have several running.  We are working on a fix for this (use the "Relaunch Simulator when Project is Modified" Simulator preference for a better workflow in the meantime)
 * Some of the completions have minor errors with nested optional parameters.  This will be fixed

### Reporting Issues

If some aspect of the plugin doesn't behave as expected be sure to include any console output when reporting the problem.  You can view the console using **View > Show Console** and copy and paste the information displayed there.
