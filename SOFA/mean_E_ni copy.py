import pandas as pd
import numpy as np
import meshio

def fromCSVtoK(path): 
    # Leggere il file CSV in un DataFrame pandas
    df = pd.read_csv(path, header=None)
    
    # Convertire il DataFrame pandas in un array NumPy
    K = df.to_numpy()
    
    return K

def ExtractInfo(path):
    # Legge il file di mesh dal percorso specificato usando la libreria meshio.
    mesh = meshio.read(path)

    # Estrae i punti/nodi della mesh caricata. 
    # 'mesh.points' restituisce un array di coordinate 3D (x, y, z) per ciascun nodo.
    nodes = mesh.points  

    # Inizializza una lista vuota per memorizzare gli elementi tetraedrici.
    tetra_elements = []

    # Itera attraverso i blocchi di celle nel file di mesh.
    # Ogni 'cell_block' rappresenta un blocco di elementi (es. triangoli, tetraedri).
    for cell_block in mesh.cells:
        # Verifica se il tipo di cella è "tetra" (tetraedro lineare) o "tetra10" (tetraedro quadratico con 10 nodi).
        if cell_block.type in ["tetra", "tetra10"]:
            # Aggiunge gli elementi del blocco corrente alla lista 'tetra_elements'.
            # 'cell_block.data' contiene gli indici dei nodi che formano ciascun elemento.
            tetra_elements.extend(cell_block.data)          

    return nodes, tetra_elements

def Common_Points(tetra, tetras):
    # Inizializza i contatori per ogni nodo del tetraedro 'tetra'.
    # I contatori rappresentano il numero di volte in cui ciascun nodo appare negli altri tetraedri della lista 'tetras'.
    counter_A = 0
    counter_B = 0
    counter_C = 0
    counter_D = 0
    
    # Itera su ogni tetraedro 't' nella lista di tetraedri 'tetras'.
    for t in tetras:
        # Controlla se il primo nodo (tetra[0]) del tetraedro 'tetra' è presente nel tetraedro 't'.
        if tetra[0] in t:
            counter_A += 1  # Incrementa il contatore del nodo A se trovato.

        # Controlla se il secondo nodo (tetra[1]) del tetraedro 'tetra' è presente nel tetraedro 't'.
        if tetra[1] in t:
            counter_B += 1  # Incrementa il contatore del nodo B se trovato.

        # Controlla se il terzo nodo (tetra[2]) del tetraedro 'tetra' è presente nel tetraedro 't'.
        if tetra[2] in t:
            counter_C += 1  # Incrementa il contatore del nodo C se trovato.

        # Controlla se il quarto nodo (tetra[3]) del tetraedro 'tetra' è presente nel tetraedro 't'.
        if tetra[3] in t:
            counter_D += 1  # Incrementa il contatore del nodo D se trovato.
            
    return counter_A, counter_B, counter_C, counter_D

def ExtractKe(K, tetra, tetras):
    # Faccio una copia della matrice globale K così che le modifiche fatte su esso non veranno salvate
    Kcopy = K.copy()
    
    # Chiama la funzione Common_Points per ottenere il numero di volte che ciascun nodo del tetraedro 'tetra' appare in altri tetraedri nella lista 'tetras'.
    counter_A, counter_B, counter_C, counter_D = Common_Points(tetra, tetras)

    # Inizializza una lista vuota per memorizzare gli indici dei gradi di libertà (DoFs) dei nodi del tetraedro.
    index = []
    print(tetra)
    
    # Itera su ciascun nodo 'i' del tetraedro 'tetra'.
    for i in tetra: 
        # Calcola l'indice dei gradi di libertà (DoFs) corrispondenti a ciascun nodo 'i' nelle direzioni x, y e z.
        dof_x = 3 * i       # Grado di libertà nella direzione x.
        index.append(dof_x) # Aggiunge il DoF x all'indice.
        dof_y = 3 * i + 1   # Grado di libertà nella direzione y.
        index.append(dof_y) # Aggiunge il DoF y all'indice.
        dof_z = 3 * i + 2   # Grado di libertà nella direzione z.
        index.append(dof_z) # Aggiunge il DoF z all'indice.
            
        # Modifica la sotto-matrice della matrice globale 'K' corrispondente agli indici del nodo corrente.
        # Divide la sotto-matrice di 'K' per il contatore corrispondente a ciascun nodo per normalizzare i contributi del nodo.
        if i == tetra[0]:
            Kcopy[index, index] /= counter_A
        elif i == tetra[1]:
            Kcopy[index, index] /= counter_B
        elif i == tetra[2]:
            Kcopy[index, index] /= counter_C
        elif i == tetra[3]:
            Kcopy[index, index] /= counter_D
        
    # Estrae la sotto-matrice locale 'Ke' dalla matrice globale 'K' utilizzando gli indici calcolati.
    Ke = Kcopy[np.ix_(index, index)]
    
    return Ke
    
def pseudo_determinant_for_coef(M):
    # Funzione per calcolare una sorta di determinante "pseudo" che viene usato per popolare la matrice J.
    # Calcola il determinante basato su un sottoinsieme specifico degli elementi di M.
    return (M[0, 1] * M[1, 2] - M[1, 1] * M[0, 2] -
            M[0, 0] * M[1, 2] + M[1, 0] * M[0, 2] +
            M[0, 0] * M[1, 1] - M[1, 0] * M[0, 1])
    
def compute_strain_displacement(a, b, c, d):
    # Inizializza la matrice J come una matrice 12x6 di zeri.
    J = np.zeros((12, 6))

    # Inizializza la matrice M come una matrice 2x3 di zeri.
    # Questa matrice verrà utilizzata per calcolare valori specifici necessari per la matrice J.
    M = np.zeros((2, 3))

    # Popola la matrice M con valori derivati dalle coordinate dei nodi b, c e d.
    # Viene utilizzato per calcolare determinanti parziali per i componenti della matrice J.
    M[0, 0] = b[1]
    M[0, 1] = c[1]
    M[0, 2] = d[1]
    M[1, 0] = b[2]
    M[1, 1] = c[2]
    M[1, 2] = d[2]
    # Assegna i valori calcolati alla matrice J.
    J[0, 0] = J[1, 3] = J[2, 5] = -pseudo_determinant_for_coef(M)

    # Modifica ulteriormente M e continua a popolare J.
    M[0, 0] = b[0]
    M[0, 1] = c[0]
    M[0, 2] = d[0]
    J[0, 3] = J[1, 1] = J[2, 4] = pseudo_determinant_for_coef(M)

    M[1, 0] = b[1]
    M[1, 1] = c[1]
    M[1, 2] = d[1]
    J[0, 5] = J[1, 4] = J[2, 2] = -pseudo_determinant_for_coef(M)

    # Continua a riempire la matrice J usando valori modificati di M per ogni serie di operazioni.
    M[0, 0] = c[1]
    M[0, 1] = d[1]
    M[0, 2] = a[1]
    M[1, 0] = c[2]
    M[1, 1] = d[2]
    M[1, 2] = a[2]
    J[3, 0] = J[4, 3] = J[5, 5] = pseudo_determinant_for_coef(M)

    M[0, 0] = c[0]
    M[0, 1] = d[0]
    M[0, 2] = a[0]
    J[3, 3] = J[4, 1] = J[5, 4] = -pseudo_determinant_for_coef(M)

    M[1, 0] = c[1]
    M[1, 1] = d[1]
    M[1, 2] = a[1]
    J[3, 5] = J[4, 4] = J[5, 2] = pseudo_determinant_for_coef(M)

    M[0, 0] = d[1]
    M[0, 1] = a[1]
    M[0, 2] = b[1]
    M[1, 0] = d[2]
    M[1, 1] = a[2]
    M[1, 2] = b[2]
    J[6, 0] = J[7, 3] = J[8, 5] = -pseudo_determinant_for_coef(M)

    M[0, 0] = d[0]
    M[0, 1] = a[0]
    M[0, 2] = b[0]
    J[6, 3] = J[7, 1] = J[8, 4] = pseudo_determinant_for_coef(M)

    M[1, 0] = d[1]
    M[1, 1] = a[1]
    M[1, 2] = b[1]
    J[6, 5] = J[7, 4] = J[8, 2] = -pseudo_determinant_for_coef(M)

    M[0, 0] = a[1]
    M[0, 1] = b[1]
    M[0, 2] = c[1]
    M[1, 0] = a[2]
    M[1, 1] = b[2]
    M[1, 2] = c[2]
    J[9, 0] = J[10, 3] = J[11, 5] = pseudo_determinant_for_coef(M)

    M[0, 0] = a[0]
    M[0, 1] = b[0]
    M[0, 2] = c[0]
    J[9, 3] = J[10, 1] = J[11, 4] = -pseudo_determinant_for_coef(M)

    M[1, 0] = a[1]
    M[1, 1] = b[1]
    M[1, 2] = c[1]
    J[9, 5] = J[10, 4] = J[11, 2] = pseudo_determinant_for_coef(M)

    # Assegna 0 a tutte le altre componenti di J in base agli indici forniti in 'zero_indices'.
    zero_indices = [
        (0, 1), (0, 2), (0, 4), (1, 0), (1, 2), (1, 5), (2, 0), (2, 1), (2, 3),
        (3, 1), (3, 2), (3, 4), (4, 0), (4, 2), (4, 5), (5, 0), (5, 1), (5, 3),
        (6, 1), (6, 2), (6, 4), (7, 0), (7, 2), (7, 5), (8, 0), (8, 1), (8, 3),
        (9, 1), (9, 2), (9, 4), (10, 0), (10, 2), (10, 5), (11, 0), (11, 1), (11, 3)
    ]
    # Imposta gli elementi corrispondenti agli indici specificati a zero.
    for i, j in zero_indices:
        J[i, j] = 0
        
    return J


def Compute_E_nu(Ke, J, tetra, points):
    # Calcola l'inversa generalizzata (pseudo-inversa) della matrice J
    Jinv = np.linalg.pinv(J)
    
    # Moltiplica l'inversa di J con la matrice Ke
    JinvKe = np.dot(Jinv, Ke)
    
    # Calcola la matrice C moltiplicando JinvKe con la trasposta di Jinv
    C = np.dot(JinvKe, Jinv.T)
    
    # Calcola i vettori A, B, D per determinare il volume del tetraedro
    A = points[tetra[1]] - points[tetra[0]]
    B = points[tetra[2]] - points[tetra[0]]
    D = points[tetra[3]] - points[tetra[0]]

    # Calcola il prodotto vettoriale tra A e B
    AB = np.cross(A, B)
    
    # Calcola sei volte il volume del tetraedro usando il prodotto scalare tra AB e D
    volume6 = np.abs(np.dot(AB, D))
    
    # Calcola 36 volte il volume del tetraedro (come da metodo ThetraedronCorotationalFEMForceField)
    volume36 = volume6 * 6

    # Scala la matrice C in base al volume calcolato
    C *= volume36
    
    # Estrae i valori lambda e mu (costanti di Lamè) dalla matrice C
    lambda_ = C[1, 2]
    mu = C[4, 4]

    # Calcola il modulo di Young (E) e il coefficiente di Poisson (nu)
    E = mu * (3 * lambda_ + 2 * mu) / (lambda_ + mu)
    nu = lambda_ / (2 * (lambda_ + mu))

    return E, nu

def Mean_E_nu(tetras, points, K):
     
    tetras_rid = [tetra for tetra in tetras if all(3*n + 2 <= K.shape[0] for n in tetra)]  
     
    # Inizializza i contatori per il calcolo della media
    counter_E = 0
    counter_nu = 0 
    
    # Itera su ogni tetraedro per calcolare E e nu
    for tetra in tetras_rid:
        # Estrae la matrice Ke per il tetraedro corrente
        Ke = ExtractKe(K, tetra, tetras_rid)
        
        # Calcola la matrice di deformazione per il tetraedro corrente
        J = compute_strain_displacement(points[tetra[0]], points[tetra[1]], points[tetra[2]], points[tetra[3]])
        
        # Calcola E (Modulo di Young) e nu (coefficiente di Poisson) per il tetraedro corrente
        E, nu = Compute_E_nu(Ke, J, tetra, points)
        
        # Aggiorna i contatori con i valori calcolati
        counter_E += E
        counter_nu += nu
        
    # Calcola le medie di E e nu
    E_mean = counter_E / len(tetras_rid)
    nu_mean = counter_nu / len(tetras_rid)

    return E_mean, nu_mean
 


def main():
    K = fromCSVtoK(r'C:\Users\monta\Desktop\Materie\Altro\Tirocinio\SOFA\stiffness_matrix\mean_stiffness.csv')
    nodes, tetra = ExtractInfo(r'C:\Users\monta\Desktop\Materie\Altro\Tirocinio\Liver_Database\3D_Slicer\liver_test\Liver_Test_1\Liver_Test_1.msh')
    E, nu = Mean_E_nu(tetra, nodes, K)
    print(E, nu)
    
main()

