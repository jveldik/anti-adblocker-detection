import os
import csv
import esprima
import sys
import pickle

# Function to extract features from an AST
def extract_features_from_AST(node, new_features):
    stack = [node]
    while stack:
        current_node = stack.pop()
        if isinstance(current_node, esprima.nodes.Node):
            if current_node.type == 'Literal':
                text = str(current_node.value)
                if text and len(text) < 50:
                    new_features[0].append(text)
                    new_features[1].append(text)
            elif current_node.type == 'Identifier':
                text = str(current_node.name)
                if text and len(text) < 50:
                    new_features[0].append(text)
                    new_features[2].append(text)
            stack += reversed([value for key, value in current_node.items() if isinstance(value, (list, esprima.nodes.Node))])
        elif isinstance(current_node, list):
            stack += reversed(current_node)

def extract_features_from_url(url):
    new_features = [[],[],[]]
    if not os.path.exists(f"data/scripts/{url}"):
        print(f"Directory data/scripts/{url} does not exist")
        return new_features
    for dir in os.listdir(f"data/scripts/{url}"):
        if dir.endswith(".js"):
            with open(f"data/scripts/{url}/{dir}", 'r', encoding='utf-8') as f:
                script = f.read()
            try:
                ast = esprima.parseScript(script)
            except Exception as e:
                with open('parsing_errors.log', 'a') as error_log:
                    error_log.write(f"Error parsing JavaScript code with {url}/{dir}: {e}\n")
                continue
            extract_features_from_AST(getattr(ast, 'body'), new_features)
    new_features = [list(set(features)) for features in new_features]
    print(f"Extracted features from {url}")
    return new_features

def save_features(url, features):
    with open(f'data/features/{url}.pickle', 'wb') as f:
        pickle.dump(features, f)

def process_urls(filename):
    with open(f"data/{filename}", mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            url = row[0]
            if os.path.exists(f"data/features/{url}.pickle"):
                print(f"Features already extracted for {url}")
            else:
                features = extract_features_from_url(url)
                save_features(url, features)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: feature_extraction.py <filename>")
        exit()
    filename = sys.argv[1]
    process_urls(filename)
