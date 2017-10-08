from maya import cmds, OpenMayaUI

# import pyside, do qt version check for maya 2017 >
qtVersion = cmds.about(qtVersion=True)
if qtVersion.startswith("4") or type(qtVersion) != str:
    from PySide.QtGui import *
    from PySide.QtCore import *
    import shiboken
else:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    import shiboken2 as shiboken
    
# import command line bake
from . import bake
    
# ----------------------------------------------------------------------------
  
FONT = QFont()
FONT.setFamily("Consolas")

BOLT_FONT = QFont()
BOLT_FONT.setFamily("Consolas")
BOLT_FONT.setWeight(100)     
        
def mayaWindow():
    """
    Get Maya's main window.
    
    :rtype: QMainWindow
    """
    window = OpenMayaUI.MQtUtil.mainWindow()
    window = shiboken.wrapInstance(long(window), QMainWindow)
    
    return window  
    
# ----------------------------------------------------------------------------

def getInstancers():
    """
    Get all instancer nodes in the scene.
    
    :return: Instancer node list
    :rtype: list
    """
    return cmds.ls(type="instancer") or []
        
def getFrameRange():
    """
    Read the current playback options to get the start and end frame.
    Float values are converted to integers for baking reasons.
    
    :return: Start and end frame current playback options
    :rtype: tuple
    """
    start = cmds.playbackOptions(query=True, minTime=True)
    end = cmds.playbackOptions(query=True, maxTime=True)
    
    return int(start), int(end)

# ----------------------------------------------------------------------------

class InstancerSelectorWidget(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        
        # variable
        instancers = getInstancers()
        
        # create ui
        layout = QHBoxLayout(self)
        layout.setContentsMargins(3, 0, 3, 0)
        layout.setSpacing(0)
        
        # create label
        label = QLabel(self)
        label.setText("Instancer:")
        label.setFont(FONT)
        label.setFixedWidth(100)
        layout.addWidget(label)
        
        # create combobox
        self.instancerCB = QComboBox(self)
        self.instancerCB.setFont(FONT)
        self.instancerCB.addItems(instancers)
        layout.addWidget(self.instancerCB)
        
    # ------------------------------------------------------------------------
    
    def getInstancer(self):
        """
        Get selected instancer.
        
        :rtype: str
        """
        return self.instancerCB.currentText()
        
class FrameRangeSelectorWidget(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        
        # variable
        self.spinBoxes = []
        start, end = getFrameRange()
        
        # create ui
        layout = QHBoxLayout(self)
        layout.setContentsMargins(3, 0, 3, 0)
        layout.setSpacing(0)
        
        # create label
        label = QLabel(self)
        label.setText("Time Range: ")
        label.setFont(FONT)
        label.setFixedWidth(100)
        layout.addWidget(label)
        
        # create spin boxes
        for value in [start, end]:
            spinBox = QSpinBox(self)
            spinBox.setFont(FONT)
            spinBox.setMinimum(-99999)
            spinBox.setMaximum(99999)
            spinBox.setValue(value)
            layout.addWidget(spinBox)
            
            self.spinBoxes.append(spinBox)

    # ------------------------------------------------------------------------
    
    def getFrameRange(self):
        """
        Get selected frame range.
        
        :return: Start and end frame as a tuple
        :rtype: tuple
        """
        return tuple([s.value() for s in self.spinBoxes])

class BakeInstancerWidget(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        
        # set ui
        self.setParent(parent)   

        self.setWindowTitle("Bake Instancer")           
        self.resize(300, 50)
        
        # set icon
        self.setWindowFlags(Qt.Window)   
        self.setWindowIcon(QIcon(":/instancer.png"))
                
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
    
        # instancer selector
        self.instancer = InstancerSelectorWidget(self)
        layout.addWidget(self.instancer)
        
        # frame range selector
        self.frameRange = FrameRangeSelectorWidget(self)
        layout.addWidget(self.frameRange)
       
        # create bake button
        button = QPushButton(self)
        button.setText("Bake")
        button.setFont(BOLT_FONT)
        button.released.connect(self.bake)
        layout.addWidget(button) 
        
        # create spacer
        spacer = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)
        
        # create progress bar
        self.progressBar = QProgressBar(self)   
        self.progressBar.setVisible(False)
        layout.addWidget(self.progressBar)
        
        # disable bake button if no instancer is selected
        if not self.instancer.getInstancer():
            button.setEnabled(False)
        
    # ------------------------------------------------------------------------
        
    def bake(self): 
        """
        Get the instancer and frame range to bake from the ui and call the 
        command line bake function.
        """
        # get arguments
        instancer = self.instancer.getInstancer()
        start, end = self.frameRange.getFrameRange()
        
        # show progress bar
        self.progressBar.setVisible(True)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(end+1-start)
        self.progressBar.setValue(0)  
        
        # bake
        bake(instancer, start, end, self.progressBar)
       
def show():
    bakeInstancer = BakeInstancerWidget(mayaWindow())
    bakeInstancer.show()