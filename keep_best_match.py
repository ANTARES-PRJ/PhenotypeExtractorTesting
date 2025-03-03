import os
import pandas as pd
import random


def select_best_match(input_codes, dataset_dict, dataset_reports):
    best_match = None
    best_match_size = float('inf')
    best_report_candidates = []

    # Funzione per cercare il miglior match
    def search_match(codes_to_search, is_combined=False):
        nonlocal best_match_size, best_report_candidates
        for dataset_totali in dataset_dict:
            dataset_codici, dataset_padri = dataset_dict[dataset_totali]
            all_codes = codes_to_search(dataset_codici, dataset_padri) if is_combined else dataset_codici
            if input_codes == all_codes:
                return [dataset_codici, dataset_padri, dataset_reports[dataset_totali]]
            elif input_codes.issubset(all_codes):
                if len(dataset_codici) < best_match_size:
                    best_match_size = len(dataset_codici)
                    best_report_candidates = [(dataset_codici, dataset_padri, dataset_reports[dataset_totali])]
                elif len(dataset_codici) == best_match_size:
                    best_report_candidates.append((dataset_codici, dataset_padri, dataset_reports[dataset_totali]))

    # Prima ricerca tra i codici originali
    search_match(lambda codici, padri: codici)
    
    # Se non trovata corrispondenza, prova con i codici originali + padri
    search_match(lambda codici, padri: codici.union(padri), is_combined=True)

    # Se ci sono più candidati con la stessa numerosità, seleziona uno a caso
    if best_report_candidates:
        return random.choice(best_report_candidates)

    return None


def process_match(codici_riga, dataset_dict, dataset_reports):
    # Seleziona il miglior match durante l'assegnazione
    match_result = select_best_match(codici_riga, dataset_dict, dataset_reports)

    if match_result:
        dataset_codici, dataset_padri, report = match_result
        return [",".join(sorted(codici_riga)), ",".join(sorted(dataset_codici)), ",".join(sorted(dataset_padri)), report]
    return None


def extract_reports_to_csv(codici_file, dataset_file, output_directory):
    os.makedirs(output_directory, exist_ok=True)

    # Caricamento file CSV
    df_codici = pd.read_csv(codici_file, header=None, dtype=str).fillna('')
    df_dataset = pd.read_csv(dataset_file, dtype=str, usecols=[0, 1, 2]).fillna('')

    # Creazione dizionari per i confronti
    dataset_dict, dataset_reports = {}, {}
    for _, row in df_dataset.iterrows():
        dataset_codici = frozenset(row.iloc[0].split(','))
        dataset_padri = frozenset(row.iloc[1].split(','))
        report = row.iloc[2]
        dataset_totali = dataset_codici.union(dataset_padri)
        dataset_dict[dataset_totali] = (dataset_codici, dataset_padri)
        dataset_reports[dataset_totali] = report

    # Liste per i risultati
    output_data_matches, output_data_no_matches, output_data_exact_matches = [], [], []

    # Analisi dei codici di input
    for _, row in df_codici.iterrows():
        codici_riga = frozenset([codice.strip() for sublist in row.dropna().astype(str).apply(lambda x: x.split(',')) for codice in sublist if codice.strip() != ''])
        codici_riga_str = ",".join(sorted(codici_riga))

        # Elenco di report per esatti match
        exact_matching_reports = [
            [",".join(sorted(codici_riga)), ",".join(sorted(dataset_codici)), ",".join(sorted(dataset_padri)), dataset_reports[dataset_totali]]
            for dataset_totali, (dataset_codici, dataset_padri) in dataset_dict.items() if codici_riga == dataset_codici
        ]

        if exact_matching_reports:
            output_data_exact_matches.extend(exact_matching_reports)
        else:
            match_result = process_match(codici_riga, dataset_dict, dataset_reports)
            if match_result:
                # Aggiungi le righe con i dati corrispondenti
                output_data_matches.append(match_result)
            else:
                # Aggiungi righe "no match"
                output_data_no_matches.append([codici_riga_str, "Nessuna corrispondenza", "Nessuna corrispondenza", "Nessuna corrispondenza"])

    # Salvataggio dei CSV
    output_file_matches = os.path.join(output_directory, "report_matches.csv")
    output_file_no_matches = os.path.join(output_directory, "report_no_matches.csv")
    output_file_exact_matches = os.path.join(output_directory, "report_exact_matches.csv")

    pd.DataFrame(output_data_matches, columns=["Codici Input", "Codici Originali", "Codici Originali+Padri", "Report"]).to_csv(output_file_matches, index=False, encoding='utf-8')
    pd.DataFrame(output_data_no_matches, columns=["Codici Input", "Codici Originali", "Codici Originali+Padri", "Report"]).to_csv(output_file_no_matches, index=False, encoding='utf-8')
    pd.DataFrame(output_data_exact_matches, columns=["Codici Input", "Codici Originali", "Codici Originali+Padri", "Report"]).to_csv(output_file_exact_matches, index=False, encoding='utf-8')

    print(f"Estrazione completata! I file CSV sono stati salvati nella cartella: {output_directory}")


# Esecuzione della funzione
script_dir = os.path.dirname(os.path.abspath(__file__))

# Definisce la cartella 'output' come directory di lavoro
output_dir = os.path.join(script_dir, "output")
os.makedirs(output_dir, exist_ok=True)  

# Definizione file e cartella di output
codici_file = os.path.join(output_dir, "formatted_codes.csv")
dataset_file = os.path.join(output_dir, "ordered_dataset_withparents.csv")

# Esegui la funzione principale
extract_reports_to_csv(codici_file, dataset_file, output_dir)
