import pandas as pd
import os

def format_code(code):
    """Formatta il codice nel formato HP:0000000 solo se necessario."""
    code = str(code).strip()
    if code in ["", "null"]:
        return None  # Rimuove i codici nulli
    
    if code.startswith("HP:") and len(code) == 10 and code[3:].isdigit():
        return code  # Il codice è già formattato correttamente
    
    if code.startswith("HP") and len(code) == 9 and code[2:].isdigit():
        return f"HP:{code[2:]}"  # Aggiunge i due punti se mancanti
    
    numeric_part = ''.join(filter(str.isdigit, code)).zfill(7)
    return f"HP:{numeric_part}" if numeric_part else None

def remove_hp_0000000(df):
    """Rimuove tutte le righe e colonne contenenti solo HP:0000000."""
    df_cleaned = df.dropna(how='all', axis=0)  # Rimuove righe con solo NaN
    df_cleaned = df_cleaned.dropna(how='all', axis=1)  # Rimuove colonne con solo NaN
    
    # Se una cella contiene 'HP:0000000', la considera come NaN
    df_cleaned = df_cleaned.map(lambda x: None if x == "HP:0000000" else x)
    df_cleaned = df_cleaned.dropna(how='all', axis=0)  # Rimuove righe con solo NaN dopo sostituzione
    df_cleaned = df_cleaned.dropna(how='all', axis=1)  # Rimuove colonne con solo NaN dopo sostituzione

    return df_cleaned

def save_formatted_codes(input_file, output_file):
    """Legge i codici dal file e li salva formattati in un nuovo file"""
    df_codici = pd.read_csv(input_file, header=None, skiprows=1)
    
    # Normalizza i codici
    df_codici = df_codici.apply(lambda col: col.map(format_code))
    
   
    df_codici = df_codici.apply(lambda row: row.dropna().reset_index(drop=True), axis=1)
    
    
    df_codici = remove_hp_0000000(df_codici)
    
    # Salva il file formattato
    df_codici.to_csv(output_file, index=False, header=False)
    print(f"File codici formattati salvato in: {output_file}")

# Ottiene la directory di esecuzione dello script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Definisce la cartella 'output' come directory di lavoro
output_dir = os.path.join(script_dir, "output")
os.makedirs(output_dir, exist_ok=True)  # Crea la cartella output se non esiste

# Percorsi dei file di input e output nella cartella 'output'
input_file = os.path.join(output_dir, "codes.csv")
output_file = os.path.join(output_dir, "formatted_codes.csv")

# Esecuzione della funzione
save_formatted_codes(input_file, output_file)
