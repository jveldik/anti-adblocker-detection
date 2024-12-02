# anti-adblocker-detection

The goal of this project is to create a method to accuratally detect anti adblockers on the web. Here this is done by first scraping websites from the Alexa top 1 million websites. The scripts and screenshots are stored from all english websites. Some website will also be given an indication on whether they are using an adblocker based on keywords/phrases in the page source of the website. This is saved in a csv file.
```
python data_generation <num_urls>
```
It is important that labels are accurate, so to ensure that, manual labeling is needed. This is automated as much as possible, to speed up the process. All true labels and the same amount of false labels are manually labeled. This way the labeling is kept to a minimum. The labels are added as extra column to the csv file.
```
python label_urls.py
```
To train a model, features are needed. In this project features are extracted from the javascript scripts present in the page source of a url. All features are stored in a folder, so that they can easily be used.
```
python feature_extraction.py
```
From the features a feature set has to be created, which the model will use to label urls. Several feature sets are created based on identifiers, literals or both of these. There is also a variety in size between the feature sets. The features in the set are chosen based on a chi-squared test scoring function. 
```
python feature_set_creation.py
```
Now that we have feature sets and data models can be trained. In this project a svm, a cnn and a mlp model are used.
```
python svm_model.py
```
```
python cnn_model.py
```
```
python mlp_model.py
```
Finally, there is also a script to run the best models on all the data that is collected. This will result in a list of the urls that are stored, with a label given by the models indicating the use of an anti adblocker. This adds three column to the csv file.
```
python run_models.py
```
