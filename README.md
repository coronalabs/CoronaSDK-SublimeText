Corona Editor
=============

Corona Editor is the official ***Corona SDK*** plugin for ***Sublime Text***.  Designed to make building apps even easier by adding functionality to ***Sublime Text*** to improve developer productivity.

## Installation Instructions

1. Install the ***Sublime Text*** **Package Control** plugin if you don't already have it: [https://sublime.wbond.net/installation](https://sublime.wbond.net/installation)
1. Choose: **Tools** > **Command Palette...** > **Package Control: Install Package**
1. Find **Corona Editor** by typing in the search field, click on it to install it
1. Restart ***Sublime Text*** or reopen any .lua files to see the new features

Alternatively, if you are comfortable doing manual installs of Sublime Text plugins, you can download the plugin from [https://github.com/coronalabs/CoronaSDK-SublimeText/archive/master.zip](here).

## Using the Plugin

After restarting ***Sublime Text*** you'll have several new features available when editing .lua files.

There are several ***Sublime Text*** User Preferences that can be set to fine tune the behavior of the plugin.  You can find information on setting User Preferences [http://www.sublimetext.com/docs/3/settings.html](here).

### Completion 
Completion works for all API calls and constants (correctly handling periods in the name).  Fuzzy matching is optionally done to increase the chances of finding the item you are looking for.

##### Preferences
 * **corona_sdk_completion** (default: True)

	If you don't like Corona Editor's completion you can turn it off entirely using this preference.

 * **corona_sdk_use_daily_docs** (default: False)

	Tell the completion system to use the "Daily Build" completions rather than the "Public Release" ones.

 * **corona_sdk_use_fuzzy_completion** (default: True)

	Turn off "fuzzy completion" and just complete based on the characters typed so far as a prefix.

 * **corona_sdk_complete_periods** (default: True)

	Corona Editor turns off the special meaning of periods as "word separators" in Sublime Text to make Corona completions work better.  If you like to use cursor movement keys like "Alt+Arrow" to move to the periods in function calls you might want to turn this off.  The most obvious effect of turning it off is that when you type a period all the completions disappear until you type another character.

 * **corona_sdk_auto_build** (default: False)

	If you set this to "True" the Sublime Text "build" command will be issued any time you save a Lua file.

##### Current Gotchas
 * The order of items in the completions popup seems a little odd but is due to Sublime's "fuzzy" matching

### Documentation Lookup
Documentation can be called up by placing the cursor on an API call (or selecting it) and either hitting **F1** or choosing **Corona SDK Docs** from the context menu.  Lua keywords will be looked up in the Lua documentation.  If the context of something isn't recognized, a search of the Corona SDK documentation will be initiated.


##### Preferences
 * **corona_sdk_use_daily_docs** (default: False)

 	Opt to go to the "Daily Build" documentation instead of the "Public Release" documentation.

##### Current Gotchas
 * Note that right clicking on an item wont move the cursor there so you can't right click on a term that's not at the insertion point and then pick "Corona SDK Docs" from the context menu as it's the position of the text cursor that determines what's looked up (left click on the item first)
 * Some of the completions have minor errors with nested optional parameters.

### Build System
The current app can be run in the Simulator by pressing Ctrl+B (Windows) or Cmd+B (MacOSX).  Debug output appears in the "build" window in ***Sublime Text***

### Syntax Highlighting
Syntax highlighting of Lua with Corona SDK calls is done (choose **View > Syntax > Corona SDK Lua** to enable this)

### Miscellaneous
 * A shortcut to the ***Sublime Text*** **Goto Anything...** function list has been added to the context menu as `Function Navigator...`.

## Reporting Issues

You can find discussion about Corona Editor on our [http://forums.coronalabs.com/forum/630-corona-editor/](Forum).

If some aspect of the plugin doesn't behave as expected be sure to include any console output when reporting the problem.  You can view the console using **View > Show Console** and copy and paste the information displayed there.
