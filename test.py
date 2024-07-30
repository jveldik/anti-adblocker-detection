import pickle
import pandas as pd

df = pd.read_csv("data/stored_urls.csv")
for url in df['url'].to_list():
    with open(f'data/features/{url}.pickle', 'rb') as f:
        features = pickle.load(f)
    print(len(features))
    features = features[1:]
    print(len(features))
    # with open(f'data/features/{url}.pickle', 'wb') as f:
    #     pickle.dump(features, f)
    break