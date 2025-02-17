import csv

def calcola_depth(codice, dati):
    """Calcola la profondità del codice"""
    depth = 0
    while True:
        # Verifica se il codice ha delle sovraclassi
        sovraclassi = [riga[1] for riga in dati if riga[0] == codice]
        if sovraclassi:
            codice = sovraclassi[0]  # Passa al primo sovraclassificato
            depth += 1
        else:
            break
    return depth

def riorganizza_codici(input_file, output_file):
    # Carica il file CSV
    with open(input_file, mode='r') as file:
        reader = csv.reader(file)
        dati = list(reader)
    
    # Calcola la profondità per ogni codice
    depth_dict = {}
    for riga in dati:
        codice = riga[0]
        depth = calcola_depth(codice, dati)
        if depth not in depth_dict:
            depth_dict[depth] = []
        depth_dict[depth].append(codice)
    
    # Trova la profondità massima per determinare il numero di righe
    max_depth = max(depth_dict.keys())

    # Crea la struttura per il nuovo CSV
    rows = []
    for depth in range(max_depth + 1):
        row = [f"Depth_{depth}"]  # La prima colonna è "Depth_x"
        # Aggiungi i codici per ogni livello di profondità
        codici = depth_dict.get(depth, [])
        row.extend(codici)
        
        # Completa la riga con vuoti 
        while len(row) <= max(len(depth_dict[d]) for d in range(max_depth + 1)):
            row.append("")  # Aggiungi una cella vuota se mancano codici a quella profondità

        rows.append(row)

    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Scrivi l'intestazione
        writer.writerow(["Depth", *["HPO_ID_" + str(i) for i in range(1, max(len(depth_dict[d]) for d in range(max_depth + 1)) + 1)]]) 
        writer.writerows(rows)

# Percorsi dei file CSV
input_file = r"C:\Users\Amorl\Desktop\progetto\ordered_hpo_complete.csv"  # File di input
output_file = r"C:\Users\Amorl\Desktop\progetto\true_depth.csv"  # File di output

# Esegui la funzione
riorganizza_codici(input_file, output_file)
