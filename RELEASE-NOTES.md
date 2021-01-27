## Solar2D Editor Release Notes

Always check the [README](https://github.com/coronalabs/CoronaSDK-SublimeText/blob/master/README.md) for the latest information.

### 1.8.0

 * Changed branding to Solar2D
 
 * Changed syntax name to Lua (Solar2D)
 
 * Updated autocomplete file - event.xDelta/yDelta, sqlite3, lateUpdate, transition.resumeAll(), pauseAll(), cancelAll() and timer.resumeAll(), pauseAll(), cancelAll()
 
 * Changed http:// calls to https://

### 1.7.9

 * Fix syntax file loading
 
 * Correct file name
 
 * Remove code causing crash
 
 * Dynamically generate path for syntax file

### 1.7.8

 * New release to make package control happy :)

### 1.7.7.2

 * Trying to fix the crash

### 1.7.7.1

 * Added settings to extension list

### 1.7.7

 * Fix plugin crash

### 1.7.6

 * Fix plugin to set syntax to new language format

### 1.7.5

 * Quick fix for new language format transition

### 1.7.4

 * Syntax update and autocomplete extras

### 1.7.3

 * Fix issue with spaces and special characters in pathnames on macOS

### 1.7.2

 * Fix issue with spaces and special characters in pathnames on macOS

### 1.7.1

 * Fix issue where 'Run Project' didn't work on Windows

### 1.7.0

 * Fix issue with inline function definition syntax coloring (fixes #20)

 * Look for the Simulator in the new "Corona" location (rather than "CoronaSDK") (fixes #23)

 * Make **Super+B** run the project in the Simulator (synonym for **Super+F10**)

 * Improve clickability of errors and warnings which contain file and line number information

 * Update completions to latest version of Corona

### 1.6.1

 * Rows and columns in the current tab are no longer reset when using **Super+F10** unless they were created by the Corona Editor Debugger (a corollary of this is if you create your own rows and columns the Debugger can't create its own and its functionality will be reduced)

 * All errors in the build panel should once more be clickable to go to that location in the source code

 * A new setting `corona_sdk_simulator_show_console` has been added, which, if set to true, will cause the Corona Simulator Console to be shown when running a project with **Super+F10**

### 1.6.0

 * Debugger improvements
	 * fixed issue with a hang after pressing Shift+F10
	 * fixed bug with spaces in project pathname
	 * current status is now displayed in the "Console" pane
	 * "Console" output is now cleaner
	 * Generally improved reliability

 * On OS X, **Corona Editor > Run Project** now uses the most recent Daily Build in the /Applications folder by default

 * Removed "build system" for Corona projects (**Corona Editor > Run Project** / **Super+F10** is much more reliable)

 * Added "Clear Build Panel" command to main menu and context menu

 * Fixed indentation of elseif blocks

 * Latest completions (up to date for build 2016.2803)

### 1.5.0

 * Various debugger improvements including:
	 * syntax coloring of debugger panes
	 * avoiding problematic debugger commands in certain versions of Corona Simulator
	 * better display of file paths
	 * table variable contents are shown correctly
	 * formatting of variable contents when inspecting

 * Fix error in `class` snippet (fixes issue #17)

 * Update snippets

 * Add support for Simulator version detection

 * Improved completion generation and latest completions (for build 2014.2511)

 * Also look for settings in the main Sublime Text prefs. This means Corona Editor settings can be set in either the Corona Editor settings file (`~/Library/Application Support/Sublime Text 3/Packages/User/Corona Editor.sublime-settings`) or the main Sublime Text settings file (`~/Library/Application Support/Sublime Text 3/Packages/User/Preferences.sublime-settings`)

 * Add `-no-console` option to Mac Simulator invocation

 * A message is shown on the status line if Corona SDK completion is not being done because a .lua file does not have `Corona SDK Lua` syntax set

 * Fixed various Windows issues
	 * About box misbehavior
	 * Correct regex for finding errors
	 * Fix snippets path

 * Latest completions (up to date for release 2014.2511).

 * Fixes for ***Sublime Text 2*** compatibility.

 * Tweaks to build subsystem.

 * You can now use **Corona Editor > Debugger > Stop** to close the additional panes even if the editor doesn't think the debugger is running.

 * Allow errors to be double-clicked in build panel when **Corona Editor >Run Project** is used.

 * Save all modified files before running project (but only if modified).

 * Improved reliability of **Corona Editor > Run Project**.

 * Tweaked syntax highlighting.

 * Completion improvements
	 * Added capability to strip whitespace from completions (thx personalnadir); set `corona_sdk_completions_strip_white_space` to activate
	 * Fixed various issues with completion and periods.  Lots of testing needed
	 * Files with `Corona SDK Lua` syntax type set are candidates for Corona Editor completion.  New, unsaved files are assumed to be Corona SDK Lua files unless `corona_sdk_default_new_file_to_corona_lua` is set to false
	 * Handle invalid completion data files more gracefully
	 * Latest completions from Corona SDK documentation

 * Set user preference `corona_sdk_debug` to true to turn on debug output in the ***Sublime Text*** console (works for certain modules).

 * Add instructions in the README for using the development version.

### 1.0.0

 * **Debugger**
 	A debugger for Corona apps an be accessed using the **Corona Editor > Debugger** menu.

 * **Snippets**
 	A library of code snippets is available via the **Corona Editor > Snippets** menu.

 * **Completions**
	Completions now use the "syntax" of the current file so they work before a file is saved (if you set the syntax using **View > Syntax > Corona SDK Lua**.  Completions have been updated and now include a "legacy" option.

 * **Menu Integration**
 	Most features are available in the "Corona Editor" menu.

### 0.8.9

 * **Completions**
	Various improvements to completion including many more completions and the inclusion of "types". 
	Colons are now handled correctly so Lua objects now complete properly.

### 0.8.8

 * **Completions**
	Completions now (optionally) do fuzzy matching on the available
	completions. Behavior of completions around periods has been improved.
	There are completions for both "public" and "daily" APIs.

 * **Building works correctly**
    Multiple builds now result in just one Simulator whose output goes into the build results window on MacOSX and Windows.  This requires Daily Build 1240 or higher (on older builds you'll still get multiple Simulators started).  Also fixed issue with "\Program Files (x86)" folder on Windows.

 * **Building in projects works**
 	It's now possible to hit Super+B on any .lua file in a project and have the Simulator load `main.lua` as expected.

 * **Documentation Lookup**
	Fine tuned documentation lookup so that "lfs", "socket", "sqlite3"
	trigger searches.

### 0.8.7

 * **Fixed issue with completions**
    A rewhacked and improved completion mechanism is coming but in the
    meantime this fixes an issue with the rename of the plugin in ***Sublime Text 3***.

 * **Improved documentation lookup**
    Documentation lookup has been made smarter so that it displays the
    correct page more often.  If it can't display a particular page it now
    defaults to searching either the online Lua documentation or the Corona
    SDK documentation depending on context.

 * **Improved syntax detection**
    The detection of function definitions has been extended to cover both
    styles of Lua function definitions:
    ```
         function f () body end
    ```
    and
    ```
         f = function () body end
    ```
    This improves the list of functions displayed by Super+R in particular.

 * **Added "Function Navigator..." menu item**
    To make accessing the list of functions defined in the current source
    file more discoverable a menu item has been added to the right-click
    context menu which is the equivalent of "Super+R"

