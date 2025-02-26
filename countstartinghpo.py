import pandas as pd
import os
import sys
from collections import Counter

def count_hpo_ids_with_pandas(input_csv, hpo_column='HPO_IDs'):
    """Conta le occorrenze degli ID HPO in un file CSV."""
    df = pd.read_csv(input_csv)

    # Verifica che la colonna esista nel dataset
    if hpo_column not in df.columns:
        raise KeyError(f"Colonna '{hpo_column}' non trovata nel file {input_csv}")

    # Estrai la colonna HPO_IDs e rimuovi eventuali valori mancanti
    hpo_series = df[hpo_column].dropna()

    # Dividi gli ID HPO separati da virgola e appiattisci la lista
    hpo_ids = []
    for ids in hpo_series:
        hpo_ids.extend([hpo_id.strip() for hpo_id in ids.split(',')])

    # Conta le occorrenze di ogni HPO ID
    hpo_counter = Counter(hpo_ids)

    # DataFrame ordinato per occorrenze decrescenti
    hpo_counts_df = pd.DataFrame(hpo_counter.items(), columns=['HPO_IDs', 'Count'])
    hpo_counts_df = hpo_counts_df.sort_values(by='Count', ascending=False)

    return hpo_counts_df

def save_hpo_counts(output_csv, hpo_counts_df):
    """Salva il conteggio degli HPO IDs in un file CSV."""
    hpo_counts_df.to_csv(output_csv, index=False)

def main():
    # Ottieni la cartella dello script corrente
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "output")  # Cartella output

    # Assicurati che la cartella output esista
    os.makedirs(output_dir, exist_ok=True)

    # File di input e output (nella cartella output)
    input_csv = os.path.join(output_dir, "ordered_dataset.csv")
    output_csv = os.path.join(output_dir, "hpo_counts.csv")

    # Permette di specificare i percorsi da riga di comando
    if len(sys.argv) > 1:
        input_csv = sys.argv[1]  # Primo argomento: file di input
    if len(sys.argv) > 2:
        output_csv = sys.argv[2]  # Secondo argomento: file di output

    try:
        # Conta gli HPO IDs
        hpo_counts_df = count_hpo_ids_with_pandas(input_csv)

        # Salva i risultati
        save_hpo_counts(output_csv, hpo_counts_df)

        print(f"HPO counts salvati in: {output_csv}")
    except KeyError as e:
        print(f"Errore: {e}")

if __name__ == "__main__":
    main()
