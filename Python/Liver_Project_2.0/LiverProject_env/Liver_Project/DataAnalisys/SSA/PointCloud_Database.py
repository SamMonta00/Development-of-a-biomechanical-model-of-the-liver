import open3d as o3d 
import numpy as np
import os

#generate point cloud from stl file with open3D
def PointCloud():
    # Lista dei nomi dei file STL da caricare
    livers_path = r"C:\Users\monta\Desktop\Materie\Altro\Tirocinio\Liver_Database\3D_Slicer\liver_segmentation"
    # Crea una lista vuota per memorizzare i modelli 3D
    point_clouds = []
    arr_point_clouds = []

    for file_name in os.listdir(livers_path):
        if file_name.endswith(".stl"):
            file_path = os.path.join(livers_path, file_name)
            mesh = o3d.io.read_triangle_mesh(file_path)
            point_cloud = o3d.geometry.PointCloud()
            point_cloud.points = mesh.vertices
            point_cloud.colors = mesh.vertex_colors
            point_cloud.normals = mesh.vertex_normals
            point_clouds.append(point_cloud)
            arr_point_cloud = np.asarray(point_cloud.points)
            arr_point_clouds.append(arr_point_cloud)
    return arr_point_clouds

def Plot_1(arr_point_clouds):
    for liver in arr_point_clouds:
        pc_liver = o3d.geometry.PointCloud()
        pc_liver.points = o3d.utility.Vector3dVector(liver)
        o3d.visualization.draw_geometries([pc_liver])
    
#Reshape to obtain the same shape in both livers
def MatrixReshape(arr_point_clouds):
    arr_point_clouds_reshape = []
    for liver in arr_point_clouds:
        dif = abs(50000 - liver.shape[0])  
        remove = np.random.choice(liver.shape[0], dif, replace=False)
        liver = np.delete(liver, remove, axis=0)
        arr_point_clouds_reshape.append(liver)
    return arr_point_clouds_reshape

def Plot_2(arr_point_clouds_reshape):
    for liver in arr_point_clouds_reshape:
        pc_liver = o3d.geometry.PointCloud()
        pc_liver.points = o3d.utility.Vector3dVector(liver)
        o3d.visualization.draw_geometries([pc_liver])
    
