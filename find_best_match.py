import os
import pandas as pd
import random
from collections import defaultdict

# Dizionario per tracciare la frequenza di utilizzo dei report
report_usage_counter = defaultdict(int)
used_reports = set()
assigned_reports = set()

def select_best_match(input_codes, dataset_dict):
    exact_matches = []
    partial_matches = []
    best_partial_match_size = float('inf')

    def search_match(codes_to_search, is_combined=False):
        nonlocal best_partial_match_size, exact_matches, partial_matches
        for dataset_totali in dataset_dict:
            dataset_codici, dataset_padri, dataset_row = dataset_dict[dataset_totali]
            all_codes = codes_to_search(dataset_codici, dataset_padri) if is_combined else dataset_codici
            
            if input_codes == all_codes:
                exact_matches.append((dataset_codici, dataset_padri, dataset_row.tolist()))
            elif input_codes.issubset(all_codes):
                num_additional_codes = len(all_codes) - len(input_codes)
                if num_additional_codes < best_partial_match_size:
                    best_partial_match_size = num_additional_codes
                    partial_matches = [(dataset_codici, dataset_padri, dataset_row.tolist())]
                elif num_additional_codes == best_partial_match_size:
                    partial_matches.append((dataset_codici, dataset_padri, dataset_row.tolist()))
    
    # Cerca sia corrispondenze esatte che parziali
    search_match(lambda codici, padri: codici)
    search_match(lambda codici, padri: codici.union(padri), is_combined=True)

    # Funzione per scegliere il match meno utilizzato
    def choose_least_used(match_list, exclude_assigned=True):
        if exclude_assigned:
            available_matches = [match for match in match_list if tuple(match[2]) not in assigned_reports]
        else:
            available_matches = match_list
        
        if available_matches:
            return min(available_matches, key=lambda match: report_usage_counter[tuple(match[2])])
        return None

    # Se ci sono corrispondenze esatte, scegli il meno utilizzato tra quelle esatte
    best_match = choose_least_used(exact_matches)
    if not best_match:
        best_match = choose_least_used(partial_matches)
    if not best_match:
        best_match = choose_least_used(exact_matches, exclude_assigned=False) or choose_least_used(partial_matches, exclude_assigned=False)
    
    if best_match:
        report_usage_counter[tuple(best_match[2])] += 1
        assigned_reports.add(tuple(best_match[2]))
        return best_match
    
    return None

def process_match(codici_riga, dataset_dict, hierarchy_dict):
    match_result = select_best_match(codici_riga, dataset_dict)
    if match_result:
        codici_dataset, codici_padri, riga_dataset = match_result
        codici_dataset_str = ",".join(sorted(codici_dataset))
        hierarchy_str = get_hierarchy_string(codici_dataset, hierarchy_dict)
        return [",".join(sorted(codici_riga)), codici_dataset_str, hierarchy_str] + riga_dataset
    return None

def get_hierarchy_string(codes, hierarchy_dict):
    hierarchy_list = []
    for code in codes:
        if code in hierarchy_dict:
            padri = ",".join(sorted(hierarchy_dict[code]))
            hierarchy_list.append(f"[{code}---{padri}]")
        else:
            hierarchy_list.append(f"[{code}---]")
    return "".join(hierarchy_list)

def extract_reports_to_csv(codici_file, dataset_file, hierarchy_file, output_directory, num_rows=None):
    os.makedirs(output_directory, exist_ok=True)
    
    df_codici = pd.read_csv(codici_file, header=None, dtype=str).fillna('')
    if num_rows is not None:
        df_codici = df_codici.head(num_rows)
    df_dataset = pd.read_csv(dataset_file, dtype=str).fillna('')
    df_hierarchy = pd.read_csv(hierarchy_file, dtype=str, header=None).fillna('')
    
    dataset_dict = {}
    for _, row in df_dataset.iterrows():
        dataset_codici = frozenset(row.iloc[0].split(','))
        dataset_padri = frozenset(row.iloc[1].split(','))
        dataset_totali = dataset_codici.union(dataset_padri)
        dataset_dict[dataset_totali] = (dataset_codici, dataset_padri, row)
    
    hierarchy_dict = {}
    for _, row in df_hierarchy.iterrows():
        code = row.iloc[0]
        padri = set([p.strip() for p in row.iloc[1:].dropna()])
        hierarchy_dict[code] = padri
    
    output_data_matches, output_data_no_matches, output_data_exact_matches, output_data_all_codes = [], [], [], []
    
    for _, row in df_codici.iterrows():
        codici_riga = frozenset([codice.strip() for sublist in row.dropna().astype(str).apply(lambda x: x.split(',')) for codice in sublist if codice.strip() != ''])
        codici_riga_str = ",".join(sorted(codici_riga))
        
        exact_matching_rows = [
            [",".join(sorted(codici_riga)), ",".join(sorted(dataset_dict[dataset_totali][0])), get_hierarchy_string(dataset_dict[dataset_totali][0], hierarchy_dict)] + dataset_dict[dataset_totali][2].tolist()
            for dataset_totali, (dataset_codici, dataset_padri, _) in dataset_dict.items() if codici_riga == dataset_codici
        ]
        
        if exact_matching_rows:
            output_data_exact_matches.extend(exact_matching_rows)
            output_data_all_codes.append(exact_matching_rows[0])
        else:
            match_result = process_match(codici_riga, dataset_dict, hierarchy_dict)
            if match_result:
                output_data_matches.append(match_result)
                output_data_all_codes.append(match_result)
            else:
                output_data_no_matches.append([codici_riga_str] + ["Nessuna corrispondenza"] * (len(df_dataset.columns)))
                output_data_all_codes.append([codici_riga_str] + ["not found in dataset"] * (len(df_dataset.columns)))
    
    pd.DataFrame(output_data_matches).to_csv(os.path.join(output_directory, "report_matches.csv"), index=False, encoding='utf-8')

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    codici_file = os.path.join(output_dir, "HPO-t2-formatted.csv")
    dataset_file = os.path.join(output_dir, "ordered_dataset_withparents.csv")
    hierarchy_file = os.path.join(output_dir, "completehpohierarchy.csv")
    extract_reports_to_csv(codici_file, dataset_file, hierarchy_file, output_dir)

if __name__ == "__main__":
    main()
