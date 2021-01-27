Solar2D Editor
=============

***Solar2D Editor*** (rebranded Corona Editor) is the official [***Solar2D***](https://solar2d.com/) plugin for ***Sublime Text***.  Designed to make building apps even easier by adding functionality to ***Sublime Text*** to improve developer productivity.

## Sublime Text Version

[***Sublime Text 3***](https://www.sublimetext.com/) is required to use Solar2D Editor.
 
## Installation Instructions

1. Install the ***Sublime Text*** **Package Control** plugin if you don't already have it using **Tools > Command Palette... > Install Package Control**
1. When that's installed, in ***Sublime Text*** choose: **Tools > Command Palette... > Package Control: Install Package**
1. Find **Corona Editor** by typing in the search field, click on it to install it
1. Restart ***Sublime Text*** to see the new features

If you want to help test the latest development version of ***Solar2D Editor*** you can configure **Package Control** to grab it instead of the official release version by following these steps:

1. In ***Sublime Text*** choose: **Tools > Command Palette... > Package Control: Remove Package** and uninstall any installed version of ***Corona Editor***
1. Choose: **Tools > Command Palette... > Package Control: Add Repository**
1. Enter `https://github.com/coronalabs/CoronaSDK-SublimeText`
1. Choose: **Tools > Command Palette... > Package Control: Install Package**
1. Find **CoronaSDK-SublimeText** (or, on some machines, **Corona Editor - Daily Build**) by typing in the search field, click on it to install it
1. Restart ***Sublime Text*** or reopen any .lua files to see the new features

Alternatively, if you are comfortable doing manual installs of Sublime Text plugins and want to run the latest development version, you can download the plugin from [https://github.com/coronalabs/CoronaSDK-SublimeText/archive/master.zip](https://github.com/coronalabs/CoronaSDK-SublimeText/archive/master.zip)

If you install the tip from Github please report any issues using the Issues page on Github: [https://github.com/coronalabs/CoronaSDK-SublimeText/issues](https://github.com/coronalabs/CoronaSDK-SublimeText/issues)

## Using the Plugin

After restarting ***Sublime Text*** you'll have several new features  available in the **Solar2D Editor** menu and in the context menu when editing Solar2D .lua files.  Most of the features of the plugin rely on the current **Syntax** setting so when editing files you should use **View > Syntax > Lua (Solar2D)** command to set the correct syntax for the file.  You will probably also want to change ***Sublime Text***'s default for .lua files by choosing **View > Syntax > Open all with current extension as... > Lua (Solar2D)** when you have a .lua file open in the editor.

If the syntax option is set correctly you'll see it displayed in the bottom righthand corner of the ***Sublime Text*** window.

There are several ***Sublime Text*** User Preferences that can be set to fine tune the behavior of the plugin.  You can find information on setting User Preferences here [http://www.sublimetext.com/docs/3/settings.html](http://www.sublimetext.com/docs/3/settings.html).

### Debugger
Debugger allows code to be single stepped, variables to be examined and breakpoints to be set.  You can run the debugger using the **Solar2D Editor** menu from any file in the project and it will automatically find **main.lua**.  Right click on a code line in the editor and choose **Toggle Breakpoint** to turn a breakpoint on or off.  Select the name of a variable and choose **Inspect Variable** from the context menu to see its value.

The following keys also control the Debugger:

| Key       | Action            |
| ---------:| ----------------- |
| F10       | Run Project in the Debugger or continue project execution |
| Shift+F10 | Stop debugger     |
| Super+F10 | Run Project       |
| F11       | Step over         |
| Shift+F11 | Step into         |

A simpler alternative to the **Build** command in ***Sublime Text*** is the **Run Project** command in the **Solar2D Editor** menu (or Super+F10).  It doesn't have all the bells and whistles of the build system but it is quick and easy.  It is also better at finding your project's `main.lua` if you aren't using ***Sublime Text***'s projects.  Super+B (usually bound to the **Build** command) is now bound to the **Run Project** command for Solar2D Lua files. 

On macOS, if you install Solar2D in **/Applications** without changing the default name, it will use the highest numbered (most recent) build to run the project (to change this behavior, see `corona_sdk_simulator_path` below).

##### Preferences
 * `corona_sdk_simulator_path` (default: system dependent)

	Set this to the path of your Solar2D Simulator if it's not installed
	in the default location for your operating system (remember to double
	the backslashes in Windows paths).  You can also set this in the `build.settings`
	file of individual projects to customize the version of the Solar2D Simulator that
	is used for each project (note that the Lua syntax for the `build.settings` file
	is different to the JSON syntax of the ***Sublime Text*** preference files in that
	the name of the preference is not quoted in Lua).

 * `corona_sdk_simulator_show_console` (default: false)
 
    Set this to true to have the Solar2D Simulator Console be shown when running a project with **Super+F10** (or **Super+B**).

##### Current Gotchas
 * If you **Run** the project and it doesn't hit a breakpoint, you'll have to stop and restart to regain control (in particular, setting a breakpoint on a line of code you know is being executed wont stop the program).
 * Single stepping through "internal locations" is tedious.
 * There's an implicit breakpoint set on the first line of main.lua so to hit your own first breakpoint you need to run once to start the debugger and stop on the first line then run again to continue until you hit your own breakpoint.
 * If you create rows and columns in using ***Sublime Text***'s **View > Layout** command in the current tab, the debugger wont create its own panes and its functionality will be reduced.

### Completion
Completion works for all API calls and constants (correctly handling periods in the name).  Fuzzy matching is optionally done to increase the chances of finding the item you are looking for.  Completion relies on the current **Syntax** setting so when creating new files you should use **View > Syntax > Lua (Solar2D)** command to set the correct syntax for the new file.  You will probably also want to change ***Sublime Text***'s default for .lua files by choosing **View > Syntax > Open all with current extension as... > Lua (Solar2D)** when you have a .lua file open in the editor.

##### Preferences
 * `corona_sdk_completion` (default: True)

	If you don't like Solar2D Editor's completion you can turn it off entirely using this preference.

 * `corona_sdk_use_fuzzy_completion` (default: True)

	Turn off "fuzzy completion" and just complete based on the characters typed so far as a prefix.

 * `corona_sdk_complete_periods` (default: True)

	Solar2D Editor turns off the special meaning of periods as "word separators" in Sublime Text to make Solar2D completions work better.  If you like to use cursor movement keys like "Alt+Arrow" to move to the periods in function calls you might want to turn this off.  The most obvious effect of turning it off is that when you type a period all the completions disappear until you type another character.

 * `corona_sdk_use_docset` (default: `public`)

	Choose which completion set you want to use.  Can be one of `public` (the default), `legacy`(deprecated) or `daily`(deprecated).

 * `corona_completions_strip_white_space` (default: False)

	Set to true if you want items to be completed with minimal whitespace included.

##### Current Gotchas
 * The order of items in the completions popup seems a little odd but is due to Sublime Text's "fuzzy" matching

 * Some of the completions may have minor errors with nested optional parameters due to the way they are automatically generated.

### Documentation Lookup
Documentation can be called up by placing the cursor on an API call (or selecting it) and either hitting **F1** or choosing **Solar2D Docs** from the context menu.  Lua keywords will be looked up in the Lua documentation.  If the context of something isn't recognized, a search of the Solar2D documentation will be initiated.

##### Current Gotchas
 * Note that right clicking on an item wont move the cursor there so you can't right click on a term that's not at the insertion point and then pick **Solar2D Docs** from the context menu as it's the position of the text cursor that determines what's looked up (left click on the item first)

### Snippets
A selection of commonly used code fragments and templates is available via the **Solar2D Editor > Snippets** menu.  Selecting an item from a submenu will insert its code at the current insertion point in the file.

A default set of snippets is created in the ***Sublime Text*** support folder `Packages/User/Corona Editor/Snippets`.  You can create your own folders and files to add to the default set.  Files should either be ***Sublime Text*** `.sublime-snippet` files or plain text files.  The contents of plain text files are just inserted when chosen unless they exactly match a completion entry in which case the completion is looked up and they work like a normal completion (you can tab between the arguments) which provides a way to make menus of hard to remember API calls.

### Build System
The **Run Project** command in the **Solar2D Editor** menu (or Super+B or Super+F10) is a simpler alternative to the **Build** command in ***Sublime Text*** (see above for more information).

### Syntax Highlighting
Syntax highlighting of Lua with Solar2D calls is done (choose **View > Syntax > Lua (Solar2D)** to enable this).  You will probably also want to change ***Sublime Text***'s default for .lua files by choosing **View > Syntax > Open all with current extension as... > Lua (Solar2D)** when you have a .lua file open in the editor.

### Miscellaneous
 * A shortcut to the ***Sublime Text*** **Goto Anything...** function list has been added to the context menu as **Function Navigator...**. This lists the functions defined in the current file and choosing one takes you to that definition.
 * The **Solar2D Editor** menu has a **Show/Hide Build Panel** command to toggle the visibility of the Build Results panel (which displays the output of the Simulator).  Note that hiding the panel clears its contents.

## Reporting Issues

You can find discussion about Solar2D Editor on [the forums](https://forums.solar2d.com/c/corona/corona-editor/91).

If some aspect of the plugin doesn't behave as expected be sure to include any console output when reporting the problem.  You can view the console using **View > Show Console** and copy and paste the information displayed there.

## Known Issues

 * Syntax highlighting is incorrect for function definitions that look like:
 `````
 local back=simplebutton.create("Back",function() menumanager.openMenu("main") end)
 `````

## Platform Specific Advice

### Mac

You may want to set the `Use all F1, F2, etc. keys as standard function keys` option in **System Preferences > Keyboard** to make using F10 and F11 easier for the debugger.  Alternatively you may want to reassign the keys used to drive the debugger; information on how to this can be found at [http://www.sublimetext.com/docs/key-bindings](http://www.sublimetext.com/docs/key-bindings)

## Thanks

Many thanks to the Solar2D users who have provided feedback and suggestions to make Solar2D Editor even better.  Particular thanks to _personalnadir_, _develephant_, _givemeyourgits_ and _landoncope_ for their contributions and help.
