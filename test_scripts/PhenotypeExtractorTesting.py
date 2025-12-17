from PhenotypeExtractor import *
import HPOMapper
import pandas as pd
import time
import os

models = ["gpt-oss:120b"]
prompts = ["phenotypes_prompt_mid.txt", 
           "phenotypes_prompt_simple.txt" 
           "phenotypes_prompt_full.txt"
           ]

use_two_prompts = False

# The path containing the test cases
test_path = "../output/2wise_test_suite.csv"
model_name = "sentence-transformers/all-MiniLM-L6-v2"
# The logger
logger = utils.logger_def(__name__)
# The json file with HPO concepts
hpo_concepts_file = "../concepts/hpo_concepts_filtered.json"
# The thresholds for fuzzy search
threshold = 0.8
threshold_for_equality = 0.9999

def get_llm_output(text, prompt, prompt2=None):
    # Dictionary containing all extracted data
    extracted_data = {}
    phenotypes = extract_phenotypes(text, default_model, prompt, logger)
    if prompt2 is not None:
        # If a second prompt is provided, use it to extract additional phenotypes
        phenotypes = extract_phenotypes("", default_model, prompt2.replace("{Text}", text).replace("{Json}",phenotypes), logger)

    # Map the phenotypes to HPO terms
    if phenotypes is not None and phenotypes != "[]" and phenotypes != "":
        data = HPOMapper.map_concepts(model_name, hpo_concepts_file, json.loads(phenotypes), threshold_for_equality, threshold, logger)
        extracted_data['phenotypes'] = data
    else:
        extracted_data['phenotypes'] = None

    return extracted_data

if __name__ == "__main__":
    # Open the csv file and read it into a pandas dataframe
    # The "HPO_IDs" column will contain our oracle
    # The "Document" column contains the text

    for model in models:
        for prompt_file in prompts:
            
            test_set = pd.read_csv(test_path)

            prompt = open("../prompts/" + prompt_file, "r").read()

            summary_file = "../results/summary_" + prompt_file.split(".")[0] + "_" + model.split(":")[0].replace(".", "") + ".csv"

            default_model = model

            if summary_file in os.listdir("../results/"):
                continue

            # Open the summary file
            summary = open(summary_file, "w")
            # Write the header
            summary.write("Result,Oracle,Time\n")

            for i in range(0, test_set.size-1):
                # Start counting the time
                start_time = time.time()
                
                try:
                    extracted_data = get_llm_output(test_set.iloc[i]["Document"], prompt)
                except Exception as e:
                    print(f"[Error] Failed to process document at index {i} - {prompt_file} - {model}: {repr(e)}. Skipping...")
                    continue
                
                # The oracle HPO ids are separated by a comma. We need to split them and convert them to a list
                oracle_HPO_ids = test_set.iloc[i]["HPO_IDs"]
                oracle_HPO_ids = oracle_HPO_ids.split(",")
                # Extracted data is a dictionary containing the extracted phenotypes. We need to extract the HPO ids
                # from the extracted data. They are in the "uri" field
                extracted_HPO_ids = []
                if extracted_data['phenotypes'] is not None:
                    for phenotype in extracted_data['phenotypes']:
                        if 'HPO_matched_URI' in phenotype:
                            extracted_HPO_ids.append(phenotype['HPO_matched_URI'])
                        else:
                            if 'options' in phenotype:
                                # Take only the first option
                                phenotype = phenotype['options'][0]
                                if 'uri' in phenotype:
                                    extracted_HPO_ids.append(phenotype['uri'])
                                    print("[Testing] " + phenotype['uri'])
                # For each extracted HPO id, remove the leading part "http://purl.obolibrary.org/obo/" and substitute "_" with ":"
                extracted_HPO_ids = [x.replace("http://purl.obolibrary.org/obo/", "").replace("_", ":") for x in extracted_HPO_ids]

                # End counting the time
                end_time = time.time()
                # Write the result to the summary file
                summary.write(str(extracted_HPO_ids) + "," + str(oracle_HPO_ids) + "," + str(end_time - start_time) + "\n")
                summary.flush()
                print(extracted_HPO_ids)
                print(oracle_HPO_ids)

            summary.close()
