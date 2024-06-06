import csv
import pickle
import sys
import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Conv1D, GlobalMaxPooling1D

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
        number_of_features = int(sys.argv[4])
    else:
        print("The first argument should be the filename")
        print("The second argument should be the modelname")
        print("The third argument should be the set name")
        print("The fourth argument should be the number of features")
        exit()

    # Load feature matrix and labels
    labels, matrix = load_data(filename, set_name, number_of_features)
    labels = np.array(labels)

    # Convert sparse matrix to dense matrix
    if not isinstance(matrix, np.ndarray):
        matrix = matrix.toarray()

    # Standardize features
    scaler = StandardScaler()
    matrix = scaler.fit_transform(matrix)

    # Convert labels to categorical (one-hot encoding)
    labels = tf.keras.utils.to_categorical(labels)

    # Define the CNN model
    def create_cnn_model(input_dim):
        model = Sequential()
        model.add(Conv1D(filters=128, kernel_size=5, activation='relu', input_shape=(input_dim, 1)))
        model.add(GlobalMaxPooling1D())
        model.add(Dense(256, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(2, activation='softmax'))  # 2 output classes
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        return model

    # Reshape matrix for CNN input
    matrix = np.expand_dims(matrix, axis=2)

    # Perform stratified k-fold cross-validation
    skf = StratifiedKFold(n_splits=5)
    cross_val_predictions = []

    for train_index, test_index in skf.split(matrix, np.argmax(labels, axis=1)):
        X_train, X_test = matrix[train_index], matrix[test_index]
        y_train, y_test = labels[train_index], labels[test_index]
        
        model = create_cnn_model(input_dim=number_of_features)
        model.fit(X_train, y_train, epochs=10, batch_size=32, verbose=1)
        
        y_pred = model.predict(X_test)
        cross_val_predictions.extend(np.argmax(y_pred, axis=1))

    # Generate a classification report
    y_true = np.argmax(labels, axis=1)
    classification_rep = classification_report(y_true, cross_val_predictions)
    print("Classification Report:\n", classification_rep)

    # Save the model
    with open(f"data/models/{modelname}_{set_name}_{number_of_features}.pickle", 'wb') as f:
        pickle.dump(model, f)
