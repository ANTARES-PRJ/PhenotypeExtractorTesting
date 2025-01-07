#libreria panda utilizzata per dataset,conversione csv
import pandas as pd 
#sottomodello di deep_translator che contiene diversi traduttori, quello scelto per questo progetto è GoogleTranslator
from deep_translator import GoogleTranslator
#gestione del file sistem utilizzata per la verifica di esistenza di un file
import os 

# Configura il traduttore e scelta dei parametri da passare a google translate
translator = GoogleTranslator(source='auto', target='en')

# File di input e output
input_file = r"C:\Users\Amorl\Desktop\progetto\original.csv"  # Sostituisci con il percorso del file da tradurre
output_file = r"C:\Users\Amorl\Desktop\progetto\file_tradotto10x.csv" # File tradotto finale

# Controlla se il file di output esiste già
if os.path.exists(output_file):
    # Carica i progressi esistenti
    df_output = pd.read_csv(output_file)
    #restituisce il numero di righe del file già tradotte, ovvero quelle aggiunte al file di output
    righe_tradotte = len(df_output)
else:
    # Crea un nuovo DataFrame per il file tradotto
    df_output = pd.DataFrame()
    righe_tradotte = 0

# Carica il file di input già stato tradotto in precedenza con panda da parquet a csv 
#df = pd.read_parquet('filename.parquet')
#df.to_csv('filename.csv')
df_input = pd.read_csv(input_file)

# Itera sulle righe del file di input partendo dalla riga già tradotta
#batch_size numero di righe in contemporanea
batch_size = 10
#partendo da righe_tradotte e procede fino alla fine del file (len)
for start_index in range(righe_tradotte, len(df_input), batch_size):
    end_index = min(start_index + batch_size, len(df_input))
    #Metodo di Pandas per selezionare righe e colonne in base alla posizione (indice numerico).
    batch = df_input.iloc[start_index:end_index]

    batch_tradotto = []
    for _, riga in batch.iterrows():
        # Ottieni la riga corrente come dizionario
        riga = riga.to_dict()

        # Traduce ogni colonna (salta colonne non stringhe)
        riga_tradotta = {}
        for colonna, valore in riga.items():
            if isinstance(valore, str):  # Traduci solo se è una stringa
                try:
                    riga_tradotta[colonna] = translator.translate(valore)
                except Exception as e:
                    print(f"Errore durante la traduzione della colonna '{colonna}' alla riga {start_index}: {e}")
                    riga_tradotta[colonna] = valore  # Mantieni il testo originale in caso di errore
            else:
                riga_tradotta[colonna] = valore  # Mantieni il testo originale in caso di errore
        #Ogni riga tradotta viene aggiunta a batch_tradotto
        batch_tradotto.append(riga_tradotta)

    # Aggiungi le righe tradotte al DataFrame di output
    df_output = pd.concat([df_output, pd.DataFrame(batch_tradotto)], ignore_index=True)

    # Salva immediatamente il file aggiornato
    df_output.to_csv(output_file, index=False)
    print(f"Righe {start_index + 1} - {end_index} tradotte e salvate.")

print("Traduzione completata!")