import pandas as pd
import os

# Ottiene la directory di esecuzione dello script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Definisce la cartella 'output' come directory 
output_dir = os.path.join(base_dir, "output")
os.makedirs(output_dir, exist_ok=True)  # Crea la cartella se non esiste

# Definisce i percorsi dei file di input e output dentro la cartella 'output'
dataset_input = os.path.join(output_dir, "ordered_dataset.csv")
ordered_hpo_complete = os.path.join(output_dir, "completehpohierarchy.csv")
dataset_output = os.path.join(output_dir, "ordered_dataset_withparents.csv")

# Caricare i file
# Dataset principale
df = pd.read_csv(dataset_input)
# Gerarchia HPO
df_hpo = pd.read_csv(ordered_hpo_complete, index_col=0, dtype=str)

# Funzione per trovare i codici padri
def get_parent_codes(hpo_codes):
    codes = hpo_codes.split(',')  # Separiamo i codici HPO
    parent_codes = set()
    
    for code in codes:
        if code in df_hpo.index:
            parents = df_hpo.loc[code].dropna().tolist()  # Prendiamo i codici padre
            parent_codes.update(parents)
    
    return ','.join(map(str, parent_codes))

# Aggiungere la nuova colonna
col_name = df.columns[0]  # Prima colonna del dataset

df.insert(1, 'Parent_HPO_Codes', df[col_name].astype(str).apply(get_parent_codes))

# Salvare il nuovo file
df.to_csv(dataset_output, index=False)

print("Dataset File is Updated!")
