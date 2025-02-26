import os
import pandas as pd
import re

def parse_obo(obo_file):
    hpo_hierarchy = {}
    current_hpo, superclass_list = None, []

    with open(obo_file, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line.startswith("[Term]"):
                if current_hpo:
                    hpo_hierarchy[current_hpo] = superclass_list
                current_hpo, superclass_list = None, []

            elif line.startswith("id: HP:"):
                current_hpo = line.split("id: ")[1]

            elif line.startswith("is_a: HP:"):
                superclass = re.search(r'HP:\d+', line).group(0)
                superclass_list.append(superclass)

        if current_hpo:
            hpo_hierarchy[current_hpo] = superclass_list

    return hpo_hierarchy

def resolve_superclasses(hpo_hierarchy):
    def get_all_superclasses(hpo, seen=None):
        if seen is None:
            seen = set()
        if hpo in seen or hpo not in hpo_hierarchy:
            return []

        seen.add(hpo)
        all_superclasses = []
        for sc in hpo_hierarchy[hpo]:
            if sc == "HP:0000001":
                all_superclasses.append(sc)
                break
            all_superclasses.append(sc)
            all_superclasses.extend(get_all_superclasses(sc, seen))

        return all_superclasses

    return {hpo: get_all_superclasses(hpo) for hpo in hpo_hierarchy}

def save_to_csv(hpo_hierarchy, output_csv):
    sorted_hpos = sorted(hpo_hierarchy.keys(), key=lambda x: int(x.split(":")[1]))  # Ordina numericamente
    data = []
    
    max_columns = max(len(superclasses) for superclasses in hpo_hierarchy.values())

    for hpo in sorted_hpos:
        row = [hpo] + hpo_hierarchy[hpo]

        while len(row) < max_columns + 1:
            row.append('')

        if "HP:0000001" in row:
            row = row[:row.index("HP:0000001") + 1]

        data.append(row)

    columns = ["HPO_Code"] + [f"Superclass_{i}" for i in range(1, max_columns + 1)]
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(output_csv, index=False, encoding="utf-8")
    print(f" File CSV salvato correttamente in: {output_csv}")

# Percorso della cartella output
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "output")

# Assicurati che la cartella di output esista
os.makedirs(output_dir, exist_ok=True)

# Percorsi dei file
obo_file = os.path.join(output_dir, "hp.obo")  # Il file .obo deve stare nella stessa cartella dello script
output_csv = os.path.join(output_dir, "completehpohierarchy.csv")

# Esecuzione dello script
hpo_hierarchy = parse_obo(obo_file)
resolved_hierarchy = resolve_superclasses(hpo_hierarchy)
save_to_csv(resolved_hierarchy, output_csv)
