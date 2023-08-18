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

# Function to extract features from JavaScript code
def extract_features(parser, extractor, scripts):
    for script in scripts:
        tree = parser.parse(script)
        extractor.visit(tree)
        break

# Iterate through HTML files and extract features
page_sources_path = "data/page_sources/"
parser = Parser()
extractor = FeatureExtractor()
for file in os.listdir(page_sources_path):
    if file.endswith('.html'):
        html_path = os.path.join(page_sources_path, file)
        scripts = extract_scripts(html_path)
        feature_sets = extract_features(parser, extractor, scripts)
        break
print(extractor.feature_sets)