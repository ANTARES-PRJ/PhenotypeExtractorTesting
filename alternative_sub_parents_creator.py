import os
import pandas as pd
import re
from collections import defaultdict

def parse_obo(obo_file):
    hpo_hierarchy = {}
    alt_ids = {}  # Dictionary for alternative codes
    subclass_mapping = defaultdict(set)
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
                subclass_mapping[superclass].add(current_hpo)

            elif line.startswith("alt_id: HP:"):
                alt_id = line.split("alt_id: ")[1]
                if current_hpo:
                    if current_hpo not in alt_ids:
                        alt_ids[current_hpo] = set()
                    alt_ids[current_hpo].add(alt_id)

        if current_hpo:
            hpo_hierarchy[current_hpo] = superclass_list

    return hpo_hierarchy, alt_ids, subclass_mapping

def get_all_subclasses(code, subclass_mapping, visited=None):
    if visited is None:
        visited = set()
    if code in visited:
        return set()
    visited.add(code)
    subclasses = subclass_mapping.get(code, set()).copy()
    for sub in subclass_mapping.get(code, set()):
        subclasses |= get_all_subclasses(sub, subclass_mapping, visited)
    return subclasses

def resolve_superclasses(hpo_hierarchy):
    def get_all_superclasses(hpo, seen=None):
        if seen is None:
            seen = set()
        if hpo in seen or hpo not in hpo_hierarchy:
            return []

        seen.add(hpo)
        all_superclasses = []
        for sc in hpo_hierarchy[hpo]:
            if sc == "HP:0000001"or sc == "HP:0000118":
                continue  # Ignore root and phenotypic abnormality
            all_superclasses.append(sc)
            all_superclasses.extend(get_all_superclasses(sc, seen))

        return all_superclasses

    return {hpo: get_all_superclasses(hpo) for hpo in hpo_hierarchy}

def save_to_csv(hpo_hierarchy, alt_ids, subclass_mapping, output_csv, include_alt_ids=False):
    data = []
    for hpo in hpo_hierarchy:
        if hpo == "HP:0000001"or hpo == "HP:0000118":
            continue  # Exclude HP:0000001 from CSV
        
        row = [hpo] + hpo_hierarchy[hpo]
        row += sorted(get_all_subclasses(hpo, subclass_mapping))
        if include_alt_ids:
            row += list(alt_ids.get(hpo, set()))
        
        data.append(row)

    df = pd.DataFrame(data)
    df.to_csv(output_csv, index=False, header=False, encoding="utf-8")
    print(f"File CSV saved correctly at: {output_csv}")

script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "utils")
os.makedirs(output_dir, exist_ok=True)

obo_file = os.path.join(output_dir, "hp.obo")

# Define the output files
output_csv_with_alt = os.path.join(output_dir, "hieandsub_alt.csv")
output_csv_without_alt = os.path.join(output_dir, "hieandsub.csv")

hpo_hierarchy, alt_ids, subclass_mapping = parse_obo(obo_file)
resolved_hierarchy = resolve_superclasses(hpo_hierarchy)

# Save the CSV with alternative IDs
save_to_csv(resolved_hierarchy, alt_ids, subclass_mapping, output_csv_with_alt, include_alt_ids=True)

# Save the CSV without alternative IDs
save_to_csv(resolved_hierarchy, alt_ids, subclass_mapping, output_csv_without_alt, include_alt_ids=False)
