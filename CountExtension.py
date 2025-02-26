import pandas as pd
import os
import sys

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

def get_hierarchy_path(hierarchy, hpo_id):
    path = [hpo_id]
    while hpo_id in hierarchy and hierarchy[hpo_id]:
        hpo_id = hierarchy[hpo_id][0]  
        path.append(hpo_id)
    return path

def generate_hierarchy_csv(hp_obo_path, hpo_counts_csv_path, output_csv_path):
    hierarchy = parse_hp_obo(hp_obo_path)
    
    df_counts = pd.read_csv(hpo_counts_csv_path)
    
    all_data = []
    for _, row in df_counts.iterrows():
        hpo_id = row['HPO_IDs']
        count = row['Count']
        path = get_hierarchy_path(hierarchy, hpo_id)
        
        row_data = {"HPO_ID": hpo_id, "Count": count}
        for i, level in enumerate(path):
            row_data[f"Level_{i+1}"] = level
        
        all_data.append(row_data)
    
    df_output = pd.DataFrame(all_data)
    df_output.to_csv(output_csv_path, index=False)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    hp_obo_path = os.path.join(output_dir, "hp.obo")
    hpo_counts_csv_path = os.path.join(output_dir, "hpo_counts.csv")
    output_csv_path = os.path.join(output_dir, "output_hierarchy.csv")
    
    if len(sys.argv) > 1:
        hp_obo_path = sys.argv[1]
    if len(sys.argv) > 2:
        hpo_counts_csv_path = sys.argv[2]
    if len(sys.argv) > 3:
        output_csv_path = sys.argv[3]
    
    try:
        generate_hierarchy_csv(hp_obo_path, hpo_counts_csv_path, output_csv_path)
        print(f"Gerarchia salvata in: {output_csv_path}")
    except KeyError as e:
        print(f"Errore: {e}")

if __name__ == "__main__":
    main()
