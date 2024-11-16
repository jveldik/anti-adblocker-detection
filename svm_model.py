import pickle
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.metrics import accuracy_score, classification_report

def create_model(matrix, labels, balancing):
    # Convert labels to a numpy array
    labels = np.array(labels)

    X_train, X_test, y_train, y_test = train_test_split(matrix, labels, test_size=0.25, random_state=42, stratify = labels)

    parameters = {
        'C': [0.1, 0.5, 1, 5, 10],
        'gamma': ['scale', 'auto', 0.001, 0.01, 0.1],
        'kernel': ['linear', 'poly', 'rbf'],
        'degree': [2, 3, 4]
    }

    # Initialize the SVM classifier with class weights
    svc = SVC(class_weight='balanced')

    # Initialize stratified k-fold cross-validation
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # Initialize a grid search for the best parameters based on the accuracy score
    clf = GridSearchCV(svc, parameters, scoring='accuracy', cv=skf)

    # Train the model with the data
    clf.fit(X_train, y_train)

    # Predict on the test set
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    classification_rep = classification_report(y_test, y_pred)

    result = {
            'Set name': set_name,
            'Number of features': number_of_features,
            'Class balancing': balancing,
            'Best parameters': clf.best_params_,
            'Training accuracy': clf.best_score_,
            'Test accuracy': accuracy,
            'Classification report': '\n' + classification_rep
            }
    
    for key, value in result.items():
        print(key, ":", value)
    
    return clf, result

if __name__ == "__main__":
    df = pd.read_csv("data/stored_urls.csv")
    labels = df['manual'].dropna().tolist()
    results = []
    results_resampled = []
    smote = SMOTE(sampling_strategy='auto', random_state=42)
    
    for set_name in ["all", "identifier", "literal"]:
        for number_of_features in [100, 1000, 10000]:
            # Load feature matrix
            with open(f"data/matrices/{set_name}_{number_of_features}.pickle", 'rb') as f:
                matrix = pickle.load(f)
            balancing = "class_weights"
            # Create and train the model
            clf, result = create_model(matrix, labels, balancing)
            # Save the model
            with open(f"data/models/svm_{balancing}_{set_name}_{number_of_features}.pickle", 'wb') as f:
                pickle.dump(clf, f)
            # Store the results
            results.append(result)
            # Again with complete oversampling
            balancing = "oversampling"
            matrix_resampled, labels_resampled = smote.fit_resample(matrix, labels)
            clf_resampled, result_resampled = create_model(matrix_resampled, labels_resampled, balancing)
            with open(f"data/models/svm_{balancing}_{set_name}_{number_of_features}.pickle", 'wb') as f:
                pickle.dump(clf_resampled, f)
            results.append(result_resampled)

    # Convert results to DataFrame
    results_df = pd.DataFrame(results)

    # Print the table of accuracy scores
    print(results_df[['Set name', 'Number of features', 'Class balancing', 'Training accuracy', 'Test accuracy']])

    # Write the results to a CSV file
    results_df.to_csv('data/svm_results.csv', index=False)