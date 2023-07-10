import csv
import os.path
import tkinter
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# Constants
NR_TOP_URLS = 5000

# Load the firefox profile with adblocker extension
options = Options()
options.add_argument("-profile")
options.add_argument("883r2o43.blockerProfile")
# Set up the Selenium firefox browser
driver = webdriver.Firefox(options=options)
driver.maximize_window()

# Determine how many URLs are already labeled
nr_labels = 0
if os.path.exists("data/labeled_urls.csv"):
    with open("data/labeled_urls.csv", "r") as file:
        nr_labels = sum(1 for line in file)-1
else:
    with open("data/labeled_urls.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["URL", "usesAntiAdBlocker"])

# Load the top URLs that have not been labeled yet
with open("data/top-1m.csv", "r") as file:
    reader = csv.reader(file)
    urls = [row[1] for i, row in enumerate(reader) if i >= nr_labels and i < NR_TOP_URLS]

# Loop over the URLs
for url in urls:    
    try:       
        # Use Selenium to load the URL and capture the HTTP requests and responses
        driver.get(f"http://{url}")
        # Ask for label
        root = tkinter.Tk()
        root.wm_attributes("-topmost", 1)
        root.withdraw()
        answer = messagebox.askyesnocancel(title="Label site", message="Does this site use an anti adblocker?", default="no")
        # Stop the loop
        if answer == None:
            break
        # Save HTML page source
        pageSource = driver.page_source
        with open(f"data/page_sources/{url}.html", 'w', encoding="utf-8") as f:
            f.write(pageSource) 
        # Save screenshot
        driver.save_screenshot(f"data/screenshots/{url}.png")
        # Save label
        with open('data/labeled_urls.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([url, answer])
    except:
        print(f"There was an exception with {url}")
        with open('data/labeled_urls.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([url, None])

# Quit the selenium instance
driver.quit()

# Print the number of labeled URLs
false_count = 0
true_count = 0
empty_count = 0
total_rows = 0

with open("data/labeled_urls.csv", "r") as file:
    csv_reader = csv.reader(file)
    header = next(csv_reader)  # Skip the header row
    for row in csv_reader:
        total_rows += 1
        if len(row) > 1:
            value = row[1]
            if value == 'False':
                false_count += 1
            elif value == 'True':
                true_count += 1
            elif not value:
                empty_count += 1

print(f"You have labeled {total_rows} URLs in total, {true_count} URLs use anti adblockers, {false_count} URLs do not use anti adblockers and {empty_count} URLs gave errors.")