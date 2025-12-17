
# Evaluating an LLM-Based Phenotype Extractor from Medical Reports Using Combinatorial Testing

This is the replication package for the paper "Evaluating an LLM-Based Phenotype Extractor from Medical Reports Using Combinatorial Testing".
The LLM-based phenotype extractor is available at [https://doi.org/10.5281/zenodo.17912782](https://doi.org/10.5281/zenodo.17912782), including all configuration files, scripts, and instructions on how to set up and use the extractor.

## Requirements for this Replication Package

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

The HPO ontology, contained into the file `hp.obo`, is also required, and must be stored under the `utils` directory. 
You can download it from the following link: [https://hpo.jax.org/data/ontology](https://hpo.jax.org/data/ontology)

## Usage

### Folder Structure

- The folder contains Python scripts that process and analyze data.
- The CSV files are located in the `output` folder. The following are the most important ones:
    - `merged_dataset.csv`: the merged dataset containing medical reports and their associated phenotypes.
    - `merged_dataset_with_parents.csv`: the merged dataset containing medical reports and their associated phenotypes, including parent codes.
    - `2wise_test_suite.csv`: the combinatorial test suite generated from the dataset.
- The `utils` folder contains utility python scripts and utility files.
- The `prompts` folder contains the prompts used for the LLM-based phenotype extractor during testing.
- The `results` folder contains the results of the experiments
    - `CombinatorialPromptTesting.xlsx` reports the summary data of the experiments.
    - `summary_*.csv` files contain the output of each test execution.
    - `results_analysis.py` contains the script used to analyze the results and to extract summary values.
- The `test_scripts` folder contains the scripts used to run the LLM-based phenotype extractor on the generated test cases.


### Dataset Preparation
This replication package already contains the resulting datasets (`merged_dataset.csv` and `merged_dataset_with_parents.csv`). Thus, users who don't need to translate or merge datasets can skip this section.

- **`save_and_prepare_database.py`**: It saves the dataset needed for further operations. Then, it translates a specific dataset (translates 10 rows to English per cycle), and merges the two datasets into a single file. It also customizes the dataset by adding different names for patients, physicians, and hospitals. The script uses some of the functionalities offered by `utils/ontology_depth.py`.

After running this program, you will have a dataset named `merged_dataset.csv` and one named `merged_dataset_with_parents.csv` containing also parent codes.
The functionalities of `save_and_prepare_database.py` exploits the file `utils/names.py` which contains the names of patients, physicians, and hospitals.

### IPM Creation

- **`generate_ipm.py`**: It generates the IPM, for a given depth and number of parameters. The IPM is saved in a file named `hpo.ctw`, in CTWedge format, and `hpo.acts` in the format compatible with CAgen. To perform the translation, the script uses the functionalities offered by `utils/ctwedge_to_acts_translator.py`.

### Combinatorial sampling

- **`combinatorial_sampling.py`**: It generates the file `2wise_test_suite.csv` which contains the real test cases to be executed against the LLM.

### Test execution

After the dataset (`2wise_test_suite.csv`) is ready and the LLM-based phenotype extractor is set up (see [https://doi.org/10.5281/zenodo.17912782](https://doi.org/10.5281/zenodo.17912782)) and stored in the `test_scripts` folder, you can run the tests using the scripts in the `test_scripts` folder.

In particular, the **combinatorial prompt testing** process is executed through the file `test_scripts/PhenotypeExtractorTesting.py`, while the exhaustive prompt testing is executed through the file `test_scripts/PhenotypeExtractorTestingExhaustive.py`.

### Analysis scripts
- **`utis/dataset_analysis.py`**: It checks how many of the phenotypes in HPO are not covered by the dataset. It considers the dataset stored in the `output/merged_dataset_with_parents.csv` file, and the combinatorial test suite in `output/2wise_test_suite.csv`.
