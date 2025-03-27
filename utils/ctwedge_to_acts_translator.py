import os
import re

def translate_from_ctwedge_to_acts(ctwedge_file, acts_file, output_dir):
    """
    Translates a CTWedge file into an ACTS file format.
    This function reads a CTWedge file, extracts parameters and constraints, 
    and converts them into the ACTS format. The resulting ACTS file is saved 
    in the specified output directory.
    Args:
        ctwedge_file (str): The name of the input CTWedge file.
        acts_file (str): The name of the output ACTS file.
        output_dir (str): The directory where the input and output files are located.
    Returns:
        None
    Raises:
        FileNotFoundError: If the specified CTWedge file does not exist.
    Notes:
        - The function assumes the CTWedge file contains a "Model" name in the 
          first line, followed by "Parameters:" and "Constraints:" sections.
        - Parameters are translated into ACTS format as enums.
        - Constraints are processed and translated using the `translate_constraint` function.
        - The output ACTS file includes system information, parameters, and constraints.
    Example:
        translate_from_ctwedge_to_acts("input.ctw", "output.acts", "/path/to/output")
    """
    parameters = []
    constraints = []
    model_name = "Model"  # Default model name

    # Get the full path of the input and output files
    ctwedge_path = os.path.join(output_dir, ctwedge_file)
    acts_path = os.path.join(output_dir, acts_file)

    try:
        with open(ctwedge_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Errore: file {ctwedge_path} not found")
        return

    # Get the model name from the first line
    if lines:
        l1 = lines[0].strip()
        if l1.startswith("Model "):
            model_name = l1.split("Model ")[1]  # Get the name after "Model "

    # Add system info
    system_info = ["[System]", f"Name: {model_name}", ""]

    # Translate parameters
    parsing = False
    for line in lines:
        line = line.strip()
        if line.startswith("Parameters:"):
            parsing = True
            parameters.append("[Parameter]")  # Start of parameters
            continue
        if parsing:
            if line:  # If the line is not empty
                match = re.match(r'(\w+): \{(.+?)\};', line)  # Regex to extract name and parameter values
                if match:
                    parameter_name, values = match.groups()
                    parameters.append(f"{parameter_name}(enum):{values}")
            else:
                parsing = False  # Stop parsing

    # Analisi dei vincoli
    parsing = False
    for line in lines:
        line = line.strip()
        if line.startswith("Constraints:"):
            parsing = True
            continue
        if parsing and line.startswith("#"):
            constraint = line.strip("# ").strip()
            constraints.append(constraint)

    # Traduzione in ACTS
    acts_lines = system_info + parameters[:]  # Add system info and parameters
    acts_lines.append("")  # Empty line
    acts_lines.append("[Constraint]")

    for constraint in constraints:
        acts_lines.append(translate_constraint(constraint))

    # Save ACTS file
    with open(acts_path, 'w') as f:
        f.write('\n'.join(acts_lines))

    print(f"ACTS file has been created: {acts_path}")

def translate_constraint(ctwedge_constraint):
    """
    Translates a constraint string from CTWedge syntax to ACTS syntax.
    This function performs the following transformations:
    1. Substitutes logical operators:
       - Replaces "AND" with "&&".
       - Replaces "OR" with "||".
    2. Handles comparisons with NULL:
       - Replaces "=NULL" with "=\"NULL\"".
       - Replaces "!=NULL" with "!=\"NULL\"".
    3. Adjusts numerical comparisons:
       - Converts "==" to "=" for numerical equality.
       - Retains "!=" for numerical inequality.
    4. Simplifies multiple conditions:
       - Ensures proper formatting of logical expressions with parentheses.
    Args:
        ctwedge_constraint (str): The constraint string in CTWedge syntax.
    Returns:
        str: The translated constraint string in ACTS syntax.
    """
    # Subsitute logical operators
    acts_constraint = ctwedge_constraint.replace("AND", "&&").replace("OR", "||")

    # Comparison with NULL
    acts_constraint = acts_constraint.replace("=NULL", "=\"NULL\"")
    acts_constraint = acts_constraint.replace("!=NULL", "!=\"NULL\"")

    # Numerical comparison
    acts_constraint = re.sub(r'([a-zA-Z0-9_]+)==(\d+)', r'\1=\2', acts_constraint)
    acts_constraint = re.sub(r'([a-zA-Z0-9_]+)!=(\d+)', r'\1!=\2', acts_constraint)

    # Multiple conditions
    acts_constraint = re.sub(r'\(([^)]+)\) && \(([^)]+)\)', r'(\1) && (\2)', acts_constraint)
    acts_constraint = re.sub(r'\(([^)]+)\) \|\| \(([^)]+)\)', r'(\1) || (\2)', acts_constraint)

    return acts_constraint

if __name__ == "__main__":
    ctwedge_file = "test.ctw"  # Input file name
    acts_file = "hpo.acts"  # Output file name
    output_folder = "output"  # Output directory

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, output_folder)

    os.makedirs(output_dir, exist_ok=True)
    translate_from_ctwedge_to_acts(ctwedge_file, acts_file, output_dir)
