import csv
import os.path
import tkinter
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# Load the firefox profile with extensions
options = Options()
options.add_argument("-profile")
options.add_argument("5jqn9t8w.blockerProfile")
# options.set_preference('profile', "5jqn9t8w.blockerProfile")
# Set up the Selenium firefox browser
driver = webdriver.Firefox(options=options)
driver.maximize_window()

# Determine how many is already done
start = 0
if os.path.exists("data/top5000.csv"):
    with open("data/top5000.csv", "r") as f:
        start = sum(1 for line in f)-1
else:
    with open("data/top5000.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["URL", "usesAntiAdBlocker"])

# Load the top 5000 urls that have not been loaded yet
with open("data/top-1m.csv", "r") as f:
    reader = csv.reader(f)
    urls = [row[1] for i, row in enumerate(reader) if i >= start and i < 5000]

# Loop over the URLs
for url in urls:    
    try:       
        # Use Selenium to load the URL and capture the HTTP requests and responses
        driver.get(f"http://{url}")
        root = tkinter.Tk()
        root.wm_attributes("-topmost", 1)
        root.withdraw()
        answer = messagebox.askyesnocancel(title="Label site", message="Does this site use an anti adblocker?", default="no")
        if answer == None:
            # Quit the selenium instance
            driver.quit()
            break
        # Save HTML page source
        pageSource = driver.page_source
        with open(f"data/page_sources/{url}.html", 'w', encoding="utf-8") as f:
            f.write(pageSource) 
        # Save screenshot
        driver.save_screenshot(f"data/screenshots/{url}.png")
        # Save label
        with open('data/top5000.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([url, answer])
    except:
        print(f"There was an exception with {url}")
        with open('data/top5000.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([url, None])