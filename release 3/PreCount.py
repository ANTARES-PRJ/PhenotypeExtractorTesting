import csv

# Funzione per leggere e costruire la gerarchia dall'hp.obo
def parse_hp_obo(file_path):
    hierarchy = {}
    current_id = None

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("id: "):
                current_id = line.split(" ")[1]
                hierarchy[current_id] = []
            elif line.startswith("is_a: "):
                parent_id = line.split(" ")[1]
                hierarchy[current_id].append(parent_id)

    return hierarchy

# Funzione per calcolare ricorsivamente il percorso fino alla radice
def get_hierarchy_path(hierarchy, hpo_id):
    path = [hpo_id]
    while hpo_id in hierarchy and hierarchy[hpo_id]:
        hpo_id = hierarchy[hpo_id][0]  # Supponiamo un solo genitore per semplicità
        path.append(hpo_id)
    return path

# Funzione principale per leggere il file hpo_counts_csv e creare il nuovo CSV
def generate_hierarchy_csv(hp_obo_path, hpo_counts_csv_path, output_csv_path):
    hierarchy = parse_hp_obo(hp_obo_path)

    with open(hpo_counts_csv_path, 'r') as counts_file, open(output_csv_path, 'w', newline='') as output_file:
        reader = csv.DictReader(counts_file)
        fieldnames = ["Count", "HPO_ID"] + [f"Level_{i}" for i in range(1, 100)]  # Aggiungi la colonna 'count'
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:
            hpo_id = row['HPO_IDs']
            count = row['Count']  # Aggiungi la colonna 'count' al nuovo CSV
            path = get_hierarchy_path(hierarchy, hpo_id)
            
            # Raccogli i livelli della gerarchia
            row_data = {f"Level_{i+1}": path[i] for i in range(len(path))}
            row_data["HPO_ID"] = hpo_id
            row_data["Count"] = count  # Aggiungi 'count' prima di 'HPO_ID'

            writer.writerow(row_data)

# Esempio di utilizzo
generate_hierarchy_csv(r"C:\Users\Amorl\Desktop\progetto\hp.obo", 
                       r"C:\Users\Amorl\Desktop\progetto\hpo_counts.csv", 
                       r"C:\Users\Amorl\Desktop\progetto\outputhie.csv")

