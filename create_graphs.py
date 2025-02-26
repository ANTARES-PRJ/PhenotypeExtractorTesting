import pandas as pd
import matplotlib.pyplot as plt
import os
import obonet

# Ottieni il percorso della cartella in cui si trova il file .py
script_dir = os.path.dirname(os.path.abspath(__file__))

# Imposta il percorso per la cartella 'output' che contiene i file CSV
output_dir = os.path.join(script_dir, 'output')

# Percorsi dei file relativi alla cartella 'output'
ordered_hpo_path = os.path.join(output_dir, 'true_depth.csv')
total_counts_path = os.path.join(output_dir, 'total_counts.csv')
obo_file_path = os.path.join(output_dir, 'hp.obo')

# Richiedi all'utente di specificare il numero di righe di profondità da caricare
while True:
    try:
        num_rows = int(input("Inserisci il numero di righe di profondità da caricare: "))
        if num_rows <= 0:
            print("Inserisci un numero maggiore di zero.")
        else:
            break
    except ValueError:
        print("Inserisci un numero valido.")

# Leggi i dati dal file CSV
ordered_hpo_df = pd.read_csv(ordered_hpo_path)
# Limita il numero di righe di profondità in base alla scelta dell'utente
ordered_hpo_df = ordered_hpo_df.head(num_rows)

# Carica il file CSV con i totali dei count per ogni codice
total_counts_df = pd.read_csv(total_counts_path)

# Crea un dizionario per mappare HPO_ID -> Total_Count
total_counts_dict = dict(zip(total_counts_df['HPO_ID'], total_counts_df['Total_Count']))

# Funzione per caricare il file OBO e creare un dizionario di mappatura HPO_ID -> nome
def load_hpo_names(obo_file):
    graph = obonet.read_obo(obo_file)
    hpo_names = {}
    
    for node, data in graph.nodes(data=True):
        name = data.get('name', 'Unknown')
        hpo_names[node] = name
    
    return hpo_names

# Carica la mappatura degli HPO_ID ai loro nomi dal file OBO
hpo_names_dict = load_hpo_names(obo_file_path)

# Crea una cartella per salvare i grafici se non esiste
bar_charts_dir = os.path.join(output_dir, 'bar_charts')
if not os.path.exists(bar_charts_dir):
    os.makedirs(bar_charts_dir)

# Specifica i codici HPO da saltare nella rappresentazione grafica
excluded_hpo_codes = {'HP:0000001', 'HP:0000118'}

# Creare un dizionario per raccogliere i conteggi totali per ogni HPO_ID
hpo_count_dict = {}

# Itera su ogni riga 
for index, row in ordered_hpo_df.iterrows():
    # Estrai i codici dalla riga 
    codes = row[1:].dropna().values  # Tutti i codici tranne la colonna 'Count' e NaN
    counts = [total_counts_dict.get(code, 0) for code in codes]  # Ottieni i count totali per ogni codice
    
    # Somma i conteggi per ogni codice HPO_ID, escludendo i codici specificati
    for code, count in zip(codes, counts):
        if code in excluded_hpo_codes:
            continue  # Salta i codici esclusi
        if code in hpo_count_dict:
            hpo_count_dict[code] += count
        else:
            hpo_count_dict[code] = count

# Prepara i dati 
codes = list(hpo_count_dict.keys())
counts = list(hpo_count_dict.values())

# Ordina i codici per count in ordine decrescente e prendi i primi 200
sorted_indices = sorted(range(len(counts)), key=lambda i: counts[i], reverse=True)[:1000]
sorted_codes = [codes[i] for i in sorted_indices]
sorted_counts = [counts[i] for i in sorted_indices]

# Converti gli HPO_ID in nomi
sorted_labels = [f"{hpo_names_dict.get(code, code)} ({code})" for code in sorted_codes]

# Raggruppa i disease con lo stesso count sulla stessa riga separati da una virgola
grouped_labels = {}
for label, count in zip(sorted_labels, sorted_counts):
    if count not in grouped_labels:
        grouped_labels[count] = []
    grouped_labels[count].append(label)

# Prepara i dati per il grafico
final_labels = []
final_counts = []

# Aggrega le etichette per count
for count, labels in grouped_labels.items():
    final_labels.append(", ".join(labels))
    final_counts.append(count)

# Dividi i dati in dieci gruppi da 75 ciascuno
group_size = 75
groups = [final_labels[i:i+group_size] for i in range(0, len(final_labels), group_size)]
count_groups = [final_counts[i:i+group_size] for i in range(0, len(final_counts), group_size)]

# Crea e salva i grafici per ciascun gruppo
for i, (labels_group, counts_group) in enumerate(zip(groups, count_groups)):
    plt.figure(figsize=(12, 15))  # Dimensioni per ciascun grafico (più alte per i nomi)
    plt.barh(labels_group, counts_group, color=plt.cm.viridis([count / max(counts_group) for count in counts_group]))

    # Etichette e titolo
    plt.xlabel('Count', fontsize=14)
    plt.ylabel('HPO IDs', fontsize=14)
    plt.title(f'Top HPO Counts (Part {i+1})', fontsize=16)

    # Aggiungi il numero alle barre
    for j, count in enumerate(counts_group):
        plt.text(count + 10, j, f'{count}', va='center', color='black', fontsize=12)

    # Ruota le etichette dell'asse y per evitare sovrapposizione
    plt.yticks(rotation=0, fontsize=10)

    # Inverti l'asse y per visualizzare prima i valori con count più alto
    plt.gca().invert_yaxis()

    # Percorso per il salvataggio del grafico
    bar_chart_path = os.path.join(bar_charts_dir, f"top_1000_aggregated_bar_chart_part_{i+1}.png")
    plt.savefig(bar_chart_path, bbox_inches='tight', dpi=300)  # Salva il grafico come immagine con alta qualità
    plt.close()

print(f"I grafici a barre aggregati dei primi 1000 HPO IDs sono stati creati e salvati come immagini in {bar_charts_dir}")
