import pandas as pd
from collections import Counter

def count_hpo_ids_with_pandas(input_csv, hpo_column='HPO_IDs'):
    # Leggi il file CSV
    df = pd.read_csv(input_csv)
    # Estrai la colonna HPO_IDs e rimuovi eventuali valori mancanti
    hpo_series = df[hpo_column].dropna()
    
    # Dividi gli ID HPO separati da virgola e appiattisci la lista
    hpo_ids = []
    for ids in hpo_series:
        hpo_ids.extend([hpo_id.strip() for hpo_id in ids.split(',')])
    
    # Conta le occorrenze di ogni HPO ID
    hpo_counter = Counter(hpo_ids)
    
    # Converti il risultato in un DataFrame
    hpo_counts_df = pd.DataFrame(hpo_counter.items(), columns=['HPO_IDs', 'Count'])
    
    # Ordina per la colonna 'Count' in ordine decrescente
    hpo_counts_df = hpo_counts_df.sort_values(by='Count', ascending=False)
    
    return hpo_counts_df

def save_hpo_counts(output_csv, hpo_counts_df):
    # Salva il DataFrame in un file CSV
    hpo_counts_df.to_csv(output_csv, index=False)

# Esempio di utilizzo
input_csv = r"C:\Users\Amorl\Desktop\progetto\DatasetOrdinato.csv"  # Il file di input
output_csv = r"C:\Users\Amorl\Desktop\progetto\hpo_counts.csv" # Il file di output

try:
    # Conta gli HPO IDs
    hpo_counts_df = count_hpo_ids_with_pandas(input_csv)

    # Salva i risultati
    save_hpo_counts(output_csv, hpo_counts_df)

    print(f"HPO counts have been saved to {output_csv}")
except KeyError as e:
    print(e)
