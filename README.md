
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

For graphics generation:
```bash
pip install matplotlib
pip install obonet
```

`hp.opo` is also required.

https://hpo.jax.org/data/ontology

## Usage

### Folder Structure

- The folder contains Python scripts that process and analyze data.
- The input and output CSV files are located in the `output` folder.

### Save and Translate
Users who don't need to translate or merge datasets can skip this section.

- **`savedatabase.py`**: Saves the dataset needed for further operations.*produce dataset1.csv dataset2.csv*
- **`translate10x.py`**: Translates a specific dataset (translates 10 rows to English per cycle).
- **`mergedataset.py`**: Merges two datasets and unifies them into a single dataset.



After running these 3 programs, you will have a single dataset named `starting_dataset`.

### Dataset Customization
If you already have the desired dataset, skip this section.

- **`dataset_customization.py`**: Customizes the dataset and generates two results: one ordered and one unordered.

### HPO Operations
You must use a dataset with the following structure:

| HPO_IDs   | Documento |
|-----------|-----------|
| Hpo1,hpo2 | med_report|

The following operations are specific to datasets structured like this.

- **`countstartinghpo.py`**: Counts how many times each HPO code appears in the dataset.
- **`CountExtension.py`**: Displays the hierarchy of the codes.
- **`CountTotalHpo.py`**: Counts each code, making the count value for itself and its parent codes.

### HPO Hierarchy
- **`completehierarchy.py`**: Organizes the HPO hierarchy into a CSV file.
- **`completehierarchy_from118.py`**: Organizes the HPO hierarchy with a maximum parent code of `HP:0000118` into a CSV file.
- **`truedepthcalc.py`**: Organizes the hierarchy in a table with depth values (depth 0 represents the root, or code `HP:0000001`, while depth 15 is the maximum phenotype specification in HPO).
- **`depthfrom118.py`**: Organizes the hierarchy into a table with depth values (depth 0 is the new root `HP:0000118`, depth 13 is now the maximum depth).

### Graphics Creation & Data Representation
- **`create_graphs.py`**: Excludes codes `HP:0000001` and `HP:0000118`, and represents all other HPO codes in multi-graphs stored in the `bar_charts` directory. This script will ask for the desired depth to create graphs (review may be needed).

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
- **`csvcreator_finale.py`**: Matches the codes from the CTWEdge combination with the reports in your dataset.

## Input & Outputs

| Script name   | Inputs | Outputs   |
|-----------|-----------|-----------|
| **savedatabase.py** | | dataset1.csv <br> dataset2.csv | 
| **translate10x.py** | dataset1.csv| dataset1_translated.csv | 
| **mergedataset.py** | dataset1_translated.csv <br> dataset2.csv| starting_dataset | 
| **dataset_customization.py** | starting_dataset.csv| ordered_dataset.csv <br>notordered_dataset.csv | 
| **countstartinghpo.py** | ordered_dataset.csv| hpo_counts.csv | 
| **CountExtension.py** | hpo_counts.csv hp.obo| output_hierarchy.csv | 
| **completehierarchy.py** | hp.obo| completehpohierarchy.csv| 
| **completehierarchy_from118.py** | hp.obo| completehpohierarchy_from118.csv|
| **truedepthcalc.py** | completehpohierarchy.csv| true_depth.csv|
| **depthfrom118.py** | completehpohierarchy.csv| true_depth_from118.csv|
| **create_graphs.py** | true_depth.csv <br>total_counts.csv <br>hp.obo| bar_charts|
| **zeroremoval.py.py** | true_depth_from118.csv <br>completehpohierarchy_from118.csv | true_depth_from118_cleaned.csv <br>completehpohierarchy_from118_cleaned.csv|
| **createctwedgenozero.py** | true_depth_from118_cleaned.csv completehpohierarchy_from118_cleaned.csv| test.ctw|
| **CTWEDGE EXECUTION** | test.ctw | codes.csv|
| **codectwformatting.py** |code.csv| formatted_code.csv|
| **addingparentstodataset.py** | ordered_dataset.csv completehpohierarchy.csv| ordered_dataset_withparents.csv|
| **csvcreator_finale.py** | formatted_codes.csv ordered_dataset_withparents.csv| output_data_matches output_data_no_matches output_data_exact_matches|


## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss the proposed changes.

Please ensure to update the tests as appropriate.

## License

[Insert License Information Here]