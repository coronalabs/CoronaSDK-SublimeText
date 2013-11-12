## Corona Editor Release Notes

Always check [https://github.com/coronalabs/CoronaSDK-SublimeText/blob/master/README.md](the README) for the latest information.

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

