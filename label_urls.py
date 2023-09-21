import csv
from easygui import *
import os.path

def get_urls_to_label():
    # Check if there are already some urls labeled
    if os.path.exists("data/labeled_urls.csv"):
        # Read the last URL from labeled_urls.csv
        with open("data/labeled_urls.csv", mode='r', newline='') as file:
            reader = csv.reader(file)
            last_labeled_url = [row for row in reader][-1][0]
        # Read the URLs from stored_urls.csv, starting after the last labeled URL
        with open("data/stored_urls.csv", mode='r', newline='') as file:
            reader = csv.reader(file)
            while next(reader)[0] != last_labeled_url:
                continue
            return [row for row in reader if row[1]]
    else:
        # Make a csv file to store labeled urls
        with open("data/labeled_urls.csv", "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["URL", "AntiAdblocker"])
        with open("data/stored_urls.csv", mode='r', newline='') as file:
            reader = csv.reader(file)
            # Skip the header
            next(reader)
            return [row for row in reader if row[1]]

def make_gui():
    return "gui"

def get_label(gui, url, redirect):
    return True

def save_labels(urls, labels):
    with open("data/labeled_urls.csv", "a", newline='') as file:
        writer = csv.writer(file)
        for url, label in zip(urls, labels):
            writer.writerow([url[0], label])

urls = get_urls_to_label()
gui = make_gui()
labels = []
for url, redirect in urls:
    labels.append(get_label(gui, url, redirect))    
save_labels(urls, labels)


