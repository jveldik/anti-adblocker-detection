import os
import requests
from bs4 import BeautifulSoup

# Function to fetch and process external JavaScript content
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

# Function to extract JavaScript code from HTML file
def extract_scripts(session, html_path):
    scripts = []
    with open(html_path, 'r', encoding='utf-8') as f:
        html_code = BeautifulSoup(f.read(), 'html.parser')
        url = "http://" + html_path.replace('data/page_sources/', '').replace('.html', '')
        script_tags = html_code.find_all("script")
        for source_tag in script_tags:
            source = source_tag.get('src')
            if source:
                script_content = fetch_external_js(session, url, source)
                if script_content:
                    scripts.append(script_content)
            else:
                scripts.append(source_tag.string)
    return scripts

page_sources_path = "data/page_sources/"
session = requests.Session()
session.headers.update({'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0"})
for dir in os.listdir(page_sources_path):
    url = dir.replace('.html', '')
    if not os.path.exists(f"data/scripts/{url}") and dir.endswith('.html'):
        html_path = os.path.join(page_sources_path, dir)
        print(f"Extracting scripts from {url}")
        scripts = extract_scripts(session, html_path)
        # Make a folder
        print(f"Saving scripts from {url}")
        os.mkdir(f"data/scripts/{url}")
        for index, script in enumerate(scripts):
            if script:
                with open(f"data/scripts/{url}/{index}.js", 'w', encoding='utf-8') as f:
                    f.write(script)
        print(f"Saved scripts from {url}")
