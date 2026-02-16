# Development of a Biomechanical Model of the Liver

## Project Overview
This repository contains the methodology and implementation for creating a universal biomechanical liver model designed for pre-operative surgical simulation. The project focuses on developing an **average stiffness matrix** derived from a population-based dataset, which can be adapted to patient-specific geometries. By combining data science techniques with Finite Element Method (FEM) analysis, this model simulates realistic tissue deformation and behavior across diverse anatomical profiles.

## Key Features
* **Automated Geometry Extraction**: Processes $N$ abdominal CT scans into 3D point clouds.
* **Hybrid Alignment Pipeline**: Combines rigid (SVD/ICP) and non-rigid (iTPS) superimposition.
* **Statistical Refinement**: Uses PCA for dimensionality reduction and noise/outlier removal.
* **Biomechanical Simulation**: Calculates a mean stiffness matrix via FEM for predictive deformation testing.

---

## Methodology

### 1. Data Processing & Point Cloud Generation
The workflow begins by extracting 3D solid geometries from a database of abdominal CT scans. These solids are converted into point clouds to facilitate high-precision mathematical transformations.

### 2. Rigid & Non-Rigid Superimposition
To create a standardized "mean" model, individual liver geometries are aligned through a two-step process:
* **Rigid**: Uses **Singular Value Decomposition (SVD)** and **Iterative Closest Point (ICP)** to align "slave" livers to a master template.
* **Non-Rigid**: Employs **Iterative Thin Plate Spline (iTPS)** to adapt the liver flexibly, smoothing out artifacts and noise from the CT-to-3D conversion process.

### 3. Dimensionality Reduction (PCA)
**Principal Component Analysis** is applied to the aligned dataset to identify the primary modes of variation. This step is crucial for removing outliers and reducing the complexity of the biomechanical data without losing anatomical integrity.

### 4. FEM Analysis & Stiffness Matrix
We perform **Finite Element Method (FEM)** analysis to derive the mechanical properties of the liver. 
* **Objective**: Obtain the average stiffness matrix ($K$) across all master models.
* **Formula**: The general equilibrium equation solved is:
$$F = K \cdot u$$
where $F$ is the vector of external forces and $u$ is the displacement vector.

### 5. Validation and Testing
The resulting mean stiffness matrix is validated against a separate test dataset. We evaluate the coefficients by simulating deformations and comparing the results against real-world patient data to ensure high-fidelity pre-operative accuracy.

---

## Technical Stack
* **Data Processing**: Python, SVD, ICP, PCA
* **3D Modeling**: Point Cloud Library (Open3D)
* **Simulation**: SOFA Framework
* **Medical Imaging**: CT Scan processing (DICOM)
