import csv
import time
import pickle
import os.path
from selenium import webdriver
from selenium.webdriver.support.select import Select

def install_addon(self, path, temporary=None):
    # Usage: driver.install_addon('/path/to/adblocker.xpi')
    # ‘self’ refers to the “Webdriver” class
    # 'path' is absolute path to the addon that will be installed
    payload = {"path": path}
    if temporary:
        payload["temporary"] = temporary
    # The function returns an identifier of the installed addon.
    # This identifier can later be used to uninstall installed addon.
    return self.execute("INSTALL_ADDON", payload)["value"]

# Set up the Selenium firefox browser
driver = webdriver.Firefox()
driver.maximize_window()
original_window = driver.current_window_handle
# Path to the adblocker extension
extension_path = "adblock_plus-3.17.xpi"

# Install the adblocker extension
driver.install_addon(extension_path, temporary=True)
time.sleep(5)
# Do not allow acceptable ads
driver.switch_to.window(original_window)
driver.get("about:addons")
print("Opened tab")
time.sleep(2)
extensions_tab = driver.find_element("xpath", '//button[@data-l10n-id="addon-category-extension-title"]')
print("Found button")
extensions_tab.click()
print("Showed extensions")
dots = driver.find_element("xpath", '//button[@data-l10n-id="addon-options-button"]')
dots.click()
print("Pressed dots")
options = driver.find_element("xpath", '//panel-item[@data-l10n-id="preferences-addon-button"]')
options.click()
print("Pressed options")

time.sleep(5)
checkbox = driver.find_element("xpath", '//input[@id="acceptable-ads-allow"]')
checkbox.click()
print("Pressed checkbox")

# Make list to save all results
if os.path.exists("data/top5000.pickle"):
    with open("data/top5000.pickle") as f:
        top5000 = pickle.load(f)
else:
    top5000 = []

# Load the top 5000 urls that have not been loaded yet
with open("data/top-1m.csv", "r") as f:
    reader = csv.reader(f)
    urls = [row[1] for i, row in enumerate(reader) if i >= len(top5000) and i < 5000]

# Loop over the URLs
# for url in urls:           
#     # Use Selenium to load the URL and capture the HTTP requests and responses
#     driver.get(url)
#     har_file = ...

# Quit the selenium instance
driver.quit()

# Save the dictionary
with open("data/top5000.pickle", 'wb') as f:
    pickle.dump(top5000, f)