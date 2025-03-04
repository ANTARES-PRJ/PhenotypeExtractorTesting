import os
import re

def traduci_ctwedge_acts(ctwedge_file, acts_file, output_dir):
    """Traduce un file CTWedge in formato ACTS."""
    
    parametri = []
    vincoli = []
    nome_modello = "HPO"  # Valore di default nel caso il file non abbia una prima riga valida

    # Crea i percorsi completi dei file
    ctwedge_path = os.path.join(output_dir, ctwedge_file)
    acts_path = os.path.join(output_dir, acts_file)

    try:
        with open(ctwedge_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Errore: il file {ctwedge_path} non è stato trovato.")
        return

    # Legge il nome del modello dalla prima riga
    if lines:
        prima_riga = lines[0].strip()
        if prima_riga.startswith("Model "):
            nome_modello = prima_riga.split("Model ")[1]  # Estrai il nome dopo "Model "

    # Aggiungi il nome del sistema nel formato ACTS
    system_info = ["[System]", f"Name: {nome_modello}", ""]

    # Analisi dei parametri
    parsing_parametri = False
    for line in lines:
        line = line.strip()
        if line.startswith("Parameters:"):
            parsing_parametri = True
            parametri.append("[Parameter]")  # Inizio della sezione parametri
            continue
        if parsing_parametri:
            if line:  # Se la riga non è vuota
                match = re.match(r'(\w+): \{(.+?)\};', line)  # Regex per estrarre nome e valori
                if match:
                    nome_parametro, valori = match.groups()
                    parametri.append(f"{nome_parametro}(enum):{valori}")
            else:
                parsing_parametri = False  # Interrompe il parsing su riga vuota

    # Analisi dei vincoli
    parsing_vincoli = False
    for line in lines:
        line = line.strip()
        if line.startswith("Constraints:"):
            parsing_vincoli = True
            continue
        if parsing_vincoli and line.startswith("#"):
            vincolo = line.strip("# ").strip()
            vincoli.append(vincolo)

    # Traduzione in ACTS
    acts_lines = system_info + parametri[:]  # Includi le info di sistema e i parametri
    acts_lines.append("")  # Riga vuota per separazione
    acts_lines.append("[Constraint]")

    for vincolo in vincoli:
        acts_lines.append(traduci_vincolo(vincolo))

    # Scrittura del file ACTS
    with open(acts_path, 'w') as f:
        f.write('\n'.join(acts_lines))

    print(f"File ACTS creato: {acts_path}")

def traduci_vincolo(vincolo_ctwedge):
    """Traduce un singolo vincolo CTWedge in formato ACTS."""
    
    # Sostituzione degli operatori logici
    vincolo_acts = vincolo_ctwedge.replace("AND", "&&").replace("OR", "||")

    # Gestione dei confronti con "NULL"
    vincolo_acts = vincolo_acts.replace("=NULL", "=\"NULL\"")
    vincolo_acts = vincolo_acts.replace("!=NULL", "!=\"NULL\"")

    # Gestione dei confronti con valori numerici
    vincolo_acts = re.sub(r'([a-zA-Z0-9_]+)==(\d+)', r'\1=\2', vincolo_acts)
    vincolo_acts = re.sub(r'([a-zA-Z0-9_]+)!=(\d+)', r'\1!=\2', vincolo_acts)

    # Gestione di condizioni multiple
    vincolo_acts = re.sub(r'\(([^)]+)\) && \(([^)]+)\)', r'(\1) && (\2)', vincolo_acts)
    vincolo_acts = re.sub(r'\(([^)]+)\) \|\| \(([^)]+)\)', r'(\1) || (\2)', vincolo_acts)

    return vincolo_acts

# Gestione della cartella output
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "output")
os.makedirs(output_dir, exist_ok=True)

# Esempio di utilizzo
ctwedge_file = "test.ctw"  # Nome del file di input
acts_file = "hpo.acts"
traduci_ctwedge_acts(ctwedge_file, acts_file, output_dir)
