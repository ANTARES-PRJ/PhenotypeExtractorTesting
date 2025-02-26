import os
import pandas as pd
import csv

def calcola_depth_per_riga(riga, codice_riferimento="HP:0000001"):
    """Calcola la profondità come distanza in celle tra il codice di riferimento e il codice nella prima colonna."""
    if codice_riferimento in riga.values:
        distanza = riga[riga == codice_riferimento].index[0]  # Trova la prima colonna con HP:0000001
        return riga.index.get_loc(distanza)  # Converte l'indice in un numero
    return None

def riorganizza_codici(input_file, output_file, codice_riferimento="HP:0000001"):
    # Carica il file CSV in un DataFrame
    df = pd.read_csv(input_file, dtype=str)
    
    # Calcola la profondità per ogni riga
    depth_dict = {}
    for _, riga in df.iterrows():
        depth = calcola_depth_per_riga(riga, codice_riferimento)
        if depth is not None:
            codice = riga.iloc[0]  # Il codice è sempre nella prima colonna
            if depth not in depth_dict:
                depth_dict[depth] = []
            depth_dict[depth].append(codice)
    
    # Trova la profondità massima per determinare il numero di righe
    max_depth = max(depth_dict.keys(), default=0)

    # Crea la struttura per il nuovo CSV
    rows = []
    for depth in range(max_depth + 1):
        row = [f"Depth_{depth}"]  # La prima colonna è "Depth_x"
        codici = depth_dict.get(depth, [])
        row.extend(codici)
        
        # Completa la riga con vuoti se ci sono meno codici rispetto agli altri livelli
        max_col = max(len(depth_dict.get(d, [])) for d in range(max_depth + 1))
        while len(row) <= max_col:
            row.append("")

        rows.append(row)

    
    # Scrive il nuovo file CSV con l'intestazione
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        max_col = max(len(depth_dict.get(d, [])) for d in range(max_depth + 1))
        writer.writerow(["Depth", *["HPO_ID_" + str(i) for i in range(1, max_col + 1)]])  # Header
        writer.writerows(rows)

# Percorsi della cartella di output
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "output")

# Assicurati che la cartella di output esista
os.makedirs(output_dir, exist_ok=True)

# Percorsi dei file CSV
input_file = os.path.join(output_dir, "completehpohierarchy.csv")  
output_file = os.path.join(output_dir, "true_depth.csv")  

# Codice di riferimento
codice_riferimento = "HP:0000001"  # Codice di riferimento

# Esegui la funzione
riorganizza_codici(input_file, output_file, codice_riferimento)
