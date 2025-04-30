import os
from pathlib import Path
import pandas as pd
from deep_translator import GoogleTranslator
from utils.ontology_depth import get_parents
import random
import re
import ast
from utils.names import male_names_list, female_names_list, hospital_physicians, surname_list, escape_sentences

res_dataset = "merged_dataset.csv"
res_dataset_parent = "merged_dataset_with_parent.csv"
dataset_1 = "synthetic_clinical_cases.csv"
dataset_1_translated = "synthetic_clinical_cases_translated.csv"
dataset_2 = "clinical_case_symptoms_diseases_dataset.csv"
output_folder = "output"

def change_patient_name(text):
    """
    Modifies the patient name and adds hospital and physician information to the given text.
    This function identifies and replaces the patient name in the provided text with a randomly 
    generated name based on gender-related keywords or existing patient names. If no patient 
    name is found, it adds a new patient name. Additionally, it prepends the text with randomly 
    selected hospital and physician information.
    Args:
        text (str): The input text containing patient information.
    Returns:
        str: The modified text with updated patient name, hospital, and physician details.
    Notes:
        - The function uses predefined lists `female_names_list`, `male_names_list`, and 
          `surname_list` for generating random names.
        - The `hospital_physicians` dictionary is used to select random hospital and physician 
          information.
        - If the input is not a string, it is returned unchanged.
    """
    if isinstance(text, str):
        if "Patient" in text:
            start_pos = text.find("Patient:") + len("Patient:")
            end_pos = text.find("\n", start_pos)
            if end_pos == -1:
                end_pos = len(text)
            existing_patient = text[start_pos:end_pos].strip()

            if existing_patient in ["Ana García", "Ana García Pérez", "Ana García López"]:
                new_patient = f"{random.choice(female_names_list)} {random.choice(surname_list)}"
            elif existing_patient == "Juan Pérez":
                new_patient = f"{random.choice(male_names_list)} {random.choice(surname_list)}"
            else:
                if any(keyword in text.lower() for keyword in ["female", "woman", "ova", "ovarian", "vagina"]):
                    new_patient = f"{random.choice(female_names_list)} {random.choice(surname_list)}"
                elif any(keyword in text.lower() for keyword in ["male", "testicular", "scrotus", "penis"]):
                    new_patient = f"{random.choice(male_names_list)} {random.choice(surname_list)}"
                else:
                    new_patient = f"{random.choice(male_names_list)} {random.choice(surname_list)}"

            text = text[:start_pos] + " " + new_patient + text[end_pos:]
        else:
            if any(keyword in text.lower() for keyword in ["female", "woman", "ova", "ovarian", "vagina"]):
                new_patient = f"{random.choice(female_names_list)} {random.choice(surname_list)}"
            else:
                new_patient = f"{random.choice(male_names_list)} {random.choice(surname_list)}"

            text = f"Patient: {new_patient}\n" + text

        random_hospital = random.choice(list(hospital_physicians.keys()))
        random_physician = random.choice(hospital_physicians[random_hospital])
        text = f"Hospital: {random_hospital}\nDoctor: {random_physician}\n" + text

        return text
    
    return text

def clean_header(text, start_marker="Reason for consultation", alternative_marker="Medical History", end_marker="Signature", end_marker2="Dr.", sex_marker=["SexMale", "SexFemale"]):
    """
    Cleans and extracts relevant content from a medical text header.
    This function processes a given text by removing unwanted sections based on 
    specified markers and extracts patient and specialty information if available.
    Args:
        text (str): The input text to be cleaned and processed.
        start_marker (str, optional): The primary marker indicating the start of the 
            relevant content. Defaults to "Reason for consultation".
        alternative_marker (str, optional): An alternative marker indicating the start 
            of the relevant content. Defaults to "Medical History".
        end_marker (str, optional): The marker indicating the end of the relevant content. 
            Defaults to "Signature".
        end_marker2 (str, optional): An additional marker indicating the end of the relevant 
            content. Defaults to "Dr.".
        sex_marker (list, optional): A list of markers used to identify and remove sex-related 
            information from the text. Defaults to ["SexMale", "SexFemale"].
    Returns:
        str: The cleaned text with the extracted header information (specialty and patient name, 
        if available) followed by the relevant content.
    """
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

def clean_hpo_ids(valore):
    """
    Cleans a given HPO (Human Phenotype Ontology) ID string by removing square brackets,
    single quotes, and leading/trailing whitespace.

    Args:
        valore (str): The input value to be cleaned. If not a string, the value is returned as-is.

    Returns:
        str: The cleaned HPO ID string if the input is a string.
        Any: The original value if the input is not a string.
    """
    if isinstance(valore, str):
        return valore.replace("[", "").replace("]", "").replace("'", "").strip()
    return valore

def clean_sentences(text, sentences):
    """
    Removes specified sentences from the given text and returns the cleaned text.

    Args:
        text (str): The input text from which sentences will be removed.
        sentences (list of str): A list of sentences to be removed from the text.

    Returns:
        str: The cleaned text with specified sentences removed and leading/trailing whitespace stripped.
             If the input `text` is not a string, it is returned unchanged.
    """
    if isinstance(text, str):
        for sentence in sentences:
            text = text.replace(sentence, "")
        return text.strip()
    return text

def customize_dataset(output_folder, dataset_file):
    """
    Customizes a dataset by cleaning and modifying its content, then saves the updated dataset.
    Args:
        output_folder (str): The name of the folder where the customized dataset will be saved.
        dataset_file (str): The name of the dataset file to be processed.
    Functionality:
        - Creates the output folder if it does not exist.
        - Reads the dataset file from the specified output folder.
        - Cleans the "Document" column by removing headers and modifying patient names.
        - Cleans the "HPO_IDs" column by removing invalid entries and formatting the content.
        - Removes sentences from the "Document" column based on specific criteria.
        - Saves the customized dataset back to the output folder.
    Raises:
        FileNotFoundError: If the input dataset file does not exist.
        KeyError: If required columns ("Document", "HPO_IDs") are missing in the dataset.
        Exception: For any other issues encountered during processing.
    Returns:
        None
    """
    # Get the folders
    base_dir = os.path.dirname(os.path.realpath(__file__))
    output_dir = os.path.join(base_dir, output_folder)
    os.makedirs(output_dir, exist_ok=True)

    # Get dataset file
    input_file = os.path.join(output_dir, dataset_file)
    output_file1 = os.path.join(output_dir, dataset_file)
    df = pd.read_csv(input_file)

    # Clean the header in medical reports and HPO_IDs column
    df["Document"] = df["Document"].apply(clean_header)
    df['HPO_IDs'] = df['HPO_IDs'].apply(clean_hpo_ids)
    df = df[df['HPO_IDs'].str.strip().astype(bool)]
    df['HPO_IDs'] = df['HPO_IDs'].str.replace(r"(?<!\,)\s+(?!\,)", r",", regex=True)
    df = df[df['Document'].str.strip().astype(bool)]   

    # Modify patient name
    df['Document'] = df['Document'].apply(lambda x: change_patient_name(x))
    
    # Remove sentences
    df['Document'] = df['Document'].apply(lambda x: clean_sentences(x, escape_sentences))
    df['Document'] = df['Document'].str.replace(":", "", regex=False)

    # Salvataggio file
    df.to_csv(output_file1, index=False)
    print("Customized dataset saved successfully")


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
                if isinstance(value, str) and column != "HPO_IDs":   # Translate only if it's a string
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
    df1 = df1.rename(columns={"Documento": "Document"})
    df1_selected = df1[['HPO_IDs', 'Document']]
    df2_selected = df2[['HPO_IDs', 'Document']]

    # Concatenate the two DataFrames
    df_merged = pd.concat([df1_selected, df2_selected], ignore_index=True)

    # Save the final merged file
    df_merged.to_csv(final_output_path, index=False)
    print("Final merged file saved successfully in output folder!")



def fix_serialized_list_string(s):
    """
    Fixes a serialized list string by ensuring proper formatting and escaping.
    Args:
        s (str): The input string to be fixed.
    Returns:
        str: The fixed string with proper formatting.
    """
    try:
        # Safely evaluate the string into a Python list
        parsed = ast.literal_eval(s)
    except (ValueError, SyntaxError):
        return s  # Return as-is if parsing fails

    # Handle case like: ["HP:0007335,HP:0003892,..."]
    if isinstance(parsed, list) and len(parsed) == 1 and isinstance(parsed[0], str) and ',' in parsed[0]:
        elements = parsed[0].split(',')
    elif isinstance(parsed, list):
        elements = parsed
    else:
        return s

    # Add single quotes around each element and join with commas
    return ",".join(f"'{el.strip()}'" for el in elements)


def quote_subterms(s):
    """"
    Quotes each term in a comma-separated string.
    Args:
        s (str): The input string containing comma-separated terms.
    Returns:
        str: The string with each term quoted.
    """
    return ",".join(f"'{term.strip()}'" for term in s.split(","))


def add_parents_to_dataset(folder, input_dataset, output_dataset):
    """
    Adds a column of parent HPO (Human Phenotype Ontology) codes to a dataset.

    This function reads a CSV file containing HPO codes, computes the parent 
    HPO codes for each entry using the `get_parents` function, and inserts 
    them as a new column in the dataset. The updated dataset is then saved 
    to a new CSV file.

    Args:
        folder (str): The folder path where the input and output datasets are located.
        input_dataset (str): The name of the input CSV file containing the dataset.
        output_dataset (str): The name of the output CSV file to save the updated dataset.

    Returns:
        None

    Side Effects:
        - Reads the input dataset from the specified folder.
        - Writes the updated dataset with the new column to the output file.
        - Prints a confirmation message upon successful update.

    Note:
        The `get_parents` function must be defined elsewhere in the codebase. It is 
        expected to take an HPO code as input and return its parent HPO codes.
    """
    dataset_input = os.path.join(folder, input_dataset)
    dataset_output = os.path.join(folder, output_dataset)
    df = pd.read_csv(dataset_input)

    df.insert(1, 'Parent_HPO_Codes', df[df.columns[0]].astype(str).apply(get_parents))
    # Remove all new lines in each column of df
    df = df.replace(r'\n', ' ', regex=True)
    # Remove all double spaces in each column of df
    df = df.replace(r'\s+', ' ', regex=True)
    
    # Fix the HPO_IDs column
    df['HPO_IDs'] = df['HPO_IDs'].str.replace("' '", "','")
    df['HPO_IDs'] = df['HPO_IDs'].apply(fix_serialized_list_string)

    # Fix the Parent_HPO_Codes column
    df['Parent_HPO_Codes'] = df['Parent_HPO_Codes'].apply(quote_subterms)

    df.to_csv(dataset_output, index=False)
    print("Dataset File is Updated!")

if __name__ == "__main__":
    """ # First, save the databases
    save_database(output_folder)
    
    # Then, translate the database
    translate_database(output_folder, dataset_1, dataset_1_translated)
    
    # Lastly, merge the datasets
    merge_datasets(output_folder, dataset_1_translated, dataset_2, res_dataset)
    
    # Remove files created during the process
    os.remove(os.path.join(output_folder, dataset_1))
    os.remove(os.path.join(output_folder, dataset_1_translated))
    os.remove(os.path.join(output_folder, dataset_2))
    print("Files cleaned successfully") """

    # Create a new dataset with parent codes
    add_parents_to_dataset(output_folder, res_dataset, res_dataset_parent)







