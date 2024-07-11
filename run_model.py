import pickle
import sys
import pandas as pd
from scipy.sparse import lil_matrix

# Function to create a sparse row vector from feature lists
def create_sparse_row(feature_lists, feature_dict, set_name):
    if set_name == "all":
        relevant_features = list(set(feature_lists[0]))
    elif set_name == "literal":
        relevant_features = list(set(feature_lists[1]))
    elif set_name == "identifier":
        relevant_features = list(set(feature_lists[2]))

    feature_vector = lil_matrix((1, len(feature_dict)), dtype=bool)
    for feature in relevant_features:
        if feature in feature_dict:
            index = feature_dict[feature]
            feature_vector[0, index] = 1
    return feature_vector

def collect_feature_data(df, feature_dict, set_name):
    urls = df['url'].tolist()
    features_list = []
    
    for url in urls:
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
    
    return features_matrix

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: run_model.py <modelname> <set_name> <number_of_features>")
        exit()
    modelname = sys.argv[1]
    set_name = sys.argv[2]
    number_of_features = int(sys.argv[3])

    # Load the existing data
    df = pd.read_csv("data/stored_urls.csv")

    # Load the model to predict the labels
    with open(f"data/models/{modelname}_{set_name}_{number_of_features}.pickle", 'rb') as f:
        model = pickle.load(f)

    # Load the features the model uses
    with open(f"data/feature_sets/{set_name}_{number_of_features}.pickle", 'rb') as f:
        feature_set = pickle.load(f)

    # Convert feature_set to a dictionary for fast lookup
    feature_dict = {feature: idx for idx, feature in enumerate(feature_set)}

    # Collect feature data
    features_matrix = collect_feature_data(df, feature_dict, set_name)

    # Predict labels for the new data
    labels = model.predict(features_matrix)

    # Add a column
    df[f"{modelname}_{set_name}_{number_of_features}"] = labels

    # Save the prediction results
    df.to_csv("data/stored_urls.csv", index=False)
