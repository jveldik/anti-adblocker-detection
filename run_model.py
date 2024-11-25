import pickle
import numpy as np
import pandas as pd
from scipy.sparse import lil_matrix
from sklearn.metrics import confusion_matrix

# Function to create a sparse row vector from feature lists
def create_sparse_row(feature_lists, feature_dict, set_name):
    if set_name == "all":
        relevant_features = ["l_" + feature for feature in list(set(feature_lists[0]))] + ["i_" + feature for feature in list(set(feature_lists[1]))]
    elif set_name == "literal":
        relevant_features = list(set(feature_lists[0]))
    elif set_name == "identifier":
        relevant_features = list(set(feature_lists[1]))

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

def get_best_model(results_df):
    # Find the index of the row with the highest "Test accuracy"
    index_best_model = results_df["Test accuracy"].idxmax()
    
    # Extract the required information for the best model
    set_name = results_df.loc[index_best_model, "Set name"]
    number_of_features = results_df.loc[index_best_model, "Number of features"]
    balancing = results_df.loc[index_best_model, "Class balancing"]
    
    return set_name, number_of_features, balancing

def create_and_add_column(df, modelname, set_name, number_of_features, balancing):
    # Load the model to predict the labels
    with open(f"data/models/{modelname}_{balancing}_{set_name}_{number_of_features}.pickle", 'rb') as f:
        model = pickle.load(f)

    # Load the features the model uses
    with open(f"data/feature_sets/{set_name}_{number_of_features}.pickle", 'rb') as f:
        feature_set = pickle.load(f)

    # Convert feature_set to a dictionary for fast lookup
    feature_dict = {feature: idx for idx, feature in enumerate(feature_set)}

    # Collect feature data
    features_matrix = collect_feature_data(df, feature_dict, set_name)

    # Reshape matrix for cnn or mlp input
    if modelname != "svm":
        features_matrix = features_matrix.toarray()

    # Predict labels for the new data
    labels = model.predict(features_matrix)

    # Convert labels from probability to a boolean label for cnn or mlp labels
    if modelname != "svm":
        labels = (labels > 0.5).astype(int)  # Threshold at 0.5

    # Print confusion matrix
    print(confusion_matrix(keyword_labels, labels))

    # Add a column
    df[f"{modelname}_{balancing}_{set_name}_{number_of_features}"] = labels

if __name__ == "__main__":
    # Load the existing data
    df = pd.read_csv("data/stored_urls.csv")
    keyword_labels = df['keywords'].fillna(2).tolist()

    # Add column for best svm model
    svm_results = pd.read_csv("data/svm_results.csv")
    set_name, number_of_features, balancing = get_best_model(svm_results)
    create_and_add_column(df, "svm", set_name, number_of_features, balancing)

    # Add column for best cnn model
    cnn_results = pd.read_csv("data/cnn_results.csv")
    set_name, number_of_features, balancing = get_best_model(cnn_results)
    create_and_add_column(df, "cnn", set_name, number_of_features, balancing)
    
    # Add column for best mlp model
    mlp_results = pd.read_csv("data/mlp_results.csv")
    set_name, number_of_features, balancing = get_best_model(mlp_results)
    create_and_add_column(df, "mlp", set_name, number_of_features, balancing)

    # Save the prediction results
    df.to_csv("data/stored_urls.csv", index=False)
