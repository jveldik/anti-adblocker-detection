from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense

# Define the CNN architecture
def build_cnn_model(input_shape):
    model = Sequential([
        Conv1D(filters=32, kernel_size=3, activation='relu', input_shape=input_shape),
        MaxPooling1D(pool_size=2),
        Conv1D(filters=64, kernel_size=3, activation='relu'),
        MaxPooling1D(pool_size=2),
        Flatten(),
        Dense(128, activation='relu'),
        Dense(1, activation='sigmoid')  # Output layer for binary classification
    ])
    return model

# Compile the CNN model
def compile_cnn_model(model):
    model.compile(
        optimizer='adam',          # Optimization algorithm
        loss='binary_crossentropy',  # Binary classification loss
        metrics=['accuracy']       # Evaluation metric
    )
    return model

feature_vector_length = 100
input_shape = (feature_vector_length, 1)  # Input shape for 1D CNN

# Build and compile the CNN model
cnn_model = build_cnn_model(input_shape)
compiled_cnn_model = compile_cnn_model(cnn_model)

# Display a summary of the model architecture
compiled_cnn_model.summary()
