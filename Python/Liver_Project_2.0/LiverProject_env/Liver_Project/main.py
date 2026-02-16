import sys

sys.path.append(r'C:\Users\monta\Desktop\Materie\Altro\Tirocinio\Python\Liver_Project_2.0\LiverProject_env\Liver_Project\DataAnalisys\SSA')
sys.path.append(r'C:\Users\monta\Desktop\Materie\Altro\Tirocinio\Python\Liver_Project_2.0\LiverProject_env\Liver_Project\DataAnalisys\PCA')
sys.path.append(r'C:\Users\monta\Desktop\Materie\Altro\Tirocinio\Python\Liver_Project_2.0\LiverProject_env\Liver_Project\DataAnalisys\SSL')

# SSA
import PointCloud_Database
import RigidRegistration
import NonRigidRegistration
# PCA
import PrincipalComponentAnalysis  
#SSL
import Outliers

# main
def main():
    Liver_PointClouds = PointCloud_Database.PointCloud()
    PointCloud_Database.Plot_1(Liver_PointClouds)
    Liver_Reshape = PointCloud_Database.MatrixReshape(Liver_PointClouds)
    PointCloud_Database.Plot_2(Liver_Reshape)
    Liver_Templates, Liver_Targets = RigidRegistration.RigidSuperimposition(Liver_Reshape)
    RigidRegistration.Plot_3(Liver_Templates, Liver_Targets)
    Liver_Templates_t, Liver_Targets_t = RigidRegistration.Centroid(Liver_Templates, Liver_Targets)
    RigidRegistration.Plot_4(Liver_Templates_t, Liver_Targets_t)
    Liver_Templates_ICP, Liver_Targets_ICP = RigidRegistration.IterativeClosestPoint(Liver_Templates_t, Liver_Targets_t)
    RigidRegistration.Plot_5(Liver_Templates_ICP, Liver_Targets_ICP)
    Liver_Templates, Liver_Targets = NonRigidRegistration.ThinPlateSplineParametrization(Liver_Templates_ICP, Liver_Targets_ICP)
    NonRigidRegistration.Plot_6(Liver_Templates, Liver_Targets)
    Shape_Parameters, Modes  = PrincipalComponentAnalysis.PrincipalComponentAnalysis(Liver_Templates)
    #PrincipalComponentAnalysis.Plot_7(Mean_Shape, Liver_Parametrization)
    Filtered_Livers = Outliers.RemoveOutliers(Shape_Parameters, Liver_Reshape[:-1])
    Outliers.Plot_8(Filtered_Livers)

if __name__ == "__main__": 
    main()