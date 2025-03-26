
# Combin-AADA

Combin-AADA is a Python project designed to create a HPO (Human Phenotype Ontology) test model using Python, CTWEdge, and CAgen, starting from databases.

## Requirements

Before running the scripts, install the following dependencies:

For the Majority of programs operating with csv:
```bash
pip install pandas
```
For translation:
```bash
pip install deep_translator
```

`hp.obo` is also required. You can download it from the following link: [https://hpo.jax.org/data/ontology](https://hpo.jax.org/data/ontology)

## Usage

### Folder Structure

- The folder contains Python scripts that process and analyze data.
- The input and output CSV files are located in the `output` folder.

### Dataset Preparation
Users who don't need to translate or merge datasets can skip this section.

- **`save_and_prepare_database.py`**: Saves the dataset needed for further operations. Then, it translates a specific dataset (translates 10 rows to English per cycle), and merges the two datasets into a single file. It also customizes the dataset by adding different names for patients, physicians, and hospitals.

After running this program, you will have a single dataset named `merged_dataset.,csv`.
The functionalities of `save_and_prepare_database.py` exploits the file `names.py` which contains the names of patients, physicians, and hospitals.

### HPO Hierarchy
- **`completehierarchy.py`**: Organizes the HPO hierarchy into a CSV file.
- **`completehierarchy_from118.py`**: Organizes the HPO hierarchy with a maximum parent code of `HP:0000118` into a CSV file.
- **`truedepthcalc.py`**: Organizes the hierarchy in a table with depth values (depth 0 represents the root, or code `HP:0000001`, while depth 15 is the maximum phenotype specification in HPO).
- **`depthfrom118.py`**: Organizes the hierarchy into a table with depth values (depth 0 is the new root `HP:0000118`, depth 13 is now the maximum depth).

### CTWEdge Input Creation
- **`zeroremoval.py`**: Removes all zeros from the hierarchy and depth to generate reduced-length CTWEdge files.
- **`createctwedgenozero.py`**: Creates CTWEdge input files without `HP:+` and all zeros, while preserving hierarchy constraints and handling `NULL` values.

### CTWEdge Execution
- Execute CTWEdge on the generated input files and save the result as `code.csv`.

### Code Formatting
- **`codectwformatting.py`**: Formats the codes by converting the abbreviated form `HP:0000001` in the `code.csv` file (input required).

### Extraction of Matching Combinations
- **`addingparentstodataset.py`**: Adds parent codes to their children in the ordered dataset and stores the result in a new column.

### Association
- **`csvcreator_finale.py`**: Matches the codes from the CTWEdge combination with all the corresponding reports in your dataset.
- **`find_best_match.py`**:Matches the code from the CTWEdge combination with the best corresponding report in your dataset.
- **`from_ctw_to_acts.py`**translate from ctw to acts specifically for ctw hpo


## Input & Outputs

| Script name   | Inputs | Outputs   |
|-----------|-----------|-----------|
| **save_and_prepare_database.py** | | merged_dataset.csv | 
| **completehierarchy.py** | hp.obo| completehpohierarchy.csv| 
| **completehierarchy_from118.py** | hp.obo| completehpohierarchy_from118.csv|
| **truedepthcalc.py** | completehpohierarchy.csv| true_depth.csv|
| **depthfrom118.py** | completehpohierarchy.csv| true_depth_from118.csv|
| **zeroremoval.py.py** | true_depth_from118.csv <br>completehpohierarchy_from118.csv | true_depth_from118_cleaned.csv <br>completehpohierarchy_from118_cleaned.csv|
| **createctwedgenozero.py** | true_depth_from118_cleaned.csv completehpohierarchy_from118_cleaned.csv| test.ctw|
| **CTWEDGE EXECUTION** | test.ctw | codes.csv|
| **codectwformatting.py** |code.csv| formatted_code.csv|
| **addingparentstodataset.py** | ordered_dataset.csv completehpohierarchy.csv| ordered_dataset_withparents.csv|
| **csvcreator_finale.py** | formatted_codes.csv ordered_dataset_withparents.csv| output_data_matches output_data_no_matches output_data_exact_matches|
| **find_best_match.py** | formatted_codes.csv ordered_dataset_withparents.csv completehpohierarchy.csv| output_data_matches output_data_no_matches output_data_exact_matches|


## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss the proposed changes.

Please ensure to update the tests as appropriate.

## License

[Insert License Information Here]