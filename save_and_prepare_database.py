import os
from pathlib import Path
import pandas as pd
from deep_translator import GoogleTranslator

def save_database(folder):
    """
    Saves specified datasets from remote sources to a local folder in CSV format.
    Args:
        folder (str): The name of the folder where the datasets will be saved. 
                      The folder will be created in the same directory as the script if it doesn't exist.
    Functionality:
        - Downloads a parquet file and a CSV file from remote sources.
        - Converts the parquet file to CSV format.
        - Saves both datasets as CSV files in the specified folder.
    Input Files:
        1. Parquet file: "hf://datasets/biololab/synthetic_clinical_cases/data/train-00000-of-00001.parquet"
        2. CSV file: "hf://datasets/joseluhf11/clinical_case_symptoms_diseases_dataset/train.csv"
    Output Files:
        1. "synthetic_clinical_cases.csv" - Converted from the parquet file.
        2. "clinical_case_symptoms_diseases_dataset.csv" - Copied from the CSV file.
    Raises:
        Exception: If there is an error during file loading or saving, it will print the error message.
    Example:
        save_database("output_folder")
        This will create a folder named "output_folder" in the script's directory and save the datasets there.
    """

    # Get the directory where the script is located
    base_dir = Path(__file__).resolve().parent
    output_dir = base_dir / folder
    output_dir.mkdir(exist_ok=True)  # Create folder if it doesn't exist

    # Input file paths
    input_file1 = "hf://datasets/biololab/synthetic_clinical_cases/data/train-00000-of-00001.parquet"
    input_file2 = "hf://datasets/joseluhf11/clinical_case_symptoms_diseases_dataset/train.csv"

    # Output file paths
    output_file1 = output_dir / "synthetic_clinical_cases.csv"
    output_file2 = output_dir / "clinical_case_symptoms_diseases_dataset.csv"

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

def translate_database(folder, db_file_name, db_file_name_translated):
    """
    Translates the content of a CSV database file into English and saves the translated content to a new file.
    Args:
        folder (str): The folder containing the input and output files.
        db_file_name (str): The name of the input CSV file to be translated.
        db_file_name_translated (str): The name of the output CSV file to save the translated content.
    Returns:
        None
    Notes:
        - The function uses the `GoogleTranslator` to translate text from the source language to English.
        - Translation is performed in batches to handle large files efficiently.
        - If the output file already exists, the function resumes translation from where it left off.
        - Non-string values in the input file are preserved as-is in the output file.
        - Errors during translation of specific rows or columns are logged, and the original text is retained in such cases.
    Raises:
        Exception: If there are issues with file reading, writing, or translation, an exception is logged for the specific row or column.
    Example:
        translate_database(
            folder="data",
            db_file_name="input.csv",
            db_file_name_translated="translated_output.csv"
        )
    """

    # Configure the translator
    translator = GoogleTranslator(source='auto', target='en')

    # Get the path of the folder where the script is located
    base_dir = os.path.dirname(os.path.realpath(__file__))

    # Define input and output file paths
    input_file = os.path.join(base_dir, folder, db_file_name)  # Input file 
    output_file = os.path.join(base_dir, folder, db_file_name_translated)  # Final translated file 

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


def merge_datasets(folder, db1_file_name, db2_file_name, output_file_name):
    """
    Merges two CSV datasets by selecting specific columns and concatenating them into a single file.
    Args:
        folder (str): The name of the folder where the input and output files are located.
        db1_file_name (str): The name of the first CSV file to be merged.
        db2_file_name (str): The name of the second CSV file to be merged.
        output_file_name (str): The name of the output CSV file to save the merged data.
    Returns:
        None
    Side Effects:
        - Ensures the specified output directory exists.
        - Reads the input CSV files from the specified folder.
        - Creates a new 'Document' column in the second dataset based on the 'Clinical case' column.
        - Selects the 'HPO_IDs' and 'Document' columns from both datasets.
        - Concatenates the selected columns from both datasets into a single DataFrame.
        - Saves the merged DataFrame as a new CSV file in the specified folder.
        - Prints a success message upon saving the merged file.
    Raises:
        FileNotFoundError: If any of the input files are not found in the specified folder.
        KeyError: If the required columns ('HPO_IDs', 'Document', or 'Clinical case') are missing in the input files.
    """

    # Define output directories
    base_dir = os.path.dirname(os.path.realpath(__file__)) 
    output_dir = os.path.join(base_dir, folder)

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Define file paths
    file1_path = os.path.join(output_dir, db1_file_name)
    file2_path = os.path.join(output_dir, db2_file_name)
    final_output_path = os.path.join(output_dir, output_file_name)

    # Load the two CSV files
    df1 = pd.read_csv(file1_path)  # First CSV file
    df2 = pd.read_csv(file2_path)  # Second CSV file

    # Create a new 'Document' column by merging 'Clinical case'
    df2['Document'] = df2['Clinical case']

    # Select only the 'HPO_IDs' and 'Document' columns from both DataFrames
    df1_selected = df1[['HPO_IDs', 'Document']]
    df2_selected = df2[['HPO_IDs', 'Document']]

    # Concatenate the two DataFrames
    df_merged = pd.concat([df1_selected, df2_selected], ignore_index=True)

    # Save the final merged file
    df_merged.to_csv(final_output_path, index=False)
    print("Final merged file saved successfully in output folder!")


if __name__ == "__main__":
    # First, save the databases
    save_database(".")
    # Then, translate the database
    translate_database(".", "synthetic_clinical_cases.csv", "synthetic_clinical_cases_translated.csv")
    # Lastly, merge the datasets
    merge_datasets(".", "synthetic_clinical_cases_translated.csv", "clinical_case_symptoms_diseases_dataset.csv", "merged_dataset.csv")
    # Remove files created during the process
    os.remove("synthetic_clinical_cases.csv")
    os.remove("synthetic_clinical_cases_translated.csv")
    os.remove("clinical_case_symptoms_diseases_dataset.csv")
    print("Files cleaned successfully")







