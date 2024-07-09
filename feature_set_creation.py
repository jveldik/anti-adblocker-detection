import pickle
import pandas as pd
from scipy.sparse import lil_matrix
from sklearn.feature_selection import chi2, SelectKBest, VarianceThreshold

def load_features(url):
    with open(f'data/features/{url}.pickle', 'rb') as f:
        return pickle.load(f)

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
        for j, features in enumerate(feature_list):
            for feature_value in features:
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
        print("Applying threshold")
        matrix = variance_threshold.fit_transform(matrix)
        feature_set = variance_threshold.get_feature_names_out(feature_set)
        for k in [10000, 1000, 100]:
            # Initialize SelectKBest with the chi-squared test scoring function and desired k value
            selector = SelectKBest(score_func=chi2, k=k)
            # Fit and transform matrix to select the top k features
            print("Applying chi-squared test")
            matrix = selector.fit_transform(matrix, labels)
            feature_set = selector.get_feature_names_out(feature_set)
            # Save the filtered matrix and feature set
            print("Saving data")
            save_data(matrix, feature_set, i, k)

def extract_features_and_labels():
    feature_lists = [[], [], []]
    labels = []
    df = pd.read_csv("data/stored_urls.csv")
    df = df[df['manual'].notnull()]
    for url in df['url'].to_list():
        features = load_features(url)
        for feature_list, url_features in zip(feature_lists, features):
            feature_list.append(url_features)
    labels = df['manual'].tolist()
    return feature_lists, labels

if __name__ == "__main__":
    feature_lists, labels = extract_features_and_labels()
    feature_sets, matrices = create_matrices(feature_lists)
    filter_matrices(matrices, feature_sets, labels)
