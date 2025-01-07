import pandas as pd
from deep_translator import GoogleTranslator
import os

# Configura il traduttore
translator = GoogleTranslator(source='auto', target='en')

# File di input e output
input_file = r"C:\Users\Amorl\Desktop\progetto\original.csv" # Sostituisci con il nome del tuo file
output_file = r"C:\Users\Amorl\Desktop\progetto\file_tradotto.csv"


# Controlla se il file di output esiste già
if os.path.exists(output_file):
    # Carica i progressi esistenti
    df_output = pd.read_csv(output_file)
    righe_tradotte = len(df_output)
else:
    # Crea un nuovo DataFrame per il file tradotto
    df_output = pd.DataFrame()
    righe_tradotte = 0

# Carica il file di input
df_input = pd.read_csv(input_file)

# Itera sulle righe del file di input partendo dalla riga già tradotta
for index in range(righe_tradotte, len(df_input)):
    # Ottieni la riga corrente come dizionario
    riga = df_input.iloc[index].to_dict()
    
    # Traduce ogni colonna (salta colonne non stringhe)
    riga_tradotta = {}
    for colonna, valore in riga.items():
        if isinstance(valore, str):  # Traduci solo se è una stringa
            try:
                riga_tradotta[colonna] = translator.translate(valore)
            except Exception as e:
                print(f"Errore durante la traduzione della colonna '{colonna}' alla riga {index}: {e}")
                riga_tradotta[colonna] = valore  # Mantieni il testo originale in caso di errore
        else:
            riga_tradotta[colonna] = valore  # Copia valori non stringa direttamente
    
    # Aggiungi la riga tradotta al DataFrame di output
    df_output = pd.concat([df_output, pd.DataFrame([riga_tradotta])], ignore_index=True)
    
    # Salva immediatamente il file aggiornato
    df_output.to_csv(output_file, index=False)
    print(f"Riga {index + 1} tradotta e salvata.")

print("Traduzione completata!")