import math
from maya import cmds, OpenMaya


def asMObject(path):
    """
    str -> OpenMaya.MObject

    :param str path: Path to Maya object
    :rtype: OpenMaya.MObject
    """
    selectionList = OpenMaya.MSelectionList()
    selectionList.add(path)
    
    obj = OpenMaya.MObject()
    selectionList.getDependNode(0, obj)
    return obj


def asMDagPath(obj):
    """
    OpenMaya.MObject -> OpenMaya.MDagPath

    :param OpenMaya.MObject obj:
    :rtype: OpenMaya.MDagPath
    """
    return OpenMaya.MDagPath.getAPathTo(obj)


def asMFnTransform(dag):
    """
    OpenMaya.MDagPath -> OpenMaya.MFnTransform

    :param OpenMaya.MDagPath dag:
    :rtype: OpenMaya.MFnTransform
    """
    return OpenMaya.MFnTransform(dag.transform())


# ----------------------------------------------------------------------------         


def keyVisibility(path, t, v):
    """
    Key visibility, will create a switch putting a a key with the specified
    value on the time parsed. But will also put the reverse value on t-1.

    :param str path: path to Maya object
    :param int t: time
    :param int v: value
    """
    cmds.setKeyframe(path, v=math.fabs(v-1), t=t-1, at="visibility")
    cmds.setKeyframe(path, v=v, t=t, at="visibility")


def keyTransform(path, t):
    """
    Key transform, loop over translate, rotate and scale and set keys
    with their current value.

    :param str path: path to Maya object
    :param int t: time
    """
    for attr in ["translate", "rotate", "scale"]:
        cmds.setKeyframe(path, t=t, at=attr, itt="spline", ott="spline")


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