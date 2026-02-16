import open3d as o3d 
import numpy as np
from scipy.spatial import cKDTree

#Rigid Registration 1° step: Translation for center of gravity  
def RigidSuperimposition(arr_point_clouds_reshape):
    
    def closest_point(A, B):
        tree_B = cKDTree(B)
        # Find nearest neighbors for each point in the source cloud
        u_norm, i = tree_B.query(A)
        closest_points = B[i]
        return closest_points


    def rigid_transform_3D(A, B):
        # Center the point clouds
        centroid_A = np.mean(A, axis=0)
        centroid_B = np.mean(B, axis=0)
        A_centered = A - centroid_A
        B_centered = B - centroid_B
        # Use the singular value decomposition (SVD) to find the rotation matrix R
        H = np.dot(A_centered.T, B_centered)
        U, S, Vt = np.linalg.svd(H)
        R = np.dot(Vt.T, U.T)
        # Ensure a proper rotation matrix with determinant +1 (no reflection)
        if np.linalg.det(R) < 0:
            Vt[2, :] *= -1
            R = np.dot(Vt.T, U.T)
        # Calculate the translation vector t
        t = centroid_B - np.dot(R, centroid_A)
        return R, t

    def apply_rigid_transform(A, R, t):
        A_transformed = np.dot(A, R.T) + t
        return A_transformed
    
    templates_trasform = []
    targets = []
    template = arr_point_clouds_reshape[-1]
    template = template[::5]
    arr_point_clouds_reshape.pop(-1)
    for target in arr_point_clouds_reshape:
        target = target[::5]
        targets.append(target)
        #compute closest points
        closest_points = closest_point(template, target)
        # Perform rigid superimposition
        R, t = rigid_transform_3D(template, closest_points)
        # Apply the transformation to point cloud A
        template_t = apply_rigid_transform(template, R, t)
        templates_trasform.append(template_t)
    return templates_trasform, targets

def Plot_3(templates_trasform, targets):
    for template, target in zip(templates_trasform, targets):
        pc_template = o3d.geometry.PointCloud()
        pc_template.points = o3d.utility.Vector3dVector(template)
        pc_target = o3d.geometry.PointCloud()
        pc_target.points = o3d.utility.Vector3dVector(target)
        o3d.visualization.draw_geometries([pc_template, pc_target])

def Centroid(templates_trasform, targets):
    templates_t = []
    targets_t = []
    for template, target in zip(templates_trasform, targets):
            template_c = np.mean(template, axis = 0)
            template_t = template - template_c
            target_c = np.mean(target, axis = 0)
            target_t = target - target_c
            templates_t.append(template_t)
            targets_t.append(target_t)
            # pc_target = o3d.geometry.PointCloud()
            # pc_target.points = o3d.utility.Vector3dVector(target_t)
            # pc_template = o3d.geometry.PointCloud()
            # pc_template.points = o3d.utility.Vector3dVector(template_t)
            # o3d.visualization.draw_geometries([pc_template, pc_target])
    return templates_t, targets_t

def Plot_4(templates_t, targets_t):
    for template, target in zip(templates_t, targets_t):
        pc_template = o3d.geometry.PointCloud()
        pc_template.points = o3d.utility.Vector3dVector(template)
        pc_target = o3d.geometry.PointCloud()
        pc_target.points = o3d.utility.Vector3dVector(target)
        o3d.visualization.draw_geometries([pc_template, pc_target])

#Rigid Registration 2° step: ICP
def IterativeClosestPoint(templates_t, targets_t):
    pc_targets = []
    pc_templates = []
    templates_icp = []
    for template, target in zip(templates_t, targets_t):
        pc_target = o3d.geometry.PointCloud()
        pc_target.points = o3d.utility.Vector3dVector(target)
        pc_template = o3d.geometry.PointCloud()
        pc_template.points = o3d.utility.Vector3dVector(template)
        pc_targets.append(pc_target)
        pc_templates.append(pc_template)
    for pc_target, pc_template in zip(pc_targets, pc_templates):
        icp_result = o3d.pipelines.registration.registration_icp(
        pc_template, pc_target, max_correspondence_distance=0.05,
        estimation_method=o3d.pipelines.registration.TransformationEstimationPointToPoint(),
        criteria=o3d.pipelines.registration.ICPConvergenceCriteria(relative_fitness=1e-6, relative_rmse=1e-6, max_iteration=50)
        )
        pc_template_t = pc_template.transform(icp_result.transformation)
        template_icp = np.asarray(pc_template_t.points)
        templates_icp.append(template_icp)
        targets_icp = targets_t
        #o3d.visualization.draw_geometries([pc_target, pc_template_t])
    return templates_icp, targets_icp

def Plot_5(templates_icp, targets_icp):
    for template, target in zip(templates_icp, targets_icp):
        pc_template = o3d.geometry.PointCloud()
        pc_template.points = o3d.utility.Vector3dVector(template)
        pc_target = o3d.geometry.PointCloud()
        pc_target.points = o3d.utility.Vector3dVector(target)
        o3d.visualization.draw_geometries([pc_template, pc_target])
