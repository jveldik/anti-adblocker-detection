# anti-adblocker-detection

The goal of this project is to create a method to accuratally detect anti adblockers on the web. Here this is done by first scraping websites from the Alexa top 1 million websites. The scripts and screenshots are stored from all english websites. Some website will also be given an indication on whether they are using an adblocker based on keywords/phrases in the page source of the website.
```
python data_generation <num_urls>
```
It is important that labels are accurate, so to ensure that, manual labeling is needed. This is automated as much as possible, to speed up the process. All true labels and the same amount of false labels are manually labeled. This way the labeling is kept to a minimum.
```
python label_urls.py <filename>
```
To train a model, features are needed. In this project features are extracted from the javascript scripts present in the page source of a url. All features are stored in a folder, so that they can easily be used.
```
python feature_extraction.py <filename>
```
From the features a feature set has to be created, which the model will use to label urls. Several feature sets are created based on identifiers, literals or both of these. There is also a variety in size between the feature sets. The features in the set are chosen based on  a chi-squared test scoring function. 
```
python feature_set_creation.py <filename>
```
Now that we have feature sets and data models can be trained. In this project a svm and a cnn model are used.
```
python svm_model.py <filename> <modelname> <set_name> <number_of_features>
```
```
python cnn_model.py <filename> <modelname> <set_name> <number_of_features>
```
Finally, there is also a script to run a model on all the data that is collected. This will result in a list of the urls that are stored, with a label given by the model indicating the use of an anti adblocker. 
```
python run_model.py <filename> <modelname> <set_name> <number_of_features>
```
