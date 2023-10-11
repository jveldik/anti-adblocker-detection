import csv
import pickle
import tensorflow as tf
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from tensorflow import keras
from tensorflow.keras import layers

# Load the saved matrices and feature sets
def load_data(set_name, number_of_features):
    labels = []
    with open("data/labeled_urls.csv", mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[1] == "True":
                labels.append(True)
            elif row[1] == "False":
                labels.append(False)
    with open(f"data/matrices/{set_name}_{number_of_features}.pickle", 'rb') as f:
        matrix = pickle.load(f)
    return labels, matrix

# Change set_name and k as needed
set_name = "all"
number_of_features = 10000

# Load feature matrix and labels
labels, matrix = load_data(set_name, number_of_features)

# Convert the SciPy sparse matrix to a NumPy array
matrix = matrix.toarray()

# Split the data into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(matrix, labels, test_size=0.2, random_state=42)

# Create a simple neural network model
model = keras.Sequential()
model.add(layers.InputLayer(input_shape=(X_train.shape[1],)))
model.add(layers.Dense(64, activation='relu'))
model.add(layers.Dense(1, activation='sigmoid'))

# Compile the model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.2)

# Make predictions on the test data
y_pred = (model.predict(X_test) > 0.5).astype(int).flatten()

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)

# Generate a classification report
classification_rep = classification_report(y_test, y_pred)
print("Classification Report:\n", classification_rep)
