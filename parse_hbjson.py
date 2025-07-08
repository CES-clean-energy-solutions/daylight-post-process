import json

# Function to load and parse the HBJSON file
def parse_hbjson(file_path):
    # Load and parse the .hbjson file
    with open(file_path, 'r') as f:
        hbjson_data = json.load(f)
    return hbjson_data
