import pandas as pd
import os

# Define output directories
base_dir = os.path.dirname(os.path.realpath(__file__)) 
output_dir = os.path.join(base_dir, "output")

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Define file paths
file1_path = os.path.join(output_dir, "dataset1_translated.csv")
file2_path = os.path.join(output_dir, "dataset2.csv")
final_output_path = os.path.join(output_dir, "starting_dataset.csv")

# Load the two CSV files
df1 = pd.read_csv(file1_path)  # First CSV file
df2 = pd.read_csv(file2_path)  # Second CSV file

# Create a new 'Documento' column by merging 'Clinical case'
df2['Documento'] = df2['Clinical case']

# Select only the 'HPO_IDs' and 'Document' columns from both DataFrames
df1_selected = df1[['HPO_IDs', 'Documento']]
df2_selected = df2[['HPO_IDs', 'Documento']]

# Concatenate the two DataFrames
df_merged = pd.concat([df1_selected, df2_selected], ignore_index=True)

# Save the final merged file
df_merged.to_csv(final_output_path, index=False)
print("Final merged file saved successfully in output folder!")
