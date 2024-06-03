import csv
import os
import pickle
import esprima
from scipy.sparse import lil_matrix
from sklearn.feature_selection import chi2, SelectKBest, VarianceThreshold

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

def extract_features_from_url(url, feature_lists):
    new_features = [[],[],[]]
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
    for feature_list, url_features in zip(feature_lists, new_features):
        url_features = list(set(url_features))
        feature_list.append(url_features)
    print(f"Extracted features from {url}")

def extract_features():
    feature_lists = [[], [], []]
    labels = []
    with open("data/labeled_urls.csv", mode = 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[1] == "True":
                labels.append(True)
                extract_features_from_url(row[0], feature_lists)
            elif row[1] == "False":
                labels.append(False)
                extract_features_from_url(row[0], feature_lists)
    return feature_lists, labels

def create_matrices(feature_lists):
    feature_sets = [None, None, None]
    matrices = [None, None, None]
    # Loop over the three different kinds of features
    for i, (matrix, feature_set, feature_list) in enumerate(zip(matrices, feature_sets, feature_lists)):
        # Flatten list, remove duplicates, and sort the features
        print("Creating feature set")
        feature_set = sorted(list(set([feature for features in feature_list for feature in features])))
        # Create a dictionary to map features to their indices
        feature_index_map = {feature: index for index, feature in enumerate(feature_set)}
        # Initialize sparse matrix
        matrix = lil_matrix((len(feature_list), len(feature_set)), dtype=bool)
        # Fill in the sparse matrix using the feature_index_map
        print("Filling in the matrix")
        for j, feature in enumerate(feature_list):
            for feature_value in feature:
                index = feature_index_map.get(feature_value)
                if index is not None:
                    matrix[j, index] = 1
        print(matrix.get_shape())
        # Assign the computed feature_set and matrix to the respective lists
        feature_sets[i] = feature_set
        matrices[i] = matrix
    return feature_sets, matrices

def save_data(matrix, feature_set, i, k):
    if i == 0:
        set_name = "all"
    elif i == 1:
        set_name = "literal"
    else:
        set_name = "identifier"
    with open(f"data/matrices/{set_name}_{k}.pickle", 'wb') as f:
        pickle.dump(matrix, f)
    with open(f"data/feature_sets/{set_name}_{k}.pickle", 'wb') as f:
        pickle.dump(feature_set, f)

def filter_matrices(matrices, feature_sets, labels):
    for i, (matrix, feature_set) in enumerate(zip(matrices, feature_sets)):
        # Initialize the VarianceThreshold
        variance_threshold = VarianceThreshold(threshold=0.01)
        # Fit and transform matrix to remove low variance features
        print("Applying treshold")
        matrix = variance_threshold.fit_transform(matrix)
        feature_set = variance_threshold.get_feature_names_out(feature_set)
        for k in [10000, 1000, 100]:
            # Initialize SelectKBest with the chi-squared test scoring function and desired k value
            selector = SelectKBest(score_func=chi2, k=k)
            # Fit and transform matrix to select the top k features
            print("Applying chi")
            matrix = selector.fit_transform(matrix, labels)
            feature_set = selector.get_feature_names_out(feature_set)
            # Save the filtered matrix and feature set
            print("Saving data")
            save_data(matrix, feature_set, i, k)

if __name__ == "__main__":
    feature_lists, labels = extract_features()
    feature_sets, matrices = create_matrices(feature_lists)
    filter_matrices(matrices, feature_sets, labels)