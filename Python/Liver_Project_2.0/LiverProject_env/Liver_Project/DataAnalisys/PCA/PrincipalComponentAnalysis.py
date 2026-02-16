import numpy as np
import open3d as o3d
from sklearn.decomposition import PCA
import csv


def PrincipalComponentAnalysis(templates):
    shape_parameters = np.empty([len(templates), 3])
    modes = np.empty([len(templates), 3, 3])
    i = 0
    mean_templates = [np.mean(template, axis = 0) for template in templates]
    templates_c = [template - mean_template for template, mean_template in zip(templates, mean_templates)]
    for template in templates_c:
       pca = PCA()
       pca.fit(template)
       cov = pca.get_covariance()
       eigenvalue, eigenvector = np.linalg.eigh(cov)
       shape_parameters[i, :] =  eigenvalue
       modes[i, :, :] = eigenvector
       i += 1
    '''
    shape_parameters_flatten = shape_parameters.flatten()
    modes = modes.reshape((len(templates) * 3, 3))
    idx = np.argsort(shape_parameters_flatten)[::-1]
    shape_parameters_idx = shape_parameters_flatten[idx]
    shape_parameters_f = shape_parameters_idx[:3]
    modes_idx = modes[idx, :]
    modes_f = modes_idx[:3, :]
    mean_shape = np.mean(templates, axis=0)
    shape_parametrization = np.matmul(mean_shape, modes_f)
    shape_parameters = shape_parameters_flatten.reshape(len(templates), 3)
    '''
    return shape_parameters, modes


def Plot_7(mean_shape, shape_parametrization):
    pc_mean = o3d.geometry.PointCloud()
    pc_mean.points = o3d.utility.Vector3dVector(mean_shape)
    o3d.visualization.draw_geometries([pc_mean])
    pc_shape = o3d.geometry.PointCloud()
    pc_shape.points = o3d.utility.Vector3dVector(shape_parametrization)
    o3d.visualization.draw_geometries([pc_shape])


def Save(shape_parameters, modes):
    with open('shape_parameters.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(shape_parameters)
    with open('modes.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(modes)

