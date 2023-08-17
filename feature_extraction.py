import os
import re
import ast
from collections import defaultdict

# Function to extract JavaScript code from HTML file
def extract_scripts(html_path):
    js_code = ""
    with open(html_path, 'r', encoding='utf-8') as f:
        html_code = f.read()
        # Using regular expression to find <script> tags and extract JavaScript code
        script_tags = re.findall(r'<script.*?>(.*?)<\/script>', html_code, re.DOTALL)
        scripts = '\n'.join(script_tags)
    return scripts

# Function to extract features from JavaScript code
def extract_features(scripts):
    # Parse JavaScript code into AST
    script_asts = ast.parse(scripts)
    
    # Initialize feature dictionaries for different feature types
    feature_sets = {
        'all': defaultdict(int),
        'literal': defaultdict(int),
        'keyword': defaultdict(int)
    }
    
    # Traverse the AST to extract features
    for node in ast.walk(script_asts):
        if isinstance(node, ast.stmt):
            context = type(node).__name__
            text = ast.dump(node)
            text_elements = text.split()
            
            for feature_set in feature_sets:
                if feature_set == 'literal':
                    text_elements = [el for el in text_elements if el.isnumeric() or el.startswith('"') or el.startswith("'")]
                elif feature_set == 'keyword':
                    text_elements = [el for el in text_elements if el in {'for', 'while', 'try', 'except', 'if', 'switch'}]
                
                feature = f"{context} :: {' '.join(text_elements)}"
                feature_sets[feature_set][feature] += 1
    
    return feature_sets

# Iterate through HTML files and extract features
page_sources_path = "data/page_sources"
for file in os.listdir(page_sources_path):
    if file.endswith('.html'):
        html_path = os.path.join(page_sources_path, file)
        scripts = extract_scripts(html_path)
        feature_sets = extract_features(scripts)
        print(f"Features extracted from {file}:\n{feature_sets}")
        break