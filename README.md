
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

For scripts operating on the HPO ontology:
```bash
pip install pronto
```

`hp.obo` is also required. You can download it from the following link: [https://hpo.jax.org/data/ontology](https://hpo.jax.org/data/ontology)

## Usage

### Folder Structure

- The folder contains Python scripts that process and analyze data.
- The CSV files are located in the `output` folder.
- The `utils` folder contains utility python scripts.

### Dataset Preparation
This replication package already contains the resulting datasets. Thus, users who don't need to translate or merge datasets can skip this section.

- **`save_and_prepare_database.py`**: It saves the dataset needed for further operations. Then, it translates a specific dataset (translates 10 rows to English per cycle), and merges the two datasets into a single file. It also customizes the dataset by adding different names for patients, physicians, and hospitals.

After running this program, you will have a dataset named `merged_dataset.csv` and one named `merged_dataset_with_parents.csv` containing also parent codes.
The functionalities of `save_and_prepare_database.py` exploits the file `names.py` which contains the names of patients, physicians, and hospitals.

### IPM Creation

- **`generate_ipm.py`**: It generates the IPM, for a given depth and number of parameters. The IPM is saved in a file named `test.ctw`, in CTWedge format, and `hpo.acts` in the format compatible with CAgen.

### Combinatorial sampling

- **`combinatorial_sampling.py`**: It generates the file `2wise_test_suite.csv` which contains the real test cases to be executed against the LLM.








### HPO Hierarchy
- **`completehierarchy_from118.py`**: Organizes the HPO hierarchy with a maximum parent code of `HP:0000118` into a CSV file.

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
| **depthfrom118.py** | completehpohierarchy.csv| true_depth_from118.csv|
| **CTWEDGE EXECUTION** | test.ctw | codes.csv|
| **codectwformatting.py** |code.csv| formatted_code.csv|
| **find_best_match.py** | formatted_codes.csv ordered_dataset_withparents.csv completehpohierarchy.csv| output_data_matches output_data_no_matches output_data_exact_matches|


## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss the proposed changes.

Please ensure to update the tests as appropriate.

## License

[Insert License Information Here]