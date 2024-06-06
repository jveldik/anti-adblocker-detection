import csv
import pickle
import sys
import numpy as np
from sklearn import svm
from sklearn.model_selection import StratifiedKFold, cross_val_score, cross_val_predict
from sklearn.metrics import classification_report
from sklearn.utils.class_weight import compute_class_weight

# Load the saved matrices and feature sets
def load_data(filename, set_name, number_of_features):
    labels = []
    with open(f"data/{filename}", mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[1] == "True":
                labels.append(True)
            elif row[1] == "False":
                labels.append(False)
    with open(f"data/matrices/{set_name}_{number_of_features}.pickle", 'rb') as f:
        matrix = pickle.load(f)
    return labels, matrix

if __name__ == "__main__":
    if len(sys.argv) == 5:
        filename = sys.argv[1]
        modelname = sys.argv[2]
        set_name = sys.argv[3]
        number_of_features = sys.argv[4]
    else:
        print("The first argument should be the filename")
        print("The second argument should be the modelname")
        print("The third argument should be the set name")
        print("The fourth argument should be the number of features")
        exit()

    # Load feature matrix and labels
    labels, matrix = load_data(filename, set_name, number_of_features)

    # Convert labels to a numpy array
    labels = np.array(labels)

    # Compute class weights
    class_weights = compute_class_weight('balanced', classes=[False, True], y=labels)
    class_weight_dict = {False: class_weights[0], True: class_weights[1]}

    # Initialize the SVM classifier with class weights
    clf = svm.SVC(class_weight=class_weight_dict)

    # Perform stratified k-fold cross-validation
    skf = StratifiedKFold(n_splits=5)
    cross_val_scores = cross_val_score(clf, matrix, labels, cv=skf, scoring='accuracy')

    print("Cross-validation accuracy scores:", cross_val_scores)
    print("Mean cross-validation accuracy:", np.mean(cross_val_scores))

    # Train the classifier on the entire dataset
    clf.fit(matrix, labels)

    # Generate a classification report using cross-validation
    y_pred = cross_val_predict(clf, matrix, labels, cv=skf)
    classification_rep = classification_report(labels, y_pred)
    print("Classification Report:\n", classification_rep)

    # Save the model
    with open(f"data/models/{modelname}_{set_name}_{number_of_features}.pickle", 'wb') as f:
        pickle.dump(clf, f)