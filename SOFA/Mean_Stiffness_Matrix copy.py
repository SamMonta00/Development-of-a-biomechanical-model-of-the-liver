import os
import pandas as pd
import numpy as np

# Lista per memorizzare gli array delle matrici di rigidezza
arrays_list = []

# Percorso della cartella contenente i file CSV delle matrici di rigidezza
folder_path = r'C:\Users\monta\Desktop\Materie\Altro\Tirocinio\SOFA\stiffness_matrix'

# Leggere tutti i file CSV presenti nella cartella specificata
for file_name in os.listdir(folder_path):
    # Verificare che il file sia un CSV
    if file_name.endswith('.csv'):
        # Costruire il percorso completo del file
        file_path = os.path.join(folder_path, file_name)
        
        # Leggere il file CSV usando pandas senza intestazione (header=None)
        df = pd.read_csv(file_path, header=None)
        
        # Convertire il DataFrame in un array NumPy di tipo float64
        array = df.to_numpy(dtype=np.float64)
        
        # Aggiungere l'array alla lista degli array
        arrays_list.append(array)

# Trovare la dimensione minima tra tutte le matrici per gestire dimensioni diverse
min_dim = min(array.shape[0] for array in arrays_list)

# Lista per memorizzare le versioni "modellate" delle matrici originali
array_modellati = []

# Modellare ogni matrice con zeri per far sì che tutte abbiano la stessa dimensione
for array in arrays_list:
    # Calcolo differenza dimensionale tra la matrice n-esima e la matrice più piccola
    diff = array.shape[0] - min_dim
    if diff == 0:
       array_modellati.append(array) 
    else:
       # Eliminare le ultime diff righe e diff colonne della matrice n-esima
       del_array = array[:-diff, :-diff]
       # Aggiungere la matrice modellata alla lista
       array_modellati.append(del_array)

# Inizializzare una matrice di zeri con le stesse dimensioni delle matrici modellate
mean_matrix = np.zeros_like(array_modellati[0])

# Sommare tutte le matrici elemento per elemento
for array in array_modellati:
    mean_matrix += array

# Dividere ogni elemento della matrice per il numero totale di matrici per ottenere la matrice media
mean_matrix /= len(arrays_list)

# Salvare la matrice media risultante in un file CSV
np.savetxt('mean_stiffness.csv', mean_matrix, delimiter=',', fmt='%.2f')