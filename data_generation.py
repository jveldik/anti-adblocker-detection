import csv
import pickle
import os.path
from tkinter import messagebox
from selenium import webdriver

# Load the firefox profile with extensions
profile = webdriver.FirefoxProfile("5jqn9t8w.blockerProfile")
# Set up the Selenium firefox browser
driver = webdriver.Firefox(profile)
driver.maximize_window()

# Make list to save all results
if os.path.exists("data/top5000.pickle"):
    with open("data/top5000.pickle", "rb") as f:
        top5000 = pickle.load(f)
else:
    top5000 = []

# Load the top 5000 urls that have not been loaded yet
with open("data/top-1m.csv", "r") as f:
    reader = csv.reader(f)
    urls = [row[1] for i, row in enumerate(reader) if i >= len(top5000) and i < 5000]

# Loop over the URLs
for url in urls:           
    # Use Selenium to load the URL and capture the HTTP requests and responses
    driver.get(url)
    answer = messagebox.askyesnocancel(title="Label site", message="Does this site use an anti adblocker?", default="no")
    if answer == None:
        # Save the dictionary
        with open("data/top5000.pickle", 'wb') as f:
            pickle.dump(top5000, f)
        # Quit the selenium instance
        driver.quit()
        break
    # Save HTML page source
    pageSource = driver.page_source
    with open(f"data/page_sources/{url}.html", 'w') as f:
        f.write(pageSource) 
    # Save screenshot
    driver.save_screenshot(f"data/screenshots/{url}.png")
    top5000.append(url, answer)