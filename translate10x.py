import os
import pandas as pd
from deep_translator import GoogleTranslator

# Configure the translator
translator = GoogleTranslator(source='auto', target='en')

# Get the path of the folder where the script is located
base_dir = os.path.dirname(os.path.realpath(__file__))

# Define input and output file paths
input_file = os.path.join(base_dir, "output", "dataset1.csv")  # Input file in the 'output' folder
output_file = os.path.join(base_dir, "output", "dataset1_translated.csv")  # Final translated file in the 'output' folder

# Check if the output file already exists
if os.path.exists(output_file):
    df_output = pd.read_csv(output_file)
    translated_rows = len(df_output)
else:
    df_output = pd.DataFrame()
    translated_rows = 0

# Load the input file
df_input = pd.read_csv(input_file)

# Set batch size
batch_size = 10

# Iterate over the input file rows starting from the already translated row
for start_index in range(translated_rows, len(df_input), batch_size):
    end_index = min(start_index + batch_size, len(df_input))
    batch = df_input.iloc[start_index:end_index]

    translated_batch = []
    for _, row in batch.iterrows():
        row = row.to_dict()

        # Translate each column if the value is a string
        translated_row = {}
        for column, value in row.items():
            if isinstance(value, str):  # Translate only if it's a string
                try:
                    translated_row[column] = translator.translate(value)
                except Exception as e:
                    print(f"Error while translating column '{column}' at row {start_index}: {e}")
                    translated_row[column] = value  # Keep the original text in case of an error
            else:
                translated_row[column] = value  # Keep the original text if it's not a string

        # Add the translated row
        translated_batch.append(translated_row)

    # Append the translated rows to the output DataFrame
    df_output = pd.concat([df_output, pd.DataFrame(translated_batch)], ignore_index=True)

    # Save the updated file
    df_output.to_csv(output_file, index=False)
    print(f"Rows {start_index + 1} - {end_index} translated and saved.")

print("Translation completed!")
