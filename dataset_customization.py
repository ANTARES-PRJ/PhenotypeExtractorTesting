import os
import pandas as pd
import random
import re
from names import male_names_list, female_names_list, hospital_physicians, surname_list

# Ottieni la cartella dello script
base_dir = os.path.dirname(os.path.realpath(__file__))
output_dir = os.path.join(base_dir, "output")

# Assicurati che la cartella output esista
os.makedirs(output_dir, exist_ok=True)

# Percorsi dei file
input_file = os.path.join(output_dir, "merged_dataset.csv")
output_file1 = os.path.join(output_dir, "ordered_dataset.csv")


# Carica il DataFrame
df = pd.read_csv(input_file)

# Funzione per pulire l'intestazione del documento
def pulisci_intestazione(text, start_marker="Reason for consultation", alternative_marker="Medical History", end_marker="Signature", end_marker2="Dr.", sex_marker=["SexMale", "SexFemale"]):
    patient_name = None
    specialty = None
    lines = text.splitlines()

    for line in lines:
        line = line.strip()
        if line.startswith("Patient:"):
            patient_name = line.replace("Patient:", "").strip()
        if "Specialist" in line:
            specialty = line.strip()
            break

    if start_marker in text:
        text = text.split(start_marker, 1)[-1]
    elif alternative_marker in text:
        text = text.split(alternative_marker, 1)[-1]

    for marker in sex_marker:
        if marker in text:
            text = text.split(marker, 1)[-1].strip()
            break

    if end_marker in text:
        text = text.split(end_marker, 1)[0]
    if end_marker2 in text:
        text = text.split(end_marker2, 1)[0]

    header = ""
    if specialty:
        header += f"{specialty}\n"
    if patient_name:
        header += f"Patient: {patient_name}\n"
    
    return header + text.strip()

df["Documento"] = df["Documento"].apply(pulisci_intestazione)

# Pulizia della colonna HPO_IDs
def pulisci_hpo_ids(valore):
    if isinstance(valore, str):
        return valore.replace("[", "").replace("]", "").replace("'", "").strip()
    return valore

df['HPO_IDs'] = df['HPO_IDs'].apply(pulisci_hpo_ids)
df = df[df['HPO_IDs'].str.strip().astype(bool)]
df['HPO_IDs'] = df['HPO_IDs'].str.replace(r"(?<!\,)\s+(?!\,)", r",", regex=True)
df = df[df['Documento'].str.strip().astype(bool)]

# Funzione per sostituire il nome del paziente con nomi casuali
def sostituisci_nome_paziente(testo, lista_nomi_maschili, lista_nomi_femminili, ospedali_medici):
    if isinstance(testo, str):
        if "Patient" in testo:
            start_pos = testo.find("Patient:") + len("Patient:")
            end_pos = testo.find("\n", start_pos)
            if end_pos == -1:
                end_pos = len(testo)
            nome_paziente_esistente = testo[start_pos:end_pos].strip()

            if nome_paziente_esistente in ["Ana García", "Ana García Pérez", "Ana García López"]:
                nome_paziente_nuovo = f"{random.choice(lista_nomi_femminili)} {random.choice(surname_list)}"
            elif nome_paziente_esistente == "Juan Pérez":
                nome_paziente_nuovo = f"{random.choice(lista_nomi_maschili)} {random.choice(surname_list)}"
            else:
                if any(keyword in testo.lower() for keyword in ["female", "woman", "ova", "ovarian", "vagina"]):
                    nome_paziente_nuovo = f"{random.choice(lista_nomi_femminili)} {random.choice(surname_list)}"
                elif any(keyword in testo.lower() for keyword in ["male", "testicular", "scrotus", "penis"]):
                    nome_paziente_nuovo = f"{random.choice(lista_nomi_maschili)} {random.choice(surname_list)}"
                else:
                    nome_paziente_nuovo = f"{random.choice(lista_nomi_maschili)} {random.choice(surname_list)}"

            testo = testo[:start_pos] + " " + nome_paziente_nuovo + testo[end_pos:]
        else:
            if any(keyword in testo.lower() for keyword in ["female", "woman", "ova", "ovarian", "vagina"]):
                nome_paziente_nuovo = f"{random.choice(lista_nomi_femminili)} {random.choice(surname_list)}"
            else:
                nome_paziente_nuovo = f"{random.choice(lista_nomi_maschili)} {random.choice(surname_list)}"

            testo = f"Patient: {nome_paziente_nuovo}\n" + testo

        ospedale_random = random.choice(list(ospedali_medici.keys()))
        medico_random = random.choice(ospedali_medici[ospedale_random])
        testo = f"Hospital: {ospedale_random}\nDoctor: {medico_random}\n" + testo

        return testo
    return testo

df['Documento'] = df['Documento'].apply(
    lambda x: sostituisci_nome_paziente(x, male_names_list, female_names_list, hospital_physicians)
)

# Generalizzazione dei report rimuovendo identificatori 
frasi_da_rimuovere = [
    "Physical examination:", "Diagnostic impression:", "Central University Hospital",
    "Dr. Ana López, ", "Dr. Javier López, ", "Dr. Ana López", "Dr. Javier López", "López",
    "Signature", "Signed", "Treatment:", "Background:", "Patient background",
    "Diagnosis", "Medical history", "Clinical findings", "Reason for Consultation",
    "Personal History", "Physical Examination", "Diagnostic Impression",
    "García Pérez", "Juan Perez", "Juan Pérez,", "Juan Pérez", "Ana García López",
    "Mr. Juan Pérez", "Juan's", "Name Juan Pérez", "San Juan University Hospital",
    "Diagnostic plan", "Juan", "Garcia's ", "Garcia", "Pérez", "Ana García", "Dr. Martínez"
]

# Funzione per rimuovere le frasi dal testo
def pulisci_frasi(text, frasi):
    if isinstance(text, str):
        for frase in frasi:
            text = text.replace(frase, "")
        return text.strip()
    return text

df['Documento'] = df['Documento'].apply(lambda x: pulisci_frasi(x, frasi_da_rimuovere))
df['Documento'] = df['Documento'].str.replace(":", "", regex=False)

# Salvataggio file
df.to_csv(output_file1, index=False)


print("Dataset modificato e reso anonimo con nomi inventati")
