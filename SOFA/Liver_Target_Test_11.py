# Required import for python
import Sofa
import numpy as np
from scipy import sparse
from scipy import linalg
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


# Choose in your script to activate or not the GUI
USE_GUI = True
exportCSV = True
showImage = False

def main():
    import SofaRuntime
    import Sofa.Gui

    root = Sofa.Core.Node("root")
    createScene(root)
    Sofa.Simulation.init(root)

    if not USE_GUI:
        for iteration in range(10):
            Sofa.Simulation.animate(root, root.dt.value)
    else:
        Sofa.Gui.GUIManager.Init("myscene", "qglviewer")
        Sofa.Gui.GUIManager.createGUI(root, __file__)
        Sofa.Gui.GUIManager.SetDimension(1080, 1080)
        Sofa.Gui.GUIManager.MainLoop(root)
        Sofa.Gui.GUIManager.closeGUI()


def createScene(root):
    root.gravity=[0, 0, -9.81]
    root.dt=0.02

    root.addObject("RequiredPlugin", pluginName=[
        'Sofa.Component.Collision.Detection.Algorithm',
        'Sofa.Component.Collision.Detection.Intersection',
        'Sofa.Component.Collision.Geometry',
        'Sofa.Component.Collision.Response.Contact',
        'Sofa.Component.Constraint.Projective',
        'Sofa.Component.IO.Mesh',
        'Sofa.Component.LinearSolver.Iterative',
        'Sofa.Component.Mapping.Linear',
        'Sofa.Component.Mass',
        'Sofa.Component.ODESolver.Backward',
        'Sofa.Component.SolidMechanics.FEM.Elastic',
        'Sofa.Component.StateContainer',
        'Sofa.Component.Topology.Container.Dynamic',
        'Sofa.Component.Visual',
        'Sofa.GL.Component.Rendering3D',
        'Sofa.Component.SolidMechanics.Spring',
        'Sofa.Component.MechanicalLoad',
        'Sofa.Component.Topology.Container.Constant',
        'Sofa.Component.SolidMechanics.FEM'
    ])

    root.addObject('DefaultAnimationLoop')

    root.addObject('VisualStyle', displayFlags="showCollisionModels")
    root.addObject('CollisionPipeline', name="CollisionPipeline")
    root.addObject('BruteForceBroadPhase', name="BroadPhase")
    root.addObject('BVHNarrowPhase', name="NarrowPhase")
    root.addObject('DefaultContactManager', name="CollisionResponse", response="PenalityContactForceField")
    root.addObject('DiscreteIntersection')

    root.addObject("MeshSTLLoader", name="LiverSurface", filename = r"C:\Users\monta\Desktop\Materie\Altro\Tirocinio\Liver_Database\3D_Slicer\liver_test\Liver_Outlier_11\Liver_Test_11.stl")
    root.addObject("MeshOBJLoader", name="ConstraintIDpoints", filename = r"C:\Users\monta\Desktop\Materie\Altro\Tirocinio\Liver_Database\3D_Slicer\liver_test\Liver_Outlier_11\Points-obj") 
    
    #Liver Parenchyma with TetrahedralCorotationalFEMForceField
    liver = root.addChild('Liver')
    liver.addObject('EulerImplicitSolver', name="cg_odesolver", rayleighStiffness="0.1", rayleighMass="0.1")
    liver.addObject('CGLinearSolver', name="linear_solver", iterations="25", tolerance="1e-09", threshold="1e-09")
    liver.addObject("MeshGmshLoader", name="meshLoader", filename = r"C:\Users\monta\Desktop\Materie\Altro\Tirocinio\Liver_Database\3D_Slicer\liver_test\Liver_Outlier_11\Liver_Test_11.msh")  
    liver.addObject('TetrahedronSetTopologyContainer', name="tetra", src="@meshLoader")
    liver.addObject('MechanicalObject', name="dofs", src="@meshLoader")
    liver.addObject('TetrahedronSetGeometryAlgorithms', template="Vec3d", name="TetraGeomAlgo")
    liver.addObject('DiagonalMass', name="Mass", massDensity="1.0")
    liver.addObject('TetrahedralCorotationalFEMForceField', template="Vec3d", name="TetraFEM", method="large", poissonRatio="0.26", youngModulus="5143")
    # constraint force
    liver.addObject('FixedConstraint', name="FixedConstraint", indices="@../ConstraintIDpoints.position")
    
    # constraint pressure
    # liver.addObject('FixedConstraint', name="FixedConstraint", indices="@../ConstraintIDpoints.position")
    
    #forces
    liver.addObject('ConstantForceField', force = "0 0 -2000", indices="@../ForceIDpoints.position")

    # Glisson capsule with TriangularBendingSprings
    liverCapsule = liver.addChild('GlissonCapsule')
    liverCapsule.addObject('MeshSTLLoader', name='CapsuleMesh', filename = r"C:\Users\monta\Desktop\Materie\Altro\Tirocinio\Liver_Database\3D_Slicer\liver_test\Liver_Outlier_11\Liver_Test_11.stl")
    liverCapsule.addObject('MechanicalObject', name='dofsCapsule', src="@CapsuleMesh")
    liverCapsule.addObject('TriangleSetTopologyContainer', name="tri", src="@CapsuleMesh")
    liverCapsule.addObject('TriangleSetGeometryAlgorithms', template="Vec3d", name="TriGeomAlgo")
    liverCapsule.addObject('TriangularBendingSprings', template="Vec3d", name="BendingSprings", stiffness=10000, damping=0.2)
    liverCapsule.addObject('BarycentricMapping', name="VisualMappingCapsule", input="@../dofs", output="@dofsCapsule")
    
    # pressure
    # liverCapsule.addObject('SurfacePressureForceField', name="tractionForce", template="Vec3d", pressure="1000.0", pulseMode="true", pressureSpeed="20.0", triangleIndices = "@CapsuleMesh.triangles")
    
    #visualization Parenchyma
    liverVisu = liver.addChild('visualization')
    liverVisu.addObject('OglModel', name='VisualModelParenchyma', color='0.8 0.2 0.2 1.0', src='@../meshLoader')
    liverVisu.addObject('BarycentricMapping', name="VisualMappingParenchyma", input="@../dofs", output="@VisualModelParenchyma")

    #visualization Glisson's Capsule
    capsuleVisu = liverCapsule.addChild('capsule-visualization')
    capsuleVisu.addObject('OglModel', name='visualCapsule', color='0.2 0.8 0.2 1.0', src='@../CapsuleMesh')
    capsuleVisu.addObject('IdentityMapping')

    return root

# Function used only if this script is called from a python environment
if __name__ == '__main__':
    main()
