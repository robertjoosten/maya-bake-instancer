"""					
I N S T A L L A T I O N:
    Copy the "rjBakeInstancer" folder to your Maya scripts directory:
        C:\Users\<USER>\Documents\maya\scripts

U S A G E:
    Display the UI with the following code:
        import rjBakeInstancer.ui
        rjBakeInstancer.ui.show()
    
    Command line:
        import rjBakeInstancer
        rjBakeInstancer.bake(
            instancer,
            start,
            end,
        )

N O T E:
    This script lets you bake an instancer node into individual animated
    pieces of geometry. Usefull for people that haven't switched over
    to Maya 2017 yet, where this is standard functionality.
"""

import math
from maya import cmds, OpenMaya, OpenMayaFX
 
__author__    = "Robert Joosten"
__version__   = "0.7.1"
__email__     = "rwm.joosten@gmail.com"

def bake(instancerName, start, end, progress=None):
    """
    Process an instancer node over the specified frame range, reading the 
    positions and objects. With this data objects are duplicated and 
    positioned to mimic the instancer. With the particle data individual 
    objects can be matched over the different frames and animated. When
    a particle "dies", the visibility is turned off.

    :param str instancerName: Name if the instancer to bake
    :param int start: Start frame
    :param int end: End frame
    :param QProgressBar progress: Update ui ( Optional )
    :return: Group that contains all of the baked information
    :rtype: str
    """
    # store all particle information in data variable
    data = {}
    
    # get instance
    if not cmds.objExists(instancerName):
        raise("Instancer doesn't exist!")
        return
        
    # set visible
    cmds.setAttr("{0}.visibility".format(instancerName), 1)
    
    instancerObj = asMObject(instancerName)
    instancerDag = asMDagPath(instancerObj)
    instancer = OpenMayaFX.MFnInstancer(instancerDag)
    
    # get particles
    particleName = cmds.listConnections(
        "{0}.inputPoints".format(instancerName)
    )
    if not particleName:
        raise("No particles connected!")
        return
    
    particleName = particleName[0]
    particleObj = asMObject(particleName)
    particleDag = asMDagPath(particleObj)
    particle = OpenMayaFX.MFnParticleSystem(particleDag)    

    # variables
    ages = OpenMaya.MDoubleArray()
    paths = OpenMaya.MDagPathArray()
    matrices = OpenMaya.MMatrixArray()
    particleIndices = OpenMaya.MIntArray()
    pathIndices = OpenMaya.MIntArray()
    
    # create container group
    container = cmds.group(
        world=True, 
        empty=True, 
        n=instancerName + "_bake_1"
    )
    
    # loop time
    for i in range(start, end+1):
        # set time
        cmds.currentTime(i)
        
        # query instancer information
        instancer.allInstances(
            paths, 
            matrices, 
            particleIndices, 
            pathIndices
        )
        
        # query particle information
        particle.age(ages)
        
        # loop particle instances
        num = matrices.length()
        for j in range(num):
            # get particles index
            p = particleIndices[j]
            
            # get parent
            parent = paths[pathIndices[j]].fullPathName()
            
            # get age
            age = ages[j]
            
            if data.get(p):
                # get path and age
                path = data[p].get("path")
                
                oldAge = data[p].get("age")
                oldParent = data[p].get("parent")
                
                # check if age is less than previous
                if age < oldAge:
                    # hide mesh and delete particle id data
                    keyVisibility(path, i, 0)
                    del(data[p])
                
                # check if parent is the same as previous
                elif parent != oldParent:
                    # hide mesh and delete particle id data
                    keyVisibility(path, i, 0)
                    del(data[p])

            # duplicate path if index not in data
            if not data.get(p):
                # get parent name
                parentShort = parent.split("|")[-1].split(":")[-1]
                
                # duplicate mesh
                name = instancerName + "_" + parentShort + "_1"
                path = cmds.duplicate(parent, n=name)[0]
                path = cmds.parent(path, container)[0]
                
                # handle visibility
                keyVisibility(path, i, 1)
                
                # get dag
                dag = asMDagPath(asMObject(path))
                
                # get matrix
                transform = asMFnTransform(dag)
                matrix = transform.transformation().asMatrix()
                
                # store variables
                data[p] = {}
                data[p]["path"] = path
                data[p]["dag"] = dag
                data[p]["matrix"] = matrix
                data[p]["parent"] = parent
            
            # get variables
            path = data[p].get("path")
            dag = data[p].get("dag")
            matrix = data[p].get("matrix")
            
            # store age
            data[p]["age"] = age
                
            # set matrix
            m = matrix*matrices[j]
            m = OpenMaya.MTransformationMatrix(m)
            
            transform = asMFnTransform(dag)
            transform.set(m)
            
            # set keyframes
            keyTransform(path, i)
            
        # update progress
        if progress:
            progress.setValue(i+1-start) 
            
    return container

# ----------------------------------------------------------------------------             
            
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
