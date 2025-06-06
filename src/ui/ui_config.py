import yaml
import os

def load_styles(path="src/ui/styles.yaml"):
    with open(path, "r") as file:
        return yaml.safe_load(file)
