from maya import cmds, OpenMaya, OpenMayaFX
from . import utils


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
    :raises RuntimeError: When the instancer doesn't exist
    :raises RuntimeError: When there are no particles attached
    """
    # store all particle information in data variable
    data = {}
    
    # get instance
    if not cmds.objExists(instancerName):
        raise RuntimeError("Instancer doesn't exist!")
        
    # set visible
    cmds.setAttr("{0}.visibility".format(instancerName), 1)
    
    instancerObj = utils.asMObject(instancerName)
    instancerDag = utils.asMDagPath(instancerObj)
    instancer = OpenMayaFX.MFnInstancer(instancerDag)
    
    # get particles
    particleName = cmds.listConnections(
        "{0}.inputPoints".format(instancerName)
    )
    if not particleName:
        raise RuntimeError("No particles connected!")
    
    particleName = particleName[0]
    particleObj = utils.asMObject(particleName)
    particleDag = utils.asMDagPath(particleObj)
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
        n="{0}_bake_1".format(instancerName)
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
                    utils.keyVisibility(path, i, 0)
                    del(data[p])
                
                # check if parent is the same as previous
                elif parent != oldParent:
                    # hide mesh and delete particle id data
                    utils.keyVisibility(path, i, 0)
                    del(data[p])

            # duplicate path if index not in data
            if not data.get(p):
                # get parent name
                parentShort = parent.split("|")[-1].split(":")[-1]
                
                # duplicate mesh
                name = "{0}_{1}_1".format(instancerName, parentShort)
                path = cmds.duplicate(parent, n=name)[0]
                path = cmds.parent(path, container)[0]
                
                # handle visibility
                utils.keyVisibility(path, i, 1)
                
                # get dag
                dag = utils.asMDagPath(utils.asMObject(path))
                
                # get matrix
                transform = utils.asMFnTransform(dag)
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
            
            transform = utils.asMFnTransform(dag)
            transform.set(m)
            
            # set keyframes
            utils.keyTransform(path, i)
            
        # update progress
        if progress:
            progress.setValue(i+1-start) 
            
    return container
