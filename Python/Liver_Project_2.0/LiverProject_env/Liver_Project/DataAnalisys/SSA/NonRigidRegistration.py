import open3d as o3d
import torch
from scipy.spatial import cKDTree
from tps import ThinPlateSpline

def ThinPlateSplineParametrization(rt_templates, rt_targets): 
    #Non-Rigid Registration: TPS
    def closest_point(A, B):
        B_closest_points = []
        for a, b in zip(A, B):
           tree_b = cKDTree(a)
           # Find nearest neighbors for each point in the source cloud
           u_norm, i = tree_b.query(a)
           closest_points = b[i]
           B_closest_points.append(closest_points)
        return B_closest_points
    
    cp_targets = closest_point(rt_templates, rt_targets)
    templates_tensors = [torch.tensor(template, dtype=torch.float32) for template in rt_templates]
    targets_tensors = [torch.tensor(target, dtype=torch.float32) for target in cp_targets]
    nrr_templates = []
    nrr_targets = []
    tps = ThinPlateSpline(alpha = 0.001)
    for idx in range(len(templates_tensors)):
        tps.fit(templates_tensors[idx], targets_tensors[idx])
        output_predict = tps.transform(templates_tensors[idx])
        nrr_templates.append(output_predict)
    nrr_targets = rt_targets
    return nrr_templates, nrr_targets

def Plot_6(nrr_templates, nrr_targets):
    for template, target in zip(nrr_templates, nrr_targets):
        pc_template = o3d.geometry.PointCloud()
        pc_template.points = o3d.utility.Vector3dVector(template)
        pc_target = o3d.geometry.PointCloud()
        pc_target.points = o3d.utility.Vector3dVector(target)
        o3d.visualization.draw_geometries([pc_template])