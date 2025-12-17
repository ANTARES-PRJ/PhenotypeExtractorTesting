import pandas as pd
import numpy as np
import io
import os
import pronto
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import sys
import argparse
from itertools import combinations


hpo_ontology_file = "../utils/hp.owl"
ontology = pronto.Ontology(hpo_ontology_file)

def check_sibling(result, oracle):
    if result == oracle or result == "" or oracle == "":
        return 0
    
    result = result.replace("'", "").replace("\\u200b", "").replace(" ", "").replace('"','')
    oracle = oracle.replace("'", "").replace("\\u200b", "").replace(" ", "").replace('"','')
    
    # Check if the concept with id result is a sibling of the concept with id order
    result_concept = ontology[result]
    oracle_concept = ontology[oracle]
    result_parents = set(result_concept.superclasses())
    # Add the result_parents the terms corresponding to the alternate ids
    for alternate_id in result_concept.alternate_ids:
        result_parents.add(alternate_id)

    if (result_parents.__contains__(oracle_concept)):
        return 1
    return 0

def check_notfound_pair(not_found, dict_couples):
    # Count all unordered pairs of missing HP codes
    for pair in combinations(sorted(not_found), 2):  # sorted for consistency
        if pair not in dict_couples:
            dict_couples[pair] = 0
        dict_couples[pair] += 1

    return dict_couples

def analyze_csv(name, limit):
    # Load CSV file
    file_path = name
    # First read it into a string, then replace the ']' with '],'
    with open(file_path, 'r') as file:
        data = file.read().replace('],', '];')

    # In the first line of data, the column names are separated by ','. I want to separate them by ';'
    data = data.replace(',', ';', 2)

    # Then, read the string into a pandas DataFrame
    df = pd.read_csv(io.StringIO(data), sep=";", header=0)

    # Extract the time column
    time_values = df['Time'].values
    df['Oracle'] = df['Oracle'].astype(str).replace('"','')

    # Calculate boxplot statistics
    Q1 = np.percentile(time_values, 25)
    median = np.percentile(time_values, 50)
    Q3 = np.percentile(time_values, 75)
    IQR = Q3 - Q1
    lower_whisker = Q1 - 1.5 * IQR
    upper_whisker = Q3 + 1.5 * IQR
    lower_whisker = max(lower_whisker, min(time_values))
    upper_whisker = min(upper_whisker, max(time_values))

    # Print calculated values
    print(f"Lower Whisker: {lower_whisker}")
    print(f"Lower Quartile (Q1): {Q1}")
    print(f"Median (Q2): {median}")
    print(f"Upper Quartile (Q3): {Q3}")
    print(f"Upper Whisker: {upper_whisker}")

    # Extract the result and oracle columns
    result_values = [s.replace('"', '') for s in df['Result'].values]
    oracle_values = [s.replace('"', '') for s in df['Oracle'].values]

    # Each value in the result_values list is in the form of [Á', 'B', 'C']. I want to extract the values
    # and put them in a list
    result_values = [value[1:-1].split(", ") for value in result_values]
    oracle_values = [value[1:-1].split(", ") for value in oracle_values]

    # Now count the number of correct predictions, regardless of the order
    correct_predictions = 0
    intersection_sum = 0
    additional_phenotypes = 0
    precisions = []
    recalls = []
    wrong_predictions = dict()
    pairs = dict()

    for i in range(len(result_values)):
        not_found = []
        current_intersection_size = len(set(result_values[i]).intersection(set(oracle_values[i])))
        additional_phenotypes = len(result_values) - current_intersection_size
        if set(result_values[i]) == set(oracle_values[i]):
            correct_predictions += 1
        else:
            for oracle in oracle_values[i]:
                found = False
                for result in result_values[i]:
                    if result != oracle and check_sibling(result, oracle) or check_sibling(oracle, result):
                        current_intersection_size += 1
                        found = True
                        break
                if not found:
                    if oracle not in wrong_predictions:
                        wrong_predictions[oracle] = 0
                    wrong_predictions[oracle] = wrong_predictions[oracle] + 1
                    not_found.append(oracle)

        if (current_intersection_size == len(oracle_values[i])):
            correct_predictions += 1

        additional_phenotypes += (len(set(result_values[i])) - current_intersection_size)
        intersection_sum += current_intersection_size
        precisions.append(current_intersection_size / len(result_values[i]))
        recalls.append(current_intersection_size / len(oracle_values[i]))

        pairs = check_notfound_pair(not_found, pairs)

        if limit > 0 and i >= limit:
            break

    # Order the wrong predictions by the number of times they appear and, then, by the HPO code
    wrong_predictions = dict(sorted(wrong_predictions.items(), key=lambda item: (-item[1], item[0])))
    
    # Print the wrong predictions by keeping 5 values in each line and limiting the number of values to 20
    print("****")
    print(f"Not identified phenotypes: {len(wrong_predictions)}")
    for i, (key, value) in enumerate(wrong_predictions.items()):
        if i % 5 == 0 and i != 0:
            print()
        print(f"{key}: {value}", end=", ")
        if i == 19: 
            break
    print("****")
    # Print the pairs of missing HP codes
    print("****")
    print(f"Missing pairs of HP codes: {len(pairs)}")
    for i, (key, value) in enumerate(pairs.items()):
        if i % 5 == 0 and i != 0:
            print()
        print(f"{key}: {value}", end=", ")
        if i == 19: 
            break
    print("****")
    print(f"Correct predictions: {correct_predictions}")
    print(f"Average hits: {intersection_sum/len(result_values)}")
    print(f"Average additional phenotypes: {additional_phenotypes/len(result_values)}")
    print(f"Average recall: {sum(recalls)/len(recalls)}")
    print(f"Average precision: {sum(precisions)/len(precisions)}")
    print(f"Total number of predictions: {len(recalls)}")
    print("-----------")

    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze CSV files containing phenotype extraction results.")
    parser.add_argument("-n", "--name", help="Name of the CSV file to analyze. If not provided, all CSV files in the current directory will be analyzed.", default=None)
    parser.add_argument("-l", "--limit", help="Consider only first l lines of the CSV file.", type=int, default=-1)
    args = parser.parse_args()
    file_name = args.name
    limit = args.limit

    data = []
    # Iterate over the csv files in the current folder and analyze them one by one
    for file in os.listdir("."):
        if file.endswith(".csv"):
            if file_name is not None and file_name not in file:
                continue
            print (f"Analyzing {file}")
            data.append(analyze_csv(file, limit))


    # Merge the dataframes
    dataF = pd.concat(data, axis=0)

    # Compute the mean of the time values
    print(f"Average time: {dataF['Time'].mean()}")
    print(f"Total time: {dataF['Time'].sum()}")
