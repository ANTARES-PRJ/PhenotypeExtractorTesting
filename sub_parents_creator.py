import csv
from collections import defaultdict
import os
# Leggi il file CSV e costruisci il dizionario delle sovraclassi
hierarchy = {}
subclass_mapping = defaultdict(set)

script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "output")
os.makedirs(output_dir, exist_ok=True)
codici_file = os.path.join(output_dir, "completehpohierarchy_from118.csv")
output= os.path.join(output_dir, "hieandsub.csv")

with open(codici_file, newline="", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    header = next(reader)  # Salta l'intestazione
    
    for row in reader:
        codice = row[0]
        sovraclassi = [col for col in row[1:] if col]  # Rimuove valori vuoti
        hierarchy[codice] = sovraclassi

        # Costruisce il mapping inverso delle sottoclassi
        for supercode in sovraclassi:
            subclass_mapping[supercode].add(codice)

# Funzione per ottenere tutte le sottoclassi ricorsivamente
def get_all_subclasses(code, visited=None):
    if visited is None:
        visited = set()
    if code in visited:
        return set()
    visited.add(code)
    subclasses = subclass_mapping.get(code, set()).copy()
    for sub in subclass_mapping.get(code, set()):
        subclasses |= get_all_subclasses(sub, visited)
    return subclasses

# Aggiungi le sottoclassi a ogni codice
output_data = []
for code in hierarchy:
    all_subclasses = sorted(get_all_subclasses(code))  # Ordina per leggibilità
    output_data.append([code] + hierarchy[code] + all_subclasses)

# Scrivi il nuovo CSV con le sottoclassi incluse
with open(output, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    max_cols = max(len(row) for row in output_data)
    writer.writerow(["Codice"] + [f"Sovraclasse_{i}" for i in range(1, max_cols)])  # Header dinamico
    writer.writerows(output_data)



print("File hieandsub.csv creato con successo!")