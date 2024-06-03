import os
import pickle
import csv
import numpy as np
from scipy.sparse import lil_matrix
from feature_extraction import extract_features_from_url

# Function to create a sparse row vector from feature lists
def create_sparse_row(feature_lists, feature_set, set_name):
    if set_name == "all":
        relevant_features = feature_lists[0]
    elif set_name == "literal":
        relevant_features = feature_lists[1]
    elif set_name == "identifier":
        relevant_features = feature_lists[2]
    
    feature_vector = lil_matrix((1, len(feature_set)), dtype=bool)
    for feature in relevant_features:
        if feature in feature_set:
            index = feature_set.index(feature)
            feature_vector[0, index] = 1
    
    return feature_vector

# Function to save the prediction results
def save_results(urls, labels, modelname, set_name, number_of_features):
    with open(f"data/{modelname}_{set_name}_{number_of_features}_labeled_urls.csv", "a", newline='') as file:
        writer = csv.writer(file)
        for url, label in zip(urls, labels):
            writer.writerow([url, label])

if __name__ == "__main__":
    # Change model_name, set_name and number_of_features as needed
    modelname = "svm_initial"
    set_name = "identifier"
    number_of_features = 1000

    # Load the model to predict the labels
    with open(f"data/models/{modelname}_{set_name}_{number_of_features}.pickle", 'rb') as f:
        model = pickle.load(f)

    # Load the features the model uses
    with open(f"data/feature_sets/{set_name}_{number_of_features}.pickle", 'rb') as f:
        feature_set = pickle.load(f)

    urls = []
    features_list = []

    for url_dir in os.listdir("data/scripts"):
        url = os.path.basename(url_dir)
        if url == ".gitkeep":
            continue
        urls.append(url)
        feature_lists = [[], [], []]
        extract_features_from_url(url, feature_lists)
        sparse_row = create_sparse_row(feature_lists, feature_set, set_name)
        features_list.append(sparse_row)

    # Convert features_list to a single sparse matrix
    features_matrix = lil_matrix((len(features_list), len(feature_set)), dtype=bool)
    for i, sparse_row in enumerate(features_list):
        features_matrix[i] = sparse_row

    # Convert the sparse matrix to CSR format for efficient row slicing
    features_matrix = features_matrix.tocsr()

    # Predict labels for the new data
    labels = model.predict(features_matrix)

    # Save the prediction results
    save_results(urls, labels, modelname, set_name, number_of_features)
