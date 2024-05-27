import csv
import os.path
import pickle
import re
import sys
from time import sleep
from langid.langid import LanguageIdentifier, model
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from urllib.parse import urlparse
from urlextract import URLExtract

def get_last_visited_url(model_name):
    if os.path.exists(f"data/last_visited_url_{model_name}.txt"):
        with open("data/last_visited_url.txt", "r") as file:
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
    session.headers.update({'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"})
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
    with open(f"data/scripts/{url}/source.txt", 'w', encoding='utf-8') as f:
        f.write(page_source)
    for index, source_tag in enumerate(script_tags):
        source = source_tag.get('src')
        if source:
            script_content = fetch_external_js(session, url, source)
            save_script(url, index, script_content)
        else:
            save_script(url, index, source_tag.string)

def extract_features(page_source, feature_set):
    
    return []

def uses_anti_adblocker(page_source, model_name):
    if model_name == "keywords":
        # List of common phrases and keywords indicating an anti-adblocker message
        anti_adblock_phrases = [
            'allow ads', 'ad blocker detected', 'adblock message', 'adblock notice',
            'adblock popup', 'adblock warning', 'adblocker alert', 'adblocker detected',
            'ads are how we support', 'disable ad block', 'disable adblock',
            'disable adblock', 'disable your blocking software',
            'disable your browser extension', 'disable your extension',
            'disable your filter', 'enable ads', 'support us by disabling',
            'support us by turning off', 'turn off adblocker', 'turn off to continue',
            'turn off your blocker', 'turn off your extension', 'turn off your filter',
            'we noticed you are using an adblocker', 'whitelist our page',
            'whitelist our site', 'whitelist this page', 'whitelist us', 'your ad blocker',
            'your ad filter', 'your adblocker', 'your content blocker'
        ]
        
        # Convert the page source to lowercase to ensure case-insensitive matching
        page_source_lower = page_source.lower()
        
        # Check if any of the anti-adblocker phrases are in the page source
        for phrase in anti_adblock_phrases:
            if phrase in page_source_lower:
                return True
        return False
    else:
        feature_set = pickle.load(f"all_10000.pickle")
        features = extract_features(page_source, feature_set)
        model = pickle.load(f"models/model_name.pickle")
        return model.predict(features)

def no_anti_adblocker(page_source):
    if re.search(r'\b(ad ?-?_?block)', page_source.lower()):
        return False
    return True

def is_english(page_source):
    identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
    lang, prob = identifier.classify(page_source)
    return lang == 'en'

def visit_url(driver, session, url, model_name, counterexamples_needed):
    try:
        print(f"Visiting {url}")
        # Use Selenium to load the URL
        driver.get(f"http://{url}")
        # Wait for the page to load
        while driver.execute_script("return document.readyState") != "complete":
            sleep(5)
        sleep(5)
        
        current_url = urlparse(driver.current_url).netloc
        page_source = driver.page_source

        if is_english(page_source):
            if uses_anti_adblocker(page_source, model_name):
                print("Anti adblocker found!")
                # Check if current url is already stored
                if os.path.exists(f"data/screenshots/{current_url}.png"):
                    print(f"{current_url} was already stored")
                else:
                    # Save scripts
                    extract_scripts(session, page_source, current_url)
                    # Save screenshot
                    driver.save_screenshot(f"data/screenshots/{current_url}.png")
                    print(f"{current_url} is stored")
                # Save the current url
                with open(f"data/stored_urls_{model_name}.txt", "a", newline='') as file:
                    file.write(f"{current_url}, True\n")
                counterexamples_needed += 1
            if counterexamples_needed > 0 and no_anti_adblocker(page_source):
                print("No anti adblocker found!")
                # Check if current url is already stored
                if os.path.exists(f"data/screenshots/{current_url}.png"):
                    print(f"{current_url} was already stored")
                else:
                    # Save scripts
                    extract_scripts(session, page_source, current_url)
                    # Save screenshot
                    driver.save_screenshot(f"data/screenshots/{current_url}.png")
                    print(f"{current_url} is stored")
                # Save the current url
                with open(f"data/stored_urls_{model_name}.txt", "a", newline='') as file:
                    file.write(f"{current_url}, False\n")
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except:
        print(f"{url} caused an exception")

if __name__ == "__main__":
    n = len(sys.argv)
    if n > 0:
        num_urls = sys.argv[1]
    if n == 1:
        model_name = "keywords"
    elif n == 2:
        model_name = sys.argv[2]
    else:
        print("The first argument should be the number of urls you want to search")
        print("(Optional) The second argument is the name of the model, you want to use to classify the urls")
        exit()

    last_visited_url = get_last_visited_url(model_name)
    driver = create_driver()
    session = create_session()
    try:
        counterexamples_needed = 0
        urls = []
        with open("data/top-1m.csv", "r") as file:
            reader = csv.reader(file)
            for i, row in enumerate(reader):
                if int(row[0]) > num_urls:
                    break
                if int(row[0]) > last_visited_url:
                    visit_url(driver, session, row[1], counterexamples_needed)
                    last_visited_url = int(row[0])
    except KeyboardInterrupt:
        print("You stopped the script")
    finally:
        # Quit the selenium instance
        driver.quit()

        # Save number of visited urls
        with open(f"data/last_visited_url_{model_name}.txt", "w") as file:
            file.write(str(last_visited_url))

        # Remove duplicate urls
        url_set = set()
        with open(f"data/stored_urls_{model_name}.txt", 'r') as file:
            for line in file:
                url = line.strip()
                if url:
                    url_set.add(url)
        with open(f"data/stored_urls_{model_name}.txt", 'w') as file:
            for url in url_set:
                file.write(url + '\n')

        # Print the number of unique stored urls
        nr_stored_urls = len(url_set)
        print(f"{nr_stored_urls} urls are stored")