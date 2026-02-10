import re


def convert_to_dataclass(typeddict_str):
    # Extract class definition
    class_definition = typeddict_str.split(":")[0].strip()

    # Transform definition to dataclass syntax
    dataclass_definition = f"@dataclass\n{class_definition.replace('TypedDict', '')}"
    return dataclass_definition


def process_file(input_file, output_file):
    """
    Processes a file with TypedDict definitions and writes dataclass implementations to another file.
    """
    with open(input_file, "r") as f_in, open(output_file, "w") as f_out:
        # Read file content
        content = f_in.read()

        # Find all TypedDict definitions using regex
        typeddict_definitions = re.findall(
            r"class\s+([A-Z][a-zA-Z0-9_]+)\s*\(TypedDict\):", content
        )

        # Convert each definition and write to output file
        for definition in typeddict_definitions:
            dataclass_impl = convert_to_dataclass(definition)
            f_out.write(dataclass_impl + "\n\n")


# Specify input and output file paths
input_file = "json_schema_interface.py"
output_file = "dataclass_file.py"

process_file(input_file, output_file)
