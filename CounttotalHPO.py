import os
import pandas as pd

# Imposta la cartella di output
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

# Percorsi dei file
input_csv = os.path.join(output_dir, "output_hierarchy.csv")
output_csv = os.path.join(output_dir, "total_counts.csv")

# Carica il file CSV
df = pd.read_csv(input_csv)

# Dizionario per tenere traccia dei totali per ogni codice
code_counts = {}

# Itera su ogni riga del DataFrame
for index, row in df.iterrows():
    count = row['Count']  # Estrai il count
    # Itera sui codici 
    for col in row.index[1:]:  # Ignora la colonna 'Count'
        code = row[col]
        if pd.notna(code):  # Assicurati che il codice non sia NaN
            code_counts[code] = code_counts.get(code, 0) + count

# Creazione di un DataFrame con i codici e i loro count totali
result_df = pd.DataFrame(list(code_counts.items()), columns=['HPO_ID', 'Total_Count'])

# Salva il risultato in un nuovo file CSV
result_df.to_csv(output_csv, index=False)

print(f"File creato con successo: {output_csv}")
