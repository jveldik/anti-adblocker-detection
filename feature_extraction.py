import os
import requests
from bs4 import BeautifulSoup
from slimit.parser import Parser
from slimit.visitors.nodevisitor import ASTVisitor

# Create a visitor class for feature extraction
class FeatureExtractor(ASTVisitor):
    def __init__(self):
        self.feature_sets = {
            'all': {},
            'literal': {},
            'keyword': {}
        }

    def visit_Object(self, node):
        # Visit object literal
        for prop in node:
            left, right = prop.left, prop.right
            #print 'Property key=%s, value=%s' % (left.value, right.value)
            # Visit all children in turn
            self.visit(prop)

# Function to fetch and process external JavaScript content
def fetch_external_js(url, source):
    print(url)
    print(source)
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
    scripts = ""
    with open(html_path, 'r', encoding='utf-8') as f:
        html_code = BeautifulSoup(f.read(), 'html.parser')
        url = "http://" + html_path.replace('data/page_sources/', '').replace('.html', '')
        script_tags = html_code.find_all("script")
        
        for source_tag in script_tags:
            source = source_tag.get('src')
            if source:
                script_content = fetch_external_js(url, source)
                if script_content:
                    scripts += script_content + "\n"
            else:
                scripts += f"{source_tag.string}\n"
    print(scripts)
    return scripts

# Function to extract features from JavaScript code
def extract_features(scripts):
    parser = Parser()
    tree = parser.parse(scripts)
    
    extractor = FeatureExtractor()
    extractor.visit(tree)
    
    return extractor.feature_sets

# Iterate through HTML files and extract features
page_sources_path = "data/page_sources/"
for file in os.listdir(page_sources_path):
    if file.endswith('.html'):
        html_path = os.path.join(page_sources_path, file)
        scripts = extract_scripts(html_path)
        feature_sets = extract_features(scripts)
        print(f"Features extracted from {file}:")
        for name, features in feature_sets.items():
            print(name, features)
        break