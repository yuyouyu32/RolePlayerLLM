import yaml
import os

def read_yaml_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as e:
            print(f"Error in configuration file: {e}")
            return None
