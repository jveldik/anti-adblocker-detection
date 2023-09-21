import csv
import os.path
from time import sleep
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from urllib.parse import urlparse

# Constants
NR_TOP_URLS = 5000

def get_number_of_stored_urls():
    # Determine how many URLs are already stored
    if os.path.exists("data/stored_urls.csv"):
        with open("data/stored_urls.csv", "r") as file:
            return sum(1 for line in file)-1
    else:
        with open("data/stored_urls.csv", "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["URL", "Redirect"])
            return 0

def create_driver():
    # Load the firefox profile with adblocker extension
    options = Options()
    options.add_argument("-profile")
    options.add_argument("883r2o43.blockerProfile")
    # Set up the Selenium firefox browser
    driver = webdriver.Firefox(options=options)
    driver.maximize_window()
    return driver

def create_session():
    session = requests.Session()
    session.timeout = 5
    session.headers.update({'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0"})
    return session

def fetch_external_js(session, url, source):
    if source.startswith('/'):
        url = f"{url}{source}"
    else:
        url = source
    try:
        response = session.get(url)
        response.raise_for_status()
        return response.text
    except:
        print(f"Error fetching {url}")
        return ""

def save_script(url, index, script):
    if script:
        with open(f"data/scripts/{url}/{index}.js", 'w', encoding='utf-8') as f:
            f.write(script)

# Function to extract JavaScript code from HTML code
def extract_scripts(session, page_source, url, current_url):
    soup = BeautifulSoup(page_source, 'lxml')
    script_tags = soup.find_all("script")
    # Create folder for storing scripts
    os.mkdir(f"data/scripts/{url}")
    for index, source_tag in enumerate(script_tags):
        source = source_tag.get('src')
        if source:
            script_content = fetch_external_js(session, current_url, source)
            save_script(url, index, script_content)
        else:
            save_script(url, index, source_tag.string)

def visit_url(driver, session, url):
    try:
        # Use Selenium to load the URL
        driver.get(f"http://{url}")
        # Wait for the page to load
        sleep(5)
        while driver.execute_script("return document.readyState") != "complete":
            sleep(1)
    except:
        with open("data/stored_urls.csv", "a", newline='') as file:
            writer = csv.writer(file)
            writer.writerow([url, ""])
        return False
    # Save scripts
    page_source = driver.page_source
    current_url = urlparse(driver.current_url).netloc
    extract_scripts(session, page_source, url, current_url)
    # Save screenshot
    driver.save_screenshot(f"data/screenshots/{url}.png")
    # Save the current url
    with open("data/stored_urls.csv", "a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([url, current_url])
    return True
  
nr_urls = get_number_of_stored_urls()
driver = create_driver()
session = create_session()

# Load the top URLs that have not been stored yet
with open("data/top-1m.csv", "r") as file:
    reader = csv.reader(file)
    urls = [row[1] for i, row in enumerate(reader) if i >= nr_urls and i < NR_TOP_URLS]

# Loop over the URLs
for url in urls:
    print(f"Storing {url}")
    nr_urls += 1
    if visit_url(driver, session, url):
        print(f"URL #{nr_urls} is stored. ({url})")
    else:
        print(f"URL #{nr_urls} caused an exception. ({url})")

# Quit the selenium instance
driver.quit()