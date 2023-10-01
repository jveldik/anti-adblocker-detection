import csv
import multiprocessing
import os.path
from time import sleep
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from urllib.parse import urlparse
from urlextract import URLExtract

NR_TOP_URLS = 5000

def get_nr_visited_urls():
    if os.path.exists("data/nr_visited_urls.txt"):
        with open("data/nr_visited_urls.txt", "r") as file:
            content = file.read()
            return int(content)
    else:
        return 0

def create_driver():
    # Load the firefox profile with adblocker extension
    options = Options()
    options.add_argument('-headless')
    options.add_argument("-profile")
    options.add_argument("883r2o43.blockerProfile")
    # Set up the Selenium firefox browser
    driver = webdriver.Firefox(options=options)
    driver.maximize_window()
    return driver

def create_session():
    session = requests.Session()
    session.headers.update({'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0"})
    return session

def fetch_external_js(session, url, source):
    extractor = URLExtract()
    if extractor.has_urls(source):
        while source.startswith('/'):
            source = source[1:]
        if source.startswith("http"):
            url = source
        else:
            url = f"https://{source}"
    else:
        if source.startswith('/'):
            url = f"https://{url}{source}"
        else:
            url = f"https://{url}/{source}"
    try:
        response = session.get(url, timeout=5)
        response.raise_for_status()
        return response.text
    except KeyboardInterrupt:
        raise KeyboardInterruptException()
    except:
        print(f"Error fetching {url} from the source: {source}")

def save_script(url, index, script):
    if script:
        with open(f"data/scripts/{url}/{index}.js", 'w', encoding='utf-8') as f:
            f.write(script)

# Function to extract JavaScript code from HTML code
def extract_scripts(session, page_source, url):
    soup = BeautifulSoup(page_source, 'lxml')
    script_tags = soup.find_all("script")
    # Create folder for storing scripts
    os.mkdir(f"data/scripts/{url}")
    for index, source_tag in enumerate(script_tags):
        source = source_tag.get('src')
        if source:
            script_content = fetch_external_js(session, url, source)
            save_script(url, index, script_content)
        else:
            save_script(url, index, source_tag.string)

def visit_url(driver, session, url):
    try:
        print(f"Visiting {url}")
        # Use Selenium to load the URL
        driver.get(f"http://{url}")
        # Wait for the page to load
        while driver.execute_script("return document.readyState") != "complete":
            sleep(5)
        sleep(5)
        
        current_url = urlparse(driver.current_url).netloc
        # Check if current url is already visited
        if os.path.exists(f"data/screenshots/{current_url}.png"):
            print(f"{current_url} was already stored")
        else:
            # Save scripts
            page_source = driver.page_source
            extract_scripts(session, page_source, current_url)
            # Save screenshot
            driver.save_screenshot(f"data/screenshots/{current_url}.png")
            # Save the current url
            with open("data/stored_urls.txt", "a", newline='') as file:
                file.write(f"{current_url}\n")
            print(f"{current_url} is stored")
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except:
        print(f"{url} caused an exception")
  
nr_visited_urls = get_nr_visited_urls()
driver = create_driver()
session = create_session()

# Load the top URLs that have not been stored yet
with open("data/top-1m.csv", "r") as file:
    reader = csv.reader(file)
    urls = [row[1] for i, row in enumerate(reader) if i >= nr_visited_urls and i < NR_TOP_URLS]

try:
    # Loop over the URLs
    for url in urls:
        visit_url(driver, session, url)
        nr_visited_urls += 1
except KeyboardInterrupt:
    print("You stopped the script")
finally:
    # Quit the selenium instance
    driver.quit()

    # Save number of visited urls
    with open("data/nr_visited_urls.txt", "w") as file:
        file.write(str(nr_visited_urls))

    # Print the number of stored urls
    with open("data/stored_urls.txt", 'r') as file:
        nr_stored_urls = sum(1 for line in file if line.strip())
        print(f"{nr_stored_urls} urls are stored")