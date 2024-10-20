import pickle
import numpy as np
import pandas as pd
from imblearn.over_sampling import RandomOverSampler
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import classification_report
from sklearn.utils.class_weight import compute_class_weight
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Conv1D, GlobalMaxPooling1D

# Define the CNN model
def create_cnn_model(input_dim):
    model = Sequential()
    model.add(Conv1D(filters=128, kernel_size=5, activation='relu', input_shape=(input_dim, 1)))
    model.add(GlobalMaxPooling1D())
    model.add(Dense(256, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(2, activation='softmax'))  # 2 output classes
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

def create_model(matrix, labels, resampled):
    # Reshape matrix for CNN input
    matrix = np.expand_dims(matrix, axis=2)

    X_train, X_test, y_train, y_test = train_test_split(matrix, labels, test_size=0.25, random_state=42, stratify = labels)

    # Perform stratified k-fold cross-validation
    skf = StratifiedKFold(n_splits=5)
    cross_val_predictions = []
    cross_val_scores = []

    # Compute class weights
    if not resampled:
        labels_categorical = np.argmax(labels, axis=1)
        class_weights = compute_class_weight('balanced', classes=[0, 1], y=labels_categorical)
        class_weight_dict = {0: class_weights[0], 1: class_weights[1]}

    for train_index, test_index in skf.split(matrix, np.argmax(labels, axis=1)):
        X_train, X_test = matrix[train_index], matrix[test_index]
        y_train, y_test = labels[train_index], labels[test_index]
        
        model = create_cnn_model(number_of_features)
        if resampled:
            model.fit(X_train, y_train, epochs=10, batch_size=32, verbose=1)
        else:
            model.fit(X_train, y_train, epochs=10, batch_size=32, verbose=1, class_weight=class_weight_dict)
        
        y_pred = model.predict(X_test)
        cross_val_predictions.extend(np.argmax(y_pred, axis=1))
        score = model.evaluate(X_test, y_test, verbose=0)[1]  # accuracy score
        cross_val_scores.append(score)

    # Generate a classification report
    y_true = np.argmax(labels, axis=1)
    classification_rep = classification_report(y_true, cross_val_predictions)
    
    print("Cross-validation accuracy scores:", cross_val_scores)
    print("Mean cross-validation accuracy:", np.mean(cross_val_scores))
    print("Classification Report:\n", classification_rep)

    return model, cross_val_scores, classification_rep

if __name__ == "__main__":
    df = pd.read_csv("data/stored_urls.csv")
    labels = df['manual'].dropna().tolist()
    # Convert labels to categorical (one-hot encoding)
    labels = tf.keras.utils.to_categorical(labels)
    results = []
    results_resampled = []
    oversampler = RandomOverSampler(sampling_strategy='auto', random_state=42)
    
    for set_name in ["all", "identifier", "literal"]:
        for number_of_features in [100, 1000, 10000]:
            # Load feature matrix
            with open(f"data/matrices/{set_name}_{number_of_features}.pickle", 'rb') as f:
                matrix = pickle.load(f)
            matrix = matrix.toarray()
            matrix_resampled, labels_resampled = oversampler.fit_resample(matrix, labels)
            matrix_resampled = np.expand_dims(matrix_resampled, axis=2)
            labels_resampled = tf.keras.utils.to_categorical(labels_resampled)
            model, cross_val_scores, classification_rep = create_model(matrix, labels, True)
            model_resampled, cross_val_scores_resampled, classification_rep_resampled = create_model(matrix_resampled, labels_resampled, False)
            # Save the models
            with open(f"data/models/cnn_{set_name}_{number_of_features}.pickle", 'wb') as f:
                pickle.dump(model, f)
            with open(f"data/models/cnn_resampled_{set_name}_{number_of_features}.pickle", 'wb') as f:
                pickle.dump(model_resampled, f)
            # Store the results
            result = {
                'set_name': set_name,
                'number_of_features': number_of_features,
                'cross_val_scores': cross_val_scores,
                'mean_accuracy': np.mean(cross_val_scores),
                'classification_report': '\n' + classification_rep
            }
            results.append(result)
            result_resampled = {
                'set_name': set_name,
                'number_of_features': number_of_features,
                'cross_val_scores': cross_val_scores_resampled,
                'mean_accuracy': np.mean(cross_val_scores_resampled),
                'classification_report': '\n' + classification_rep_resampled
            }
            results_resampled.append(result_resampled)

    # Convert results to a DataFrames
    results_df = pd.DataFrame(results)
    results_resampled_df = pd.DataFrame(results_resampled)

    # Print the tables of accuracy scores
    print(results_df[['set_name', 'number_of_features', 'mean_accuracy']])
    print(results_resampled_df[['set_name', 'number_of_features', 'mean_accuracy']])

    # Write the results to a CSV file
    results_df.to_csv('data/cnn_results.csv', index=False)
    results_resampled_df.to_csv('data/cnn_resampled_results.csv', index=False)
