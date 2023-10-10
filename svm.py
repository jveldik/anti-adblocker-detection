import csv
import pickle
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Load the saved matrices and feature sets
def load_data(set_name, numer_of_features):
    labels = []
    with open("data/labeled_urls.csv", mode = 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[1] == "True":
                labels.append(True)
            elif row[1] == "False":
                labels.append(False)
    with open(f"data/matrices/{set_name}_{numer_of_features}.pickle", 'rb') as f:
        matrix = pickle.load(f)
    return labels, matrix

# Change set_name and numer_of_features as needed
set_name = "all"
numer_of_features = 10000
# Load feature matrix and labels
labels, matrix = load_data(set_name, numer_of_features)
# Split the data into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(matrix, labels, test_size=0.2, random_state=42)

# Initialize the SVM classifier
clf = svm.SVC()

# Train the classifier on the training data
clf.fit(X_train, y_train)

# Make predictions on the test data
y_pred = clf.predict(X_test)

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)

# Generate a classification report
classification_rep = classification_report(y_test, y_pred)
print("Classification Report:\n", classification_rep)
