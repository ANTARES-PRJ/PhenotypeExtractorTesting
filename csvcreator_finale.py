import os
import pandas as pd

def extract_reports_to_csv(codici_file, dataset_file, output_directory):
    # Creazione della cartella di output se non esiste
    os.makedirs(output_directory, exist_ok=True)
    
    # Definizione dei file di output
    output_file_matches = os.path.join(output_directory, "report_matches.csv")

    # Caricamento dei file in DataFrame
    df_codici = pd.read_csv(codici_file, header=None, dtype=str).fillna('')  # Codici input
    df_dataset = pd.read_csv(dataset_file, dtype=str, usecols=[0, 1, 2]).fillna('')  # Dataset

    # Creazione dizionario per confronti rapidi
    dataset_dict = {}
    dataset_reports = {}

    for _, row in df_dataset.iterrows():
        dataset_codici = frozenset(row.iloc[0].split(','))  
        dataset_padri = frozenset(row.iloc[1].split(','))
        report = row.iloc[2]
        dataset_totali = dataset_codici.union(dataset_padri)

        dataset_dict[dataset_totali] = (dataset_codici, dataset_padri)
        dataset_reports[dataset_totali] = report

    # Liste di output
    output_data_matches = []
    output_data_no_matches = []
    output_data_exact_matches = []

    # Analisi dei codici di input
    for _, row in df_codici.iterrows():
        codici_riga = frozenset([codice.strip() for sublist in row.dropna().astype(str).apply(lambda x: x.split(',')) for codice in sublist if codice.strip() != ''])
        codici_riga_str = ",".join(sorted(codici_riga))

        matching_reports = []
        exact_matching_reports = []

        # Controllo con il dizionario
        for dataset_totali in dataset_dict:
            if codici_riga.issubset(dataset_totali):
                dataset_codici, dataset_padri = dataset_dict[dataset_totali]
                report = dataset_reports[dataset_totali]
                matching_reports.append([",".join(sorted(dataset_codici)), ",".join(sorted(dataset_padri)), report])

                if codici_riga == frozenset(dataset_codici):
                    exact_matching_reports.append([",".join(sorted(codici_riga)), ",".join(sorted(dataset_codici)), ",".join(sorted(dataset_padri)), report])

        # Salvataggio risultati
        if matching_reports:
            for report_data in matching_reports:
                output_data_matches.append([codici_riga_str] + report_data)
        else:
            output_data_no_matches.append([codici_riga_str, "Nessuna corrispondenza", "Nessuna corrispondenza", "Nessuna corrispondenza"])

        if exact_matching_reports:
            for report_data in exact_matching_reports:
                report = report_data[3] if report_data[3] else ""
                output_data_exact_matches.append([report_data[0], report_data[1], report_data[2], report])

    # Creazione DataFrame e salvataggio file
    pd.DataFrame(output_data_matches, columns=["Codici Input", "Codici Originali", "Codici Originali+Padri", "Report"]).to_csv(output_file_matches, index=False, encoding='utf-8')

    print(f"Estrazione completata! I file CSV sono stati salvati nella cartella: {output_directory}")

# Definizione file e cartella di output
script_dir = os.path.dirname(os.path.abspath(__file__))

# Definisce la cartella 'output' come directory di lavoro
output_dir = os.path.join(script_dir, "output")
os.makedirs(output_dir, exist_ok=True)  

# Percorsi dei file di input
codici_file = os.path.join(output_dir, "HPO-t2-formatted.csv")
dataset_file = os.path.join(output_dir, "ordered_dataset_withparents.csv")

# Esecuzione della funzione
extract_reports_to_csv(codici_file, dataset_file, output_dir)