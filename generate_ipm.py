import pandas as pd
import re
import os
from itertools import combinations
from utils.ontology_depth import get_hpo_depth, get_parent_map
from utils.ctwedge_to_acts_translator import translate_from_ctwedge_to_acts

output_folder = "output"
file_name = "hpo.ctw"
file_name_acts = "hpo.acts"


def clean_hpo_code(hpo_code):
    """
    Cleans and normalizes an HPO (Human Phenotype Ontology) code.
    This function removes the 'HP:' prefix and leading zeros from the given HPO code.
    If the input is NaN or results in a single zero after cleaning, it returns None.
    Args:
        hpo_code (str or any): The HPO code to clean. Can be a string or a value that 
                               may be NaN (e.g., from a pandas DataFrame).
    Returns:
        str or None: The cleaned HPO code as a string, or None if the input is NaN 
                     or results in a single zero after cleaning.
    """
    if pd.isna(hpo_code):  
        return None
    cleaned_code = re.sub(r"^HP:0*", "", str(hpo_code))  # Removes 'HP:' and leading zeros
    return cleaned_code if cleaned_code != "0" else None  

def get_phenotypes_from_ontology(depth):
    """
    Retrieves and processes phenotypes from an ontology based on the specified depth.
    This function fetches all Human Phenotype Ontology (HPO) codes at a depth
    less than or equal to the specified depth, cleans them, and returns a sorted
    list of unique phenotypes.
    Args:
        depth (int): The depth level in the ontology to retrieve phenotypes from.
    Returns:
        list: A sorted list of cleaned HPO codes. If the specified depth is not
              available, an empty list is returned.
    Raises:
        None: This function does not raise exceptions but prints an error message
              if the specified depth is invalid.
    Notes:
        - The function relies on `get_hpo_depth()` to retrieve the ontology depths.
        - The `clean_hpo_code()` function is used to clean individual HPO codes.
    """
    depths = get_hpo_depth()
    if depth not in depths:
        print(f"Error: The depth {depth} is not available.")
        return []
    print(f"Depth {depth} found in the ontology.")
    
    # Merge all HPO codes at a depth lower or equal than the specified one
    combined_phenotypes = set()
    for d in range(1, depth + 1):
        combined_phenotypes.update(depths[d])

    cleaned_phenotypes = [clean_hpo_code(p) for p in combined_phenotypes]
    return sorted(filter(None, cleaned_phenotypes))  # Removes any empty values

def write_ctwedge_parameters(filename, phenotypes, num_phenotypes):
    """
    Writes CT wedge parameters to a file.
    This function generates a file containing model HPO parameters based on the provided
    phenotypes. It cleans and sorts the phenotypes, then writes them in a structured format
    to the specified file.
    Args:
        filename (str): The path to the file where the parameters will be written.
        phenotypes (list): A list of phenotype HPO codes to be processed.
        num_phenotypes (int): The number of phenotype parameters to include in the output.
    Returns:
        None
    Side Effects:
        Creates or overwrites the specified file with the generated parameters.
        Prints a confirmation message upon successful file creation.
    Notes:
        - The phenotypes are cleaned using the `clean_hpo_code` function (assumed to be defined elsewhere).
        - Duplicate and empty phenotype codes are removed, and the remaining codes are sorted numerically.
        - Each phenotype parameter in the output includes "NULL" as a default value.
    """    
    # Clean and sort the phenotypes
    cleaned_phenotypes = sorted(set(filter(None, [clean_hpo_code(hpo) for hpo in phenotypes])), key=int)

    with open(filename, "w", encoding="utf-8") as file:
        file.write("Model HPO\n\n")
        file.write("Parameters:\n")
        for i in range(1, num_phenotypes + 1):
            file.write(f"\tphenotype{i}: {{{', '.join(['NULL'] + cleaned_phenotypes)}}};\n")

    print(f"File '{filename}' succesfully created with parameters.")

def write_ctwedge_constraints(filename, num_phenotypes, depth):
    """
    Writes CTWedge constraints to a specified file based on the given number of phenotypes
    and ontology depth. The constraints include rules for non-NULL phenotypes, uniqueness,
    and hierarchical relationships.
    Args:
        filename (str): The path to the file where constraints will be written.
        num_phenotypes (int): The number of phenotypes to consider for constraints.
        depth (int): The depth of the ontology to retrieve phenotypes.
    Constraints:
        1. At least one phenotype must be non-NULL.
        2. No duplicate phenotypes are allowed.
        3. Hierarchical constraints ensure that if a phenotype is assigned, its
           supercategories cannot be assigned to other phenotypes.
    Notes:
        - The function uses helper functions `get_parent_map`, `get_phenotypes_from_ontology`,
          and `clean_hpo_code` to process the hierarchy and phenotypes.
        - The constraints are written in a human-readable format with comments for clarity.
    Output:
        The constraints are appended to the specified file, and a confirmation message
        is printed to indicate successful saving.
    """
    hierarchy_map = get_parent_map()
    phenotypes = get_phenotypes_from_ontology(depth)

    # Clean all values in the hierarchy map
    for key, values in hierarchy_map.items():
        hierarchy_map[key] = [clean_hpo_code(hpo) for hpo
                              in values if clean_hpo_code(hpo) in phenotypes]
        
    # Do the same for keys
    hierarchy_map = {clean_hpo_code(key): values for key, values in hierarchy_map.items() if clean_hpo_code(key) in phenotypes}

    with open(filename, "a", encoding="utf-8") as file:
        file.write("\nConstraints:\n")

        # Constraint: At least one phenotype must be non-NULL
        for null_phenotypes in combinations(range(1, num_phenotypes + 1), num_phenotypes - 1):
            non_null_phenotype = set(range(1, num_phenotypes + 1)) - set(null_phenotypes)
            non_null_phenotype = non_null_phenotype.pop() 
            # Write the constraint
            null_conditions = " AND ".join(f"phenotype{i}=NULL" for i in null_phenotypes)
            file.write(f"\t# ({null_conditions}) => (phenotype{non_null_phenotype}!=NULL) #\n")


        # Constraint: no duplicates allowed
        for i in range(1, num_phenotypes + 1):
            for j in range(1, num_phenotypes + 1):
                if i != j:
                    file.write(f"\t# phenotype{i}!=NULL => (phenotype{i}!=phenotype{j}) #\n")

        # Hierarchical constraints
        for base_phenotype, supercategories in hierarchy_map.items():
            if base_phenotype not in phenotypes:
                continue

            for i in range(1, num_phenotypes + 1):
                for j in range(1, num_phenotypes + 1):
                    if i != j:
                        constraints = [
                            f"phenotype{j}!={sc}"
                            for sc in supercategories if sc in phenotypes and sc != base_phenotype
                        ]
                        if constraints:
                            file.write(f"\t# phenotype{i}=={base_phenotype} => (" + " AND ".join(constraints) + ") #\n")

    print(f"Constraints saved in the file: '{filename}'")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Script directory
    output_dir = os.path.join(script_dir, output_folder)  
    os.makedirs(output_dir, exist_ok=True)

    try:
        depth = int(input("Insert the desired depth: "))
        num_phenotypes = int(input("Insert the desired number of phenotypes: "))
    except ValueError:
        print("Error: depth and number of phenotypes must be integers.")
        pass
    
    output_file = os.path.join(output_dir, file_name)
    phenotypes = get_phenotypes_from_ontology(depth)
    if not phenotypes:
        print("Error: could not retrieve phenotypes.")
        pass
    print (f"Phenotypes retrieved: {len(phenotypes)}")

    write_ctwedge_parameters(output_file, phenotypes, num_phenotypes)
    write_ctwedge_constraints(output_file, num_phenotypes, depth)

    # Translate CTWedge to ACTS
    acts_file = os.path.join(output_dir, file_name_acts)
    translate_from_ctwedge_to_acts(output_file, acts_file, output_dir)
