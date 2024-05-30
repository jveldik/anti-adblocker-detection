import os
import pickle
import esprima
import csv

def extract_features_from_AST(node, feature_set, set_name, number_of_features):
    

def extract_features_from_url(url_dir, feature_set, set_name):
    for dir in url_dir:
        if dir.endswith(".js"):
            with open(f"{url_dir}/{dir}", 'r', encoding='utf-8') as f:
                script = f.read()
            try:
                ast = esprima.parseScript(script)
            except Exception as e:
                with open('parsing_errors.log', 'a') as error_log:
                    error_log.write(f"Error parsing JavaScript code with {url}/{dir}: {e}\n")
                continue
            return extract_features_from_AST(getattr(ast, 'body'), feature_set, set_name, number_of_features)

def save_results(urls, labels):
    with open("data/model_labeled_urls.csv", "a", newline='') as file:
        writer = csv.writer(file)
        for url, label in zip(urls, labels):
            writer.writerow([url, label])

# Change model_name, set_name and number_of_features as needed
modelname = "svm_initial"
set_name = "identifier"
number_of_features = 1000

# Load the model to predict the labels
with open(f"data/models/{modelname}_{set_name}_{number_of_features}.pickle", 'rb') as f:
    model = pickle.load(f)

# Load the features the model uses
with open(f"data/feature_sets/{set_name}_{number_of_features}.pickle", 'rb') as f:
    feature_set = pickle.load(f)

urls = []
features_list = []

for url_dir in os.listdir("data/scripts"):
    url = os.path.basename(url_dir)
    if url == ".gitkeep":
        continue
    features = extract_features_from_url(url_dir, feature_set, set_name, number_of_features)
    label = model.predict([features])

labels = model.predict(features_list)
save_results(urls, labels)