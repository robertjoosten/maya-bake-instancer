# rjBakeInstancer
Bake an instancer node to individual animated pieces of geometry. Useful for people that haven't switched to Maya 2017 yet, where this is standard functionality.

<p align="center"><img src="https://github.com/robertjoosten/rjBakeInstancer/blob/master/README.gif"></p>
<a href="https://vimeo.com/188421440" target="_blank"><p align="center">Click for video</p></a>

## Installation
Copy the **rjBakeInstancer** folder to your Maya scripts directory:
> C:\Users\<USER>\Documents\maya\scripts

## Usage
Command line:
```python
import rjBakeInstancer
rjBakeInstancer.bake(
    instancer,
    start,
    end,
)
```

Display UI:
```python
import rjBakeInstancer.ui
rjBakeInstancer.ui.show()
```

