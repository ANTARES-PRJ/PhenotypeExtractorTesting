import os
import pandas as pd
import random


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

    search_match(lambda codici, padri: codici)
    search_match(lambda codici, padri: codici.union(padri), is_combined=True)

    if exact_matches:
        return random.choice(exact_matches)
    elif partial_matches:
        return random.choice(partial_matches)
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

    output_file_matches = os.path.join(output_directory, "report_matches.csv")
    output_file_no_matches = os.path.join(output_directory, "report_no_matches.csv")
    output_file_exact_matches = os.path.join(output_directory, "report_exact_matches.csv")
    output_file_all_codes = os.path.join(output_directory, "report_all_codes.csv")

    pd.DataFrame(output_data_matches).to_csv(output_file_matches, index=False, encoding='utf-8')
    pd.DataFrame(output_data_no_matches).to_csv(output_file_no_matches, index=False, encoding='utf-8')
    pd.DataFrame(output_data_exact_matches).to_csv(output_file_exact_matches, index=False, encoding='utf-8')
    pd.DataFrame(output_data_all_codes).to_csv(output_file_all_codes, index=False, encoding='utf-8')

    print(f"Estrazione completata! I file CSV sono stati salvati nella cartella: {output_directory}")


script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "output")
os.makedirs(output_dir, exist_ok=True)
codici_file = os.path.join(output_dir, "formatted_codes.csv")
dataset_file = os.path.join(output_dir, "ordered_dataset_withparents.csv")
hierarchy_file = os.path.join(output_dir, "completehpohierarchy.csv")

while True:
    try:
        num_rows_input = input("Inserisci il numero di righe da analizzare da formatted_codes.csv o premi Invio per analizzare tutte le righe: ")
        if num_rows_input == "":
            num_rows = None
            break
        else:
            num_rows = int(num_rows_input)
            if num_rows > 0:
                break
            else:
                print("Inserisci un numero positivo.")
    except ValueError:
        print("Inserisci un numero intero valido o premi Invio.")

extract_reports_to_csv(codici_file, dataset_file, hierarchy_file, output_dir, num_rows=num_rows)