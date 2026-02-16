from sklearn.neighbors import NearestNeighbors
import numpy as np
import open3d as o3d
def RemoveOutliers(shape_parameters, livers):
    k_neighbors = 20
    nbrs = NearestNeighbors(n_neighbors=k_neighbors).fit(shape_parameters)
    distances, indices = nbrs.kneighbors(shape_parameters)
    mean_distances = np.mean(distances, axis=1)
    std = np.std(distances, axis=1)
    threshold = mean_distances + 2 * std 
    threshold = threshold.reshape(-1, 1)
    outliers = distances > threshold
    true_positions = np.where(outliers)
    idx = indices[true_positions[0], true_positions[1]]
    filtered_shape_parameters = np.delete(shape_parameters, idx, axis = 0)
    filtered_livers = np.delete(livers, idx, axis = 0)
    return filtered_livers

def Plot_8(filtered_livers):
    for liver in filtered_livers:
        pc_liver = o3d.geometry.PointCloud()
        pc_liver.points = o3d.utility.Vector3dVector(liver)
        o3d.visualization.draw_geometries([pc_liver])
    

    
