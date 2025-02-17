import pandas as pd

# Carica il file CSV
df = pd.read_csv(r"C:\Users\Amorl\Desktop\progetto\outputhie.csv")

# Dizionario per tenere traccia dei totali per ogni codice
code_counts = {}

# Itera su ogni riga del DataFrame
for index, row in df.iterrows():
    count = row['Count']  # Estrai il count
    # Itera sui codici 
    for col in row.index[1:]:
        code = row[col]
        if pd.notna(code):  # Assicurati che il codice non sia NaN
            if code not in code_counts:
                code_counts[code] = 0
            code_counts[code] += count

# Creazione di un DataFrame con i codici e i loro count totali
result_df = pd.DataFrame(list(code_counts.items()), columns=['HPO_ID', 'Total_Count'])

# Salva il risultato in un nuovo file CSV
result_df.to_csv(r"C:\Users\Amorl\Desktop\progetto\total_counts.csv", index=False)

print("File creato con successo.")