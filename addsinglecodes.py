import os
import pandas as pd

def process_csv(input_file, output_file):
    # Carica il file CSV senza usare la prima riga come intestazione
    df = pd.read_csv(input_file, dtype=str, header=None)
    
    # Trova tutti i codici unici nel file (escludendo NaN)
    unique_codes = set()
    for col in df.columns:
        unique_codes.update(df[col].dropna().unique())
    
    # Converti l'insieme in lista ordinata
    unique_codes = sorted(unique_codes)
    
    # Crea un nuovo DataFrame con una sola colonna per i codici, senza intestazione
    codes_df = pd.DataFrame(unique_codes)
    
    # Crea il DataFrame finale: prima i codici unici, poi i dati originali
    final_df = pd.concat([codes_df, df], ignore_index=True, axis=0)
    
    # Salva il risultato in un nuovo CSV senza indice e senza intestazione
    final_df.to_csv(output_file, index=False, header=False)

# Ottieni il percorso dello script
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "output")
os.makedirs(output_dir, exist_ok=True)

# Percorsi dei file
input_file = os.path.join(output_dir, "formatted_codes.csv")
final_file = os.path.join(output_dir, "formatted_codes_singlecodes.csv")

# Esegui il processo
process_csv(input_file, final_file)
