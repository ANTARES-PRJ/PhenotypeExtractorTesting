import pandas as pd
import re
import os
from itertools import combinations

def clean_hpo_code(hpo_code):
    """ Rimuove il prefisso 'HP:' e gli zeri iniziali dai codici HPO, mantenendo tutti i valori tranne '0' singolo. """
    if pd.isna(hpo_code):  # Controlla se il valore è NaN
        return None
    cleaned_code = re.sub(r"^HP:0*", "", str(hpo_code))  # Rimuove 'HP:' e tutti gli 0 iniziali
    return cleaned_code if cleaned_code != "0" else None  # Esclude solo lo zero singolo

def get_phenotypes_from_csv(depth, file_path):
    """ Legge i codici HPO dal file CSV fino alla profondità specificata. """
    try:
        df = pd.read_csv(file_path, header=0, dtype=str)  # Legge come stringa
        if depth < 1 or depth > len(df):
            raise ValueError(f"La depth deve essere compresa tra 1 e {len(df)}.")

        combined_phenotypes = set()
        for i in range(depth):
            combined_phenotypes.update(df.iloc[i, 1:].dropna())

        cleaned_phenotypes = [clean_hpo_code(p) for p in combined_phenotypes]
        return sorted(filter(None, cleaned_phenotypes))  # Rimuove eventuali valori vuoti

    except Exception as e:
        print(f"Errore durante la lettura del file CSV: {e}")
        return []

def parse_hierarchy_csv(hierarchy_path):
    """ Analizza il file CSV delle gerarchie per ottenere la mappa delle superclassi. """
    try:
        df = pd.read_csv(hierarchy_path, dtype=str, low_memory=False)

        if "HPO_Code" not in df.columns or "Superclass_1" not in df.columns:
            raise ValueError("Il CSV non contiene le colonne necessarie.")

        hierarchy_map = {}
        for _, row in df.iterrows():
            base_phenotype = clean_hpo_code(row["HPO_Code"])
            supercategories = [clean_hpo_code(sc) for sc in row.dropna().tolist()[1:]]
            hierarchy_map[base_phenotype] = [sc for sc in supercategories if sc]

        return hierarchy_map

    except Exception as e:
        print(f"Errore durante il parsing del file gerarchia CSV: {e}")
        return {}

def write_ctwedge_parameters(filename, phenotypes, num_phenotypes):
    """ Scrive solo la sezione dei parametri nel file CTWedge """
    # Pulizia e ordinamento dei codici
    cleaned_phenotypes = sorted(set(filter(None, [clean_hpo_code(hpo) for hpo in phenotypes])), key=int)

    with open(filename, "w", encoding="utf-8") as file:
        file.write("Model HPO\n\n")
        file.write("Parameters:\n")
        for i in range(1, num_phenotypes + 1):
            file.write(f"\tphenotype{i}: {{{', '.join(['NULL'] + cleaned_phenotypes)}}};\n")

    print(f"File '{filename}' creato con i parametri.")

def extract_phenotypes_from_ctwedge(filename):
    """ Estrae i codici HPO dai parametri definiti nel file CTWedge. """
    phenotypes = []
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            match = re.match(r"\tphenotype\d+: \{(.+?)\}", line)
            if match:
                values = match.group(1).split(", ")
                phenotypes.extend([v for v in values if v != "NULL"])
    return sorted(set(phenotypes))

def count_phenotype1_hpo_codes(filename):
    """ Conta quanti codici HPO sono presenti in phenotype1. """
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            if line.startswith("\tphenotype1: {"):
                match = re.match(r"\tphenotype1: \{(.+?)\}", line)
                if match:
                    codes = match.group(1).split(", ")
                    hpo_count = len([c for c in codes if c != "NULL"])
                    print(f"Numero di codici HPO in phenotype1: {hpo_count}")
                    return hpo_count
    return 0

def write_ctwedge_constraints(filename, hierarchy_path, num_phenotypes):
    """ Aggiunge i vincoli al file CTWedge basandosi sui codici HPO estratti, considerando anche le superclassi. """
    hierarchy_map = parse_hierarchy_csv(hierarchy_path)
    phenotypes = extract_phenotypes_from_ctwedge(filename)

    with open(filename, "a", encoding="utf-8") as file:
        file.write("\nConstraints:\n")

        # Vincolo: Se n-1 fenotipi sono NULL, l'altro deve essere diverso da NULL
        for null_phenotypes in combinations(range(1, num_phenotypes + 1), num_phenotypes - 1):
            non_null_phenotype = set(range(1, num_phenotypes + 1)) - set(null_phenotypes)
            non_null_phenotype = non_null_phenotype.pop()  # L'unico che non è NULL
            
            # Scriviamo il vincolo
            null_conditions = " AND ".join(f"phenotype{i}=NULL" for i in null_phenotypes)
            file.write(f"\t# ({null_conditions}) => (phenotype{non_null_phenotype}!=NULL) #\n")


        # Vincoli per rendere i fenotipi unici (nessun duplicato tra loro)
        for i in range(1, num_phenotypes + 1):
            for j in range(1, num_phenotypes + 1):
                if i != j:
                    file.write(f"\t# phenotype{i}!=NULL => (phenotype{i}!=phenotype{j}) #\n")

        # Vincoli gerarchici
        for base_phenotype, supercategories in hierarchy_map.items():
            if base_phenotype not in phenotypes:
                continue

            for i in range(1, num_phenotypes + 1):
                for j in range(1, num_phenotypes + 1):
                    if i != j:
                        constraints = [
                            f"phenotype{j}!={sc}"
                            for sc in supercategories if sc in phenotypes and sc != base_phenotype
                        ]
                        if constraints:
                            file.write(f"\t# phenotype{i}=={base_phenotype} => (" + " AND ".join(constraints) + ") #\n")

    print(f"Vincoli aggiunti nel file '{filename}'")


def count_phenotype1_constraints(ctwedge_file):
    """ Conta quante righe nel file CTWedge iniziano con '# phenotype1'. """
    count = 0
    try:
        with open(ctwedge_file, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip().startswith("# phenotype1"):
                    count += 1
        print(f"Il numero di righe che iniziano con '# phenotype1' è: {count}")
        return count
    except Exception as e:
        print(f"Errore nell'aprire o leggere il file: {e}")
        return 0

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Ottiene la directory dello script
    output_dir = os.path.join(script_dir, "output")  
    os.makedirs(output_dir, exist_ok=True)
    try:
        depth = int(input("Inserisci numero di righe da considerare per la depth: "))
        num_phenotypes = int(input("Inserisci il numero di fenotipi generare: "))
    except ValueError:
        print("Errore: la depth e il numero di fenotipi devono essere numeri interi.")
        return

    
    csv_path = os.path.join(output_dir, "true_depth_from118_cleaned.csv")
    hierarchy_path = os.path.join(output_dir, "completehpohierarchy_from118_cleaned.csv")
    output_file = os.path.join(output_dir, "test.ctw")


    phenotypes = get_phenotypes_from_csv(depth, csv_path)
    if not phenotypes:
        print("Errore: impossibile ottenere i fenotipi dal file CSV.")
        return

    write_ctwedge_parameters(output_file, phenotypes, num_phenotypes)

    count_phenotype1_hpo_codes(output_file)

    write_ctwedge_constraints(output_file, hierarchy_path, num_phenotypes)

    count_phenotype1_constraints(output_file)

if __name__ == "__main__":
    main()
