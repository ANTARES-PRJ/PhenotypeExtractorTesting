from pronto import Ontology
from collections import defaultdict
import ast

ontology_path = "utils/hp.obo"
root_ids = ["HP:0000001", "HP:0000118"]
# Load the ontology
ontology = Ontology(ontology_path)

def calculate_depth(ontology, term_id, exclude_ids):
    """
    Calculate the depth of a given term in an ontology by determining the number of 
    valid parent terms.

    Args:
        ontology (dict): A dictionary representing the ontology, where keys are term IDs 
                         and values are objects with methods and attributes such as 
                         `superclasses()` and `obsolete`.
        term_id (str): The ID of the term for which the depth is to be calculated.
        exclude_ids (list): A list of term IDs to exclude from the parent terms.

    Returns:
        int: The depth of the term, defined as the number of valid parent terms 
             after filtering out excluded and obsolete terms.

    Notes:
        - A term is considered valid if it is not in the `exclude_ids` list and is not marked as obsolete.
        - The `superclasses()` method of a term is expected to return a list of parent terms.
        - Each parent term is expected to have an `id` attribute and an `obsolete` attribute.
    """
    parents = ontology[term_id].superclasses(with_self=False, distance=1)
    # Remove from parents the terms in exclude_ids
    parents = [parent for parent in parents if parent.id not in exclude_ids]
    # Remove from parents all terms that are obsolete
    parents = [parent for parent in parents if not parent.obsolete]
    # Remove from parents the term itself
    parents = [parent for parent in parents if parent.id != term_id]

    # The depth is 1 plus the minimum depth of the parents
    # If there are no valid parents, return 0
    if not parents:
        return 0
    # Recursively calculate the depth of each parent
    depths = [calculate_depth(ontology, parent.id, exclude_ids) for parent in parents]
    depth = (min(depths) + 1) if depths else 0

    return depth

def get_hpo_depth():
    """
    Calculates the depth of terms in an ontology and groups them by depth.
    This function loads an ontology, iterates through all its terms, and calculates
    the depth of each term relative to specified root IDs. Obsolete terms are skipped.
    The terms are grouped by their depth in a dictionary, where the keys are the depths
    and the values are lists of term IDs.
    Returns:
        dict: A dictionary where keys are depths (int) and values are lists of term IDs (str).
    """
    # Load the ontology
    ontology = Ontology(ontology_path)
    dict_depths = defaultdict(set)
    
    # Iterate through all terms and calculate their depth   
    for term in ontology.terms():
        if term.obsolete:
            continue  # Skip obsolete terms
        
        depth = calculate_depth(ontology, term.id, root_ids)
        if depth != float('inf'):
            if (depth in dict_depths):
                dict_depths[depth].append(term.id)
            else:
                dict_depths[depth] = [term.id]

    return dict_depths

def get_parents(term_id, exclude_ids = root_ids, parse = True):
    """
    Retrieve the parent terms of a given ontology term, excluding specified terms and obsolete terms.

    Args:
        term_id (str): The identifier of the ontology term for which to retrieve parent terms.
        exclude_ids (list): A list of term IDs to exclude from the parent terms. Defaults to `root_ids`.

    Returns:
        list: A list of parent terms, excluding those in `exclude_ids` and those marked as obsolete.
    """
    term_id = term_id.replace(' ', ',').replace(',,',',')
    if (parse):
        codes =  ast.literal_eval(term_id)
    else:
        codes = term_id.split(',')
    parent_codes = list()

    if ("Error" in codes or "Mobile:" in codes):
        return parent_codes

    for code in codes:
        code = code.replace('\u200b', '').replace(" ", "")
        if (code):
            # Get super classes
            parents = ontology[code].superclasses()
            # Remove from parents the terms in exclude_ids
            parents = [parent for parent in parents if parent.id not in exclude_ids]
            # Remove from parents all terms that are obsolete
            parents = [parent for parent in parents if not parent.obsolete]
            parent_codes.append(parents)

    # Extract only the IDs
    parent_codes = [parent.id for parents in parent_codes for parent in parents]
    # Convert into a string
    parent_codes = ",".join(parent_codes)
    parent_codes = parent_codes.replace("[", "").replace(']', "").replace("'", "").replace(" ", "")

    return parent_codes


def get_parent_map(exclude_ids = root_ids):
    """
    Generates a mapping of HPO (Human Phenotype Ontology) term IDs to their parent term IDs.
    Args:
        exclude_ids (list): A list of term IDs to exclude from the parent mapping. Defaults to `root_ids`.
    Returns:
        dict: A dictionary where the keys are HPO term IDs and the values are lists of parent term IDs,
                excluding any IDs specified in `exclude_ids`.
    Notes:
        - Obsolete terms in the ontology are skipped.
        - Parent term IDs are split by commas and filtered to exclude IDs in `exclude_ids`.
    """
    parent_map = {}
    for term in ontology.terms():
        if term.obsolete:
            continue  # Skip obsolete terms

        parent_map[term.id] = get_parents(term.id, parse = False)
        # Remove excluded IDs
        parent_map[term.id] = [parent for parent in parent_map[term.id].split(',') if parent not in exclude_ids]

    return parent_map