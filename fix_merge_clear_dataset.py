import pandas as pd
import random
import re
from NomiCreator import ospedali_medici,nomi_maschili_lista,nomi_femminili_lista,cognomi_lista

# Carico il DataFrame
df = pd.read_csv(r"C:\Users\Amorl\Desktop\progetto\Database_unito.csv")

def pulisci_intestazione(text, start_marker="Reason for consultation", alternative_marker="Medical History", end_marker="Signature",end_marker2="Dr.", sex_marker=["SexMale", "SexFemale"]):
    patient_name = None
    specialty = None

    # Split il testo in righe per analizzarle
    lines = text.splitlines()

    # Cerca il nome del paziente
    for line in lines:
        line = line.strip()
        if line.startswith("Patient:"):
            patient_name = line.replace("Patient:", "").strip()

    # Trova la riga che contiene "Specialist"
    for line in lines:
        line = line.strip()
        if "Specialist" in line:
            specialty = line.strip()
            break

    # Se "Reason for consultation" è presente, inizia da lì
    if start_marker in text:
        text = text.split(start_marker, 1)[-1]
    # Altrimenti, se "Medical History" è presente, inizia da lì
    elif alternative_marker in text:
        text = text.split(alternative_marker, 1)[-1]

    # Se "SexMale" o "SexFemale" è presente, rimuovi tutto ciò che precede (inclusi questi termini)
    for marker in sex_marker:
        if marker in text:
            text = text.split(marker, 1)[-1].strip()
            break

    # Se "Signature" è presente, elimina tutto quello che viene dopo
    if end_marker in text:
        text = text.split(end_marker, 1)[0]
    if end_marker2 in text:
        text = text.split(end_marker2, 1)[0]
    # Aggiungi nome del paziente e specializzazione al testo
    header = ""
    if specialty:
        header += f"{specialty}\n"
    if patient_name:
        header += f"Patient: {patient_name}\n"
    
    
    return header + text.strip()

df["Documento"] = df["Documento"].apply(
    lambda x: pulisci_intestazione(x, start_marker="Reason for consultation", 
                                   alternative_marker="Medical History", 
                                   end_marker="Signature")
)

df.to_csv(r"C:\Users\Amorl\Desktop\progetto\Dataset1.csv", index=False)
def pulisci_hpo_ids(valore):
    if isinstance(valore, str):  # Verifica che il valore sia una stringa
        return valore.replace("[", "").replace("]", "").replace("'", "").strip()
    return valore

# Applicazione della funzione al DataFrame
df['HPO_IDs'] = df['HPO_IDs'].apply(pulisci_hpo_ids)

# Filtra le righe non vuote
df = df[df['HPO_IDs'].str.strip().astype(bool)]

# Sostituisci spazi con virgole, senza aggiungere doppie virgole
df['HPO_IDs'] = df['HPO_IDs'].str.replace(r"(?<!\,)\s+(?!\,)", r",", regex=True)

# Rimuovi righe vuote nella colonna "Documento" per maggiore leggibilità
df = df[df['Documento'].str.strip().astype(bool)]


def sostituisci_nome_paziente(testo, lista_nomi_maschili, lista_nomi_femminili, ospedali_medici):
    if isinstance(testo, str):  # Verifica che il valore sia una stringa
        # Trova la posizione di "Patient" nel testo
        if "Patient" in testo:
            start_pos = testo.find("Patient:") + len("Patient:")  # Inizio del nome
            end_pos = testo.find("\n", start_pos)  # Trova la fine del nome (o nuova riga)
            if end_pos == -1:
                end_pos = len(testo)  # Se non c'è una nuova riga, il nome arriva fino alla fine del testo

            # Estrai il nome del paziente
            nome_paziente_esistente = testo[start_pos:end_pos].strip()

            # Controlla il genere basandosi sul nome specifico
            if nome_paziente_esistente == "Ana García":
                nome_paziente_nuovo = f"{random.choice(lista_nomi_femminili)} {random.choice(cognomi_lista)}"
            elif nome_paziente_esistente == "Ana García Pérez":
                nome_paziente_nuovo = f"{random.choice(lista_nomi_femminili)} {random.choice(cognomi_lista)}"
            elif nome_paziente_esistente == "Ana García López":
                nome_paziente_nuovo = f"{random.choice(lista_nomi_femminili)} {random.choice(cognomi_lista)}"
            elif nome_paziente_esistente == "Juan Pérez":
                nome_paziente_nuovo = f"{random.choice(lista_nomi_maschili)} {random.choice(cognomi_lista)}"
            else:
                # Se il nome non corrisponde, usa parole chiave per determinare il genere
                if any(keyword in testo.lower() for keyword in ["female", "woman", "ova", "ovarian", "vagina"]):
                    nome_paziente_nuovo = f"{random.choice(lista_nomi_femminili)} {random.choice(cognomi_lista)}"
                elif any(keyword in testo.lower() for keyword in ["male", "testicular", "scrotus", "penis"]):
                    nome_paziente_nuovo = f"{random.choice(lista_nomi_maschili)} {random.choice(cognomi_lista)}"
                else:
                    # Se non ci sono parole chiave, scegli un nome maschile di default
                    nome_paziente_nuovo = f"{random.choice(lista_nomi_maschili)} {random.choice(cognomi_lista)}"

            # Sostituisci il nome esistente con un nuovo nome dalla lista
            testo = testo[:start_pos] + " " + nome_paziente_nuovo + testo[end_pos:]

        else:
            # Se "Patient" non è presente, aggiungilo all'inizio con un nome casuale
            if any(keyword in testo.lower() for keyword in ["female", "woman", "ova", "ovarian", "vagina"]):
                nome_paziente_nuovo = f"{random.choice(lista_nomi_femminili)} {random.choice(cognomi_lista)}"
            else:
                nome_paziente_nuovo = f"{random.choice(lista_nomi_maschili)} {random.choice(cognomi_lista)}"

            testo = f"Patient: {nome_paziente_nuovo}\n" + testo

        # Aggiungi ospedale e medico
        ospedale_random = random.choice(list(ospedali_medici.keys()))  # Scegli un ospedale casuale
        medico_random = random.choice(ospedali_medici[ospedale_random])  # Scegli un medico casuale per quell'ospedale
        testo = f"Hospital: {ospedale_random}\nDoctor: {medico_random}\n" + testo

        return testo  # Restituisci il testo modificato
    return testo  # Se non è una stringa, restituisci il testo originale


# Applica la funzione alla colonna "Documento"
df['Documento'] = df['Documento'].apply(sostituisci_nome_paziente, lista_nomi_maschili=nomi_maschili_lista, lista_nomi_femminili=nomi_femminili_lista, ospedali_medici=ospedali_medici)

#generalizzazione dei report eliminando identificatori dei report importanti e nomi  già presenti
frasi_da_rimuovere = [
    "Physical examination:", 
    "Diagnostic impression:", 
    "Central University Hospital",
    "Dr. Ana López, ",
    "Dr. Javier López, ",
    "Dr. Ana López",
    "Dr. Javier López",
    "López",
    "Signature",
    "Signed",
    "Treatment:",
    "Background:",
    "Patient background",
    "Diagnosis",
    "Medical history",
    "Clinical findings",
    "Reason for Consultation",
    "Personal History",
    "Physical Examination",
    "Diagnostic Impression",
    "García Pérez",
    "Central University Hospital",
    "Juan Perez",
    "Juan Pérez,",
    "Juan Pérez",
    "Ana García López",
    "Mr. Juan Pérez",
    "Juan's",
    "Name Juan Pérez",
    "San Juan University Hospital",
    "Diagnostic plan",
    "Juan",
    "Garcia's ",
    "Garcia",
    "Pérez",

    "Ana García",
    "Dr. Martínez"
]

# Funzione per rimuovere le frasi e compattare il testo
def pulisci_frasi(text, frasi):
    if isinstance(text, str):  # Verifica che il valore sia una stringa
        for frase in frasi:
            text = text.replace(frase, "")  # Rimuove la frase specificata
        # Elimina righe vuote e compatta il testo
        #text = " ".join([line.strip() for line in text.split("\n") if line.strip()])
        return text.strip()  # Rimuove eventuali spazi iniziali o finali
    return text  # Se non è una stringa, restituisce il testo originale

# Applica la funzione alla colonna "Documento"
df['Documento'] = df['Documento'].apply(pulisci_frasi, frasi=frasi_da_rimuovere)
df['Documento'] = df['Documento'].str.replace(":", "", regex=False)



df.to_csv(r"C:\Users\Amorl\Desktop\progetto\DatasetOrdinato.csv", index=False)
# Randomizzazione Righe, commentare la riga sottostante per non randomizzare
df= df.sample(frac=1).reset_index(drop=True)
df.to_csv(r"C:\Users\Amorl\Desktop\progetto\Dataset.csv", index=False)
print("File finale salvato con successo!")