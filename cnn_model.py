import os
import pickle
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from keras_tuner import BayesianOptimization 
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Conv1D, GlobalMaxPooling1D
from tensorflow.keras.optimizers import Adam, RMSprop, SGD

def create_cnn_model(hp, input_dim, class_weights):
    model = Sequential()
    num_layers = hp.Choice("num_layers", values=[1, 2, 3])
    dense_dropout = hp.Choice('dense_dropout', values=[0.3, 0.5, 0.7])
    optimizer_choice = hp.Choice("optimizer", values=["adam", "RMSprop", "SGD"])
    learning_rate = hp.Choice("learning_rate", values=[1e-3, 1e-4, 1e-5])
    if optimizer_choice == "adam":
        optimizer = Adam(learning_rate=learning_rate)
    elif optimizer_choice == "RMSprop":
        optimizer = RMSprop(learning_rate=learning_rate)
    else:
        optimizer = SGD(learning_rate=learning_rate)

    for i in range(num_layers):
        filters = hp.Choice(f'filters_{i}', values=[64, 128, 256])
        kernel_size = hp.Choice(f'kernel_size_{i}', values=[3, 5, 7])
        dropout = hp.Choice(f'dropout_{i}', values=[0.3, 0.5, 0.7])
        # Input shape only needed for the first layer
        if i == 0:
            model.add(Conv1D(filters=filters, kernel_size=kernel_size, activation='relu', input_shape=(input_dim, 1)))
        else:
            model.add(Conv1D(filters=filters, kernel_size=kernel_size, activation='relu'))
        model.add(Dropout(dropout))
    
    model.add(GlobalMaxPooling1D())
    model.add(Dense(units=hp.Int('dense_units', min_value=128, max_value=512, step=128), activation='relu'))
    model.add(Dropout(dense_dropout))
    model.add(Dense(1, activation='sigmoid'))  # Binary classification output
    model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
    return model

def create_model(matrix, labels, number_of_features, balancing):
    # Reshape labels and matrix for CNN input
    labels = np.array(labels)
    matrix = matrix.toarray()

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(matrix, labels, test_size=0.25, random_state=42, stratify=labels)

    X_train = X_train.astype("int32")
    y_train = y_train.astype("int32")

    # Compute class weights based on the training labels
    class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
    # class_weights_dict = dict(enumerate(class_weights))

    # Initialize the tuner
    tuner = BayesianOptimization(
        lambda hp: create_cnn_model(hp, number_of_features, class_weights), 
        objective='val_accuracy',
        overwrite=True,
        directory='.hidden_tuning',  # Hidden folder by prefixing with "."
        project_name='temp_tuning'
    )

    # Run the hyperparameter search
    tuner.search(
        X_train, 
        y_train, 
        epochs=100, 
        validation_split=0.2, 
        callbacks=[EarlyStopping(monitor='val_loss', patience=3)], 
        verbose=0
    )

    # Get the best model
    clf = tuner.get_best_models(num_models=1)[0]
    best_parameters = tuner.get_best_hyperparameters(num_trials=1)[0].values
    training_accuracy = clf.evaluate(X_train, y_train, verbose=0)[1]

    # Predict on the test set
    y_test_pred = (clf.predict(X_test) > 0.5).astype("int32").flatten()
    test_accuracy = accuracy_score(y_test, y_test_pred)
    classification_rep = classification_report(y_test, y_test_pred, zero_division=1)

    # Print the results
    result = {
            'Set name': set_name,
            'Number of features': number_of_features,
            'Class balancing': balancing,
            'Best parameters': best_parameters,
            'Training accuracy': training_accuracy,
            'Test accuracy': test_accuracy,
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
