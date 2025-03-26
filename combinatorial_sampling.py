import pandas as pd
import numpy as np
import os

output_folder = "output"
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_folder)
test_suite_file = "HPO-t2.csv"
test_suite_file_cleaned = "HPO-t2-cleaned.csv"
test_suite_file_formatted = "HPO-t2-formatted.csv"
script_dir = os.path.dirname(os.path.abspath(__file__))

def remove_duplicates(filename, test_suite_file, test_suite_file_cleaned):
    """
    Removes duplicate rows from a CSV file after sorting the values in each row.

    Args:
        filename (str): The path to the CSV file to process.

    Returns:
        None: The function saves the cleaned CSV file with duplicates removed
        and prints a success message.

    Notes:
        - All values in the DataFrame are treated as strings.
        - The values in each row are sorted before checking for duplicates.
        - The cleaned file overwrites the original file.
    """
    # Load the CSV file. All values are string
    df = pd.read_csv(test_suite_file,dtype=str)
    df = df.astype(str)

    # Sort the values in each row while keeping the DataFrame structure and drop duplicates
    df_sorted = pd.DataFrame(np.sort(df.values, axis=1), columns=df.columns)
    df_unique = df_sorted.drop_duplicates()

    # Save the cleaned file
    df_unique.to_csv(test_suite_file_cleaned, index=False)

    print("Duplicates removed successfully!")

def format_code(code):
    """
    Formats a given code string into the standardized "HP:#######" format.
    Args:
        code (str): The input code to be formatted. It can be in various forms, 
                    including already formatted, missing a colon, or containing 
                    non-numeric characters.
    Returns:
        str or None: The formatted code in the "HP:#######" format if valid, 
                     or None if the input is empty, "null", or cannot be formatted.
    Examples:
        - "HP:0001234" -> "HP:0001234" (already formatted)
        - "HP0001234" -> "HP:0001234" (adds missing colon)
        - "1234" -> "HP:0001234" (pads numeric part to 7 digits)
        - "null" -> None (invalid input)
        - "" -> None (empty input)
    """
    code = str(code).strip()
    if code in ["", "null"]:
        return None  # Null codes are removed
    
    if code.startswith("HP:") and len(code) == 10 and code[3:].isdigit():
        return code  # The code is already formatted correctly
    
    if code.startswith("HP") and len(code) == 9 and code[2:].isdigit():
        return f"HP:{code[2:]}"  # Adds the colon if missing
    
    numeric_part = ''.join(filter(str.isdigit, code)).zfill(7)
    return f"HP:{numeric_part}" if numeric_part else None

def remove_hp_0000000(df):
    """
    Cleans a DataFrame by removing rows and columns that are entirely NaN, 
    and treating cells with the value 'HP:0000000' as NaN.
    Parameters:
    df (pandas.DataFrame): The input DataFrame to be cleaned.
    Returns:
    pandas.DataFrame: A cleaned DataFrame with rows and columns containing 
    only NaN values removed, and 'HP:0000000' treated as NaN.
    """
    df_cleaned = df.dropna(how='all', axis=0).dropna(how='all', axis=1)  # Remove rows with only NaN on all axis
    
    # Cells with 'HP:0000000' are considered as NaN
    df_cleaned = df_cleaned.applymap(lambda x: None if x == "HP:0000000" else x)
    df_cleaned = df_cleaned.dropna(how='all', axis=0).dropna(how='all', axis=1)  # Remove rows with only NaN on all axis

    return df_cleaned

def save_formatted_codes(input_file, output_file):
    """
    Reads a CSV file containing codes, formats the codes, removes invalid entries, 
    and saves the formatted codes to a new CSV file.
    Args:
        input_file (str): Path to the input CSV file. The file should not have a header, 
                          and the first row will be skipped during processing.
        output_file (str): Path to the output CSV file where the formatted codes will be saved.
    Returns:
        None
    Side Effects:
        - Reads the input CSV file.
        - Applies formatting to the codes using the `format_code` function.
        - Removes invalid codes (e.g., "HP:0000000") using the `remove_hp_0000000` function.
        - Saves the formatted codes to the specified output file.
        - Prints a message indicating the location of the saved file.
    """
    df_codes = pd.read_csv(input_file, header=None, skiprows=1)
    
    # Correctly format codes
    df_codes = df_codes.apply(lambda col: col.map(format_code))
    df_codes = df_codes.apply(lambda row: row.dropna().reset_index(drop=True), axis=1)
    df_codes = remove_hp_0000000(df_codes)
    
    # Save formatted file
    df_codes.to_csv(output_file, index=False, header=False)
    print(f"Formatted test suite saved in: {output_file}")

if __name__ == "__main__":
    output_dir = os.path.join(script_dir, "output")

    input_file = os.path.join(output_dir, test_suite_file)
    output_file = os.path.join(output_dir, test_suite_file_cleaned)
    # After having generated a test suite, we need to extract test cases from our datasets
    # ....
    # First, remove duplicate rows (i.e., rows with the same values in all columns but in different order)
    remove_duplicates(test_suite_file, input_file, output_file)
    
    # Second, format the codes
    input_file = os.path.join(output_dir, test_suite_file_cleaned)
    output_file = os.path.join(output_dir, test_suite_file_formatted)
    save_formatted_codes(input_file, output_file)