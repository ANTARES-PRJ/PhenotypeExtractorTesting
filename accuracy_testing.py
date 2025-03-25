import csv
import os
import time
from collections import defaultdict



def load_hierarchy(csv_file):
    """Carica la gerarchia degli HPO code da un file CSV, dove la prima colonna contiene il codice originale e le colonne a destra contengono i codici padri diretti."""
    hierarchy = defaultdict(set)
    
    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        
        for row in reader:
            if row:
                original_code = row[0].strip().strip("'")  # Codice originale nella prima colonna
                # I codici a destra (dalla seconda colonna in poi) sono i codici padri o figli o alternativi
                parents = [code.strip().strip("'") for code in row[1:] if code.strip()]
                
                # Aggiungi i codici padri (sovraclassi) per il codice originale
                for parent in parents:
                    hierarchy[original_code].add(parent)
    
    return hierarchy

def extract_hpo_groups(row_string):
    """Estrae i gruppi di codici HPO dalle parentesi quadre."""
    row_string = row_string.replace("'", "")  # Rimuove eventuali virgolette
    parts = row_string.split('[')
    
    if len(parts) < 3:
        print(f"Errore nel formato della riga: {row_string}")  # Debug
        return [], []  
    
    first_group_raw = parts[1].split(']')[0]
    second_group_raw = parts[2].split(']')[0]

    first_group = [code.strip() for code in first_group_raw.split() if code.startswith('HP:')]
    second_group = [code.strip() for code in second_group_raw.split() if code.startswith('HP:')]
    
    return first_group, second_group

def expand_codes(codes, hierarchy):
    """Espande i codici con le loro sovraclassi e sottoclassi."""
    expanded = set(codes)
    for code in codes:
        if code in hierarchy:
            expanded.update(hierarchy[code])
    return expanded

def calculate_accuracy(expanded_codes, oracle_codes):
    """Calcola la percentuale di match tra expanded_codes e oracle_codes."""
    if not oracle_codes:
        return 0.0
    matches = set(expanded_codes) & set(oracle_codes)
    accuracy = (len(matches) / len(oracle_codes)) * 100
    return accuracy  

def process_csv(input_file, hierarchy_file, output_file):
    """Elabora 1 file CSV alla volta  e salva il risultato finale."""
    print(f"\n working on: {hierarchy_file}")
    hierarchy = load_hierarchy(hierarchy_file)
    
    final_results = []
    accuracy_list = []  
    
    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)  # Salta l'intestazione
        
        for row in reader:
            row_string = ' '.join(row[:-1])  
            elapsed_time = row[-1]  # L'elapsed_time si trova nell'ultima posizione
            
            first_group, second_group = extract_hpo_groups(row_string)
            expanded_first_group = expand_codes(first_group, hierarchy)
            accuracy = calculate_accuracy(expanded_first_group, second_group)
            
            accuracy_list.append(accuracy)
            
            final_results.append([
                ', '.join(first_group),  
                ', '.join(second_group),  
                ', '.join(expanded_first_group),  
                f"{round(accuracy, 2)}%",  
                elapsed_time  
            ])
    
    average_accuracy = sum(accuracy_list) / len(accuracy_list) if accuracy_list else 0
    average_accuracy_str = f"{round(average_accuracy, 2)}%"  
    
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["Average Accuracy", average_accuracy_str])
        writer.writerow(["FirstGroup", "Oracle", "ExpandedFirstGroup", "Accuracy", "ElapsedTime"])
        writer.writerows(final_results)
    
    print(f" File salvato: {output_file}")

# Imposta il percorso dei file
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "output")
os.makedirs(output_dir, exist_ok=True)

input_file = os.path.join(script_dir, "output", "summary.csv")

# Due file di gerarchia da processare
hierarchy_files = [
    ("hieandsub.csv", "final_accuracy_subandparent.csv"),
    ("hieandsub_alt.csv", "final_accuracywithallcodes.csv"),
    ("completehpohierarchy_from118.csv", "final_accuracy_only_parents.csv")
    
]

# Esegui il processo per entrambi i file di gerarchia
for hierarchy_filename, output_filename in hierarchy_files:
    hierarchy_file = os.path.join(output_dir, hierarchy_filename)
    final_output_file = os.path.join(output_dir, output_filename)
    process_csv(input_file, hierarchy_file, final_output_file)
