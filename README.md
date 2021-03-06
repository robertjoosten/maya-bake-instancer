# maya-bake-instancer
Bake an instancer node to individual animated pieces of geometry. Useful for people that haven't switched to Maya 2017 yet, where this is standard functionality.

<p align="center"><img src="docs/_images/bakeInstancerExample.gif?raw=true"></p>
<a href="https://vimeo.com/188421440" target="_blank"><p align="center">Click for video</p></a>

## Installation
* Extract the content of the .rar file anywhere on disk.
* Drag the bakeInstancer.mel file in Maya to permanently install the script.

## Usage
A button on the MiscTools shelf will be created that will allow easy access to the ui, this way the user doesn't need to worry about any of the code.
If user wishes to not use the shelf button the following commands can be used.

Command line:
```python
import bakeInstancer
bakeInstancer.bake(instancer, start, end)
```

Display UI:
```python
import bakeInstancer.ui
bakeInstancer.ui.show()
```
