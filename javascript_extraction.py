import os
import requests
from bs4 import BeautifulSoup

# Function to fetch and process external JavaScript content
def fetch_external_js(url, source):
    if source.startswith('/'):
        url = f"{url}{source}"
    else:
        url = source
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    return ""

# Function to extract JavaScript code from HTML file
def extract_scripts(html_path):
    scripts = []
    with open(html_path, 'r', encoding='utf-8') as f:
        html_code = BeautifulSoup(f.read(), 'html.parser')
        url = "http://" + html_path.replace('data/page_sources/', '').replace('.html', '')
        script_tags = html_code.find_all("script")
        
        for source_tag in script_tags:
            source = source_tag.get('src')
            if source:
                script_content = fetch_external_js(url, source)
                if script_content:
                    scripts.append(script_content)
            else:
                scripts.append(source_tag.string)
    return scripts

page_sources_path = "data/page_sources/"
for file in os.listdir(page_sources_path):
    if file.endswith('.html'):
        html_path = os.path.join(page_sources_path, file)
        scripts = extract_scripts(html_path)
        # Make a folder
        url = file.replace('html', '')
        if not os.path.exists(f"data/scripts/{url}"):
            os.mkdir(f"data/scripts/{url}")
        for index, script in enumerate(scripts):
            with open(f"data/scripts/{url}/{index}.js", 'w', encoding='utf-8') as f:
                f.write(script)
