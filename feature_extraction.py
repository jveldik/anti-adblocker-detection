import os
import esprima

# Function to extract features from JavaScript code using esprima
def extract_features(feature_sets, script):
    tokenized_script = esprima.tokenize(script)
    parsed_script = esprima.parseScript(script)
    print(tokenized_script)
    print(parsed_script)
    print(script)
    
    return feature_sets

# Iterate through HTML files and extract features
script_sources_path = "data/scripts/"
feature_sets = {
        'all': set(),
        'literal': set(),
        'keyword': set()
    }

for file in os.listdir(script_sources_path):
    if file.endswith('.html'):
        html_path = os.path.join(page_sources_path, file)
        scripts = extract_scripts(html_path)
        for script in scripts:
            feature_sets = extract_features(feature_sets, script)
            break
        break
print(feature_sets)
script = """
function BlockAdBlock(options) {
    this._options = options || {};
    this._var = {};
    this.init();
}

BlockAdBlock.prototype.init = function() {
    this._var.bait = null;
    this._creatBait();
    this._checkBait(true);
};

BlockAdBlock.prototype._creatBait = function() {
    var bait = document.createElement('div');
    bait.setAttribute('class', this._options.baitClass);
    bait.setAttribute('style', this._options.baitStyle);
    this._var.bait = window.document.body.appendChild(bait);
    this._var.bait.offsetParent;
    this._var.bait.offsetHeight;
    this._var.bait.offsetLeft;
    this._var.bait.offsetTop;
    this._var.bait.offsetWidth;
    this._var.bait.clientHeight;
    this._var.bait.clientWidth;
    if (this._options.debug === true) {
        this._log('_creatBait', 'Bait has been created');
    }
};

BlockAdBlock.prototype._checkBait = function(loop) {
    var detected = false;
    if (window.document.body.getAttribute('abp') !== null ||
        this._var.bait.offsetParent === null ||
        this._var.bait.offsetHeight === 0 ||
        this._var.bait.offsetLeft === 0 ||
        this._var.bait.offsetTop === 0 ||
        this._var.bait.offsetWidth === 0 ||
        this._var.bait.clientHeight === 0 ||
        this._var.bait.clientWidth === 0) {
        detected = true;
    }
};
"""
feature_sets = extract_features(feature_sets, script)
print(feature_sets)