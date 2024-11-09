import os
import pickle
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from scikeras.wrappers import KerasClassifier
from sklearn.model_selection import StratifiedKFold, train_test_split, GridSearchCV
from sklearn.metrics import classification_report, accuracy_score
from sklearn.utils.class_weight import compute_class_weight
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Conv1D, GlobalMaxPooling1D

def create_cnn_model(input_dim, activation='relu', dropout=0.5, kernel_size=5, optimizer='adam'):
    model = Sequential()
    model.add(Conv1D(filters=128, kernel_size=kernel_size, activation=activation, input_shape=(input_dim, 1)))
    model.add(GlobalMaxPooling1D())
    model.add(Dense(256, activation='relu'))
    model.add(Dropout(dropout))
    model.add(Dense(1, activation='softmax'))  # 2 output classes
    model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
    return model

def create_model(matrix, labels, number_of_features, balancing):
    # Convert labels to a numpy array
    labels = np.array(labels)

    # np.expand_dims(matrix, axis=1)
    matrix = matrix.toarray()
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(matrix, labels, test_size=0.25, random_state=42, stratify=labels)

    # Compute class weights based on the training labels
    class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
    class_weight_dict = dict(enumerate(class_weights))

    # Define the parameter grid for hyperparameter tuning
    parameters = {
        'batch_size': [32, 64],
        'epochs': [10, 15, 20],
        'dropout': [0.3, 0.5, 0.7],
        'kernel_size': [3, 5, 7],
        'optimizer': ['SGD', 'RMSprop', 'Adagrad', 'Adam'],
        'optimizer__learning_rate': [0.001, 0.01, 0.1, 0.2],
        'optimizer__momentum': [0.3, 0.5, 0.7]
    }

    # Wrap the Keras model with KerasClassifier for scikit-learn compatibility
    cnn = KerasClassifier(model=create_cnn_model, input_dim=number_of_features, batch_size=64, epochs=10, dropout=0.5, kernel_size=5, optimizer='Adam', verbose=0)
    # Initialize stratified k-fold cross-validation
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # Initialize a grid search for the best parameters based on the accuracy score
    clf = GridSearchCV(cnn, parameters, scoring='accuracy', cv=skf, n_jobs=-1, verbose=0)

    # Train the model with the training data and class weights
    clf.fit(X_train, y_train, class_weight=class_weight_dict)

    # Predict on the test set
    y_test_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_test_pred)
    classification_rep = classification_report(y_test, y_test_pred)

    # Print the results
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
    # Remove unnecesary TensorFlow warnings
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

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
            matrix_resampled, labels_resampled = smote.fit_resample(matrix, labels)
            clf, result = create_model(matrix, labels, number_of_features, "Class weights")
            clf_resampled, result_resampled = create_model(matrix_resampled, labels_resampled, number_of_features, "Oversampling")
            # Save the models
            with open(f"data/models/cnn_{set_name}_{number_of_features}.pickle", 'wb') as f:
                pickle.dump(clf, f)
            with open(f"data/models/cnn_resampled_{set_name}_{number_of_features}.pickle", 'wb') as f:
                pickle.dump(clf_resampled, f)
            # Store the results
            results.append(result)
            results.append(result_resampled)

    # Convert results to DataFrame
    results_df = pd.DataFrame(results)

    # Print the table of accuracy scores
    print(results_df[['Set name', 'Number of features', 'Class balancing', 'Training accuracy', 'Test accuracy']])

    # Write the results to a CSV file
    results_df.to_csv('data/cnn_results.csv', index=False)
