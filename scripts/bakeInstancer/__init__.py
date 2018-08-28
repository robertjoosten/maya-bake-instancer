"""				
Bake an instancer node to individual animated pieces of geometry. Useful for 
people that haven't switched to Maya 2017 yet, where this is standard 
functionality.

.. figure:: /_images/bakeInstancerExample.gif
   :align: center
   
`Link to Video <https://vimeo.com/188421440>`_

Installation
============
* Extract the content of the .rar file anywhere on disk.
* Drag the bakeInstancer.mel file in Maya to permanently install the script.

Usage
=====
A button on the MiscTools shelf will be created that will allow easy access to
the ui, this way the user doesn't need to worry about any of the code. If user
wishes to not use the shelf button the following commands can be used.

Display the UI with the following code
::
    import bakeInstancer.ui
    bakeInstancer.ui.show()

Command line
::
    import bakeInstancer
    bakeInstancer.bake(
        instancer,
        start,
        end,
    )

Note
====
This script lets you bake an instancer node into individual animated pieces 
of geometry. Usefull for people that haven't switched over to Maya 2017 yet, 
where this is standard functionality.
"""
from commands import *

__author__    = "Robert Joosten"
__version__   = "0.7.1"
__email__     = "rwm.joosten@gmail.com"