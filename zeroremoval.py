import pandas as pd
import re
import os

def clean_hpo_code(hpo_code):
    """ Rimuove il prefisso 'HP:', i due punti (:) e gli zeri iniziali dai codici HPO. """
    if pd.isna(hpo_code):  # Controlla se il valore è NaN
        return None
    cleaned_code = re.sub(r"^HP:0*", "", str(hpo_code))  # Rimuove 'HP:' e tutti gli 0 iniziali
    return cleaned_code

def read_and_clean_csv(input_path, output_path):
    """ Legge un CSV, pulisce i codici HPO e salva il risultato in un nuovo file. """
    try:
        df = pd.read_csv(input_path, dtype=str)  # Legge tutto come stringa
        df = df.applymap(clean_hpo_code)  # Applica la pulizia a ogni valore della tabella
        df.to_csv(output_path, index=False)  # Salva il file senza gli indici
        print(f"File pulito salvato in: {output_path}")
    except Exception as e:
        print(f"Errore durante la lettura o scrittura del file {input_path}: {e}")

# Ottieni la directory di esecuzione dello script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Definisce la cartella 'output' come directory di lavoro
output_dir = os.path.join(script_dir, "output")
os.makedirs(output_dir, exist_ok=True)  # Crea la cartella output se non esiste

# Percorsi dei file nella cartella output
ordered_hpo_input = os.path.join(output_dir, "completehpohierarchy_from118.csv")
ordered_hpo_output = os.path.join(output_dir, "completehpohierarchy_from118_cleaned.csv")

# Esegui la pulizia per entrambi i file
read_and_clean_csv(ordered_hpo_input, ordered_hpo_output)
