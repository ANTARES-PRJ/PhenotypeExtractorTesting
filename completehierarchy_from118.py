import pandas as pd
import re
import os

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
            all_superclasses.append(sc)
            if sc == "HP:0000118":  # Nuova radice dell'albero
                break
            all_superclasses.extend(get_all_superclasses(sc, seen))

        return all_superclasses

    return {hpo: get_all_superclasses(hpo) for hpo in hpo_hierarchy}

def save_to_csv(hpo_hierarchy, output_csv):
    sorted_hpos = sorted(hpo_hierarchy.keys(), key=lambda x: int(x.split(":")[1]))
    data = []
    
    max_columns = max(len(superclasses) for superclasses in hpo_hierarchy.values())

    for hpo in sorted_hpos:
        row = [hpo] + hpo_hierarchy[hpo]

        while len(row) < max_columns + 1:
            row.append('')

        if "HP:0000118" in row:
            row = row[:row.index("HP:0000118") + 1]

        data.append(row)

    columns = ["HPO_Code"] + [f"Superclass_{i}" for i in range(1, max_columns + 1)]
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"File CSV salvato correttamente in: {output_csv}")

# Ottieni il percorso della cartella in cui si trova lo script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Percorsi dei file nella cartella output
obo_file = os.path.join(script_dir, "output", "hp.obo")  # File di input
output_csv = os.path.join(script_dir, "output", "completehpohierarchy_from118.csv")  # File di output

# Esegui il processo
hpo_hierarchy = parse_obo(obo_file)
resolved_hierarchy = resolve_superclasses(hpo_hierarchy)
save_to_csv(resolved_hierarchy, output_csv)
