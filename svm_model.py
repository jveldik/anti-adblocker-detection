import pickle
import numpy as np
import pandas as pd
from sklearn import svm
from sklearn.model_selection import StratifiedKFold, cross_val_score, cross_val_predict
from sklearn.metrics import classification_report
from sklearn.utils.class_weight import compute_class_weight

def create_model(labels, matrix):
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

    return clf, cross_val_scores, classification_rep

if __name__ == "__main__":
    df = pd.read_csv("data/stored_urls.csv")
    labels = df['manual'].dropna().tolist()
    results = []
    
    for set_name in ["all", "identifier", "literal"]:
        for number_of_features in [100, 1000, 10000]:
            # Load feature matrix
            with open(f"data/matrices/{set_name}_{number_of_features}.pickle", 'rb') as f:
                matrix = pickle.load(f)
            clf, cross_val_scores, classification_rep = create_model(labels, matrix)
            # Save the model
            with open(f"data/models/svm_{set_name}_{number_of_features}.pickle", 'wb') as f:
                pickle.dump(clf, f)
            # Store the results
            result = {
                'set_name': set_name,
                'number_of_features': number_of_features,
                'cross_val_scores': cross_val_scores,
                'mean_accuracy': np.mean(cross_val_scores),
                'classification_report': '\n' + classification_rep
            }
            results.append(result)

    # Convert results to a DataFrame
    results_df = pd.DataFrame(results)

    # Print the table of accuracy scores
    print(results_df[['set_name', 'number_of_features', 'mean_accuracy']])

    # Write the results to a CSV file
    results_df.to_csv('data/svm_results.csv', index=False)