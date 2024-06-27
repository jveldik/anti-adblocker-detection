import pickle
import csv
import sys
from scipy.sparse import lil_matrix

# Function to create a sparse row vector from feature lists
def create_sparse_row(feature_lists, feature_dict, set_name):
    if set_name == "all":
        relevant_features = list(set(feature_lists[0][0]))
    elif set_name == "literal":
        relevant_features = list(set(feature_lists[1][0]))
    elif set_name == "identifier":
        relevant_features = list(set(feature_lists[2][0]))

    feature_vector = lil_matrix((1, len(feature_dict)), dtype=bool)
    for feature in relevant_features:
        if feature in feature_dict:
            index = feature_dict[feature]
            feature_vector[0, index] = 1
    return feature_vector

# Function to save the prediction results
def save_results(urls, labels, modelname, set_name, number_of_features):
    with open(f"data/{modelname}_{set_name}_{number_of_features}_labeled_urls.csv", "a", newline='') as file:
        writer = csv.writer(file)
        for url, label in zip(urls, labels):
            writer.writerow([url, label])

def collect_feature_data(filename, feature_dict, set_name):
    urls = []
    features_list = []
    
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            url = row[0]
            urls.append(url)
            with open(f"data/features/{url}.pickle", 'rb') as f:
                feature_lists = pickle.load(f)
            sparse_row = create_sparse_row(feature_lists, feature_dict, set_name)
            features_list.append(sparse_row)
    
    # Convert features_list to a single sparse matrix
    features_matrix = lil_matrix((len(features_list), len(feature_dict)), dtype=bool)
    for i, sparse_row in enumerate(features_list):
        features_matrix[i] = sparse_row

    # Convert the sparse matrix to CSR format for efficient row slicing
    features_matrix = features_matrix.tocsr()
    
    return urls, features_matrix

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: run_model.py <filename> <modelname> <set_name> <number_of_features>")
        exit()
    filename = sys.argv[1]
    modelname = sys.argv[2]
    set_name = sys.argv[3]
    number_of_features = int(sys.argv[4])
    
    # Load the model to predict the labels
    with open(f"data/models/{modelname}_{set_name}_{number_of_features}.pickle", 'rb') as f:
        model = pickle.load(f)

    # Load the features the model uses
    with open(f"data/feature_sets/{set_name}_{number_of_features}.pickle", 'rb') as f:
        feature_set = pickle.load(f)

    # Convert feature_set to a dictionary for fast lookup
    feature_dict = {feature: idx for idx, feature in enumerate(feature_set)}

    # Collect feature data
    urls, features_matrix = collect_feature_data(filename, feature_dict, set_name)

    # Predict labels for the new data
    labels = model.predict(features_matrix)

    # Save the prediction results
    save_results(urls, labels, modelname, set_name, number_of_features)
