import os
from pathlib import Path
import pandas as pd

# Get the directory where the script is located
base_dir = Path(__file__).resolve().parent
output_dir = base_dir / "output"
output_dir.mkdir(exist_ok=True)  # Create folder if it doesn't exist

# Input file paths
input_file1 = "hf://datasets/biololab/synthetic_clinical_cases/data/train-00000-of-00001.parquet"
input_file2 = "hf://datasets/joseluhf11/clinical_case_symptoms_diseases_dataset/train.csv"

# Output file paths
output_file1 = output_dir / "dataset1.csv"
output_file2 = output_dir / "dataset2.csv"

try:
    # Load data
    df1 = pd.read_parquet(input_file1)
    df2 = pd.read_csv(input_file2)
    
    # Save output files
    df1.to_csv(output_file1, index=False)
    df2.to_csv(output_file2, index=False)
    
    print(f"Data saved successfully as {output_file1} and {output_file2}")
except Exception as e:
    print(f"Error: {e}")
