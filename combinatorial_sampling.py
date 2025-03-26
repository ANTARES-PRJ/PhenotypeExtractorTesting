import pandas as pd
import numpy as np

test_suite_file = "output/HPO-t2.csv"
test_suite_file_cleaned = "output/HPO-t2-cleaned.csv"

def remove_duplicates(filename):
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


if __name__ == "__main__":
    # After having generated a test suite, we need to extract test cases from our datasets
    # ....
    # First, remove duplicate rows (i.e., rows with the same values in all columns but in different order)
    remove_duplicates(test_suite_file)
    