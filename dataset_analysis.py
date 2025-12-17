import pandas as pd
from collections import defaultdict, deque

# ------- Load CSVs -------
file1 = pd.read_csv("output/merged_dataset_with_parents.csv")  # columns: HPO_IDs,Parent_HPO_Codes,Document
file2 = pd.read_csv("output/2wise_test_suite.csv")  # columns: TestCase,HPO_IDs,Parent_IDs,Document

# ------- Helper function to split "'HP:0002213','HP:0000656'" into a list -------
def extract_codes(cell):
    if pd.isna(cell):
        return []
    # Remove spaces; split by comma; strip quotes
    return [code.strip().strip("'").strip('"') for code in cell.split(',')]

# ------- Extract all HPO codes from File 1 -------
file1_hpo_sets = file1["HPO_IDs"].apply(extract_codes)
all_hpo_file1 = set(code for row in file1_hpo_sets for code in row)

# ------- Extract all HPO codes from File 2 -------
file2_hpo_sets = file2["HPO_IDs"].apply(extract_codes)
all_hpo_file2 = set(code for row in file2_hpo_sets for code in row)

# ------- Compute uncovered HPO codes -------
uncovered = all_hpo_file1 - all_hpo_file2

# ------- Compute percentage -------
total = len(all_hpo_file1)
uncovered_count = len(uncovered)
percentage_uncovered = (uncovered_count / total) * 100 if total > 0 else 0

# ------- Print results -------
print(f"Total HPO codes in File 1: {total}")
print(f"HPO codes NOT covered by File 2: {uncovered_count}")
print(f"Percentage uncovered: {percentage_uncovered:.2f}%")

# ---------------------
# LOAD HPO ONTOLOGY (hp.obo) AND BUILD PARENT→CHILD LOOKUP
# ---------------------
def load_hpo_children(obo_path="hp.obo"):
    parent_to_children = defaultdict(set)

    current_id = None
    with open(obo_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "[Term]":
                current_id = None
            elif line.startswith("id:"):
                current_id = line.replace("id:", "").strip()
            elif line.startswith("is_a:") and current_id:
                parent = line.replace("is_a:", "").split("!")[0].strip()
                parent_to_children[parent].add(current_id)

    return parent_to_children

# ---------------------
# FUNCTION TO GET ALL DESCENDANTS OF A GIVEN HPO NODE
# ---------------------
def get_all_children(hpo_code):
    """Breadth-first search through the ontology."""
    descendants = set()
    queue = deque([hpo_code])

    while queue:
        node = queue.popleft()
        for child in parent_to_children.get(node, []):
            if child not in descendants:
                descendants.add(child)
                queue.append(child)

    return descendants


parent_to_children = load_hpo_children("utils/hp.obo")
expanded_file2_codes = set(all_hpo_file2)

for code in all_hpo_file1:
    expanded_file2_codes.update(get_all_children(code))

# ---------------------
# CHECK COVERAGE
# ---------------------
uncovered = all_hpo_file1 - expanded_file2_codes
percentage_uncovered = (len(uncovered) / len(all_hpo_file1)) * 100 if all_hpo_file1 else 0


# ---------------------
# REPORT
# ---------------------
print("=====================================")
print(" HPO COVERAGE ANALYSIS WITH CHILD TERMS")
print("=====================================")
print(f"Total unique HPO codes in File 1: {len(all_hpo_file1)}")
print(f"Total unique HPO codes in File 2 (original): {len(all_hpo_file2)}")
print(f"Total unique HPO codes in File 2 (expanded with children): {len(expanded_file2_codes)}")
print(f"Number of UNcovered HPO codes: {len(uncovered)}")
print(f"Percentage uncovered: {percentage_uncovered:.2f}%\n")