import os
import pickle
import esprima

scripts = ["""if (new Date().getHours() < 18) {
  document.getElementById("demo").innerHTML = "Good day!";
}"""
#     ,"""
# function BlockAdBlock(options) {
#     this._options = options || {};
#     this._var = {};
#     this.init();
# }

# BlockAdBlock.prototype.init = function() {
#     this._var.bait = null;
#     this._creatBait();
#     this._checkBait(true);
# };

# BlockAdBlock.prototype._creatBait = function() {
#     var bait = document.createElement('div');
#     bait.setAttribute('class', this._options.baitClass);
#     bait.setAttribute('style', this._options.baitStyle);
#     this._var.bait = window.document.body.appendChild(bait);
#     this._var.bait.offsetParent;
#     this._var.bait.offsetHeight;
#     this._var.bait.offsetLeft;
#     this._var.bait.offsetTop;
#     this._var.bait.offsetWidth;
#     this._var.bait.clientHeight;
#     this._var.bait.clientWidth;
#     if (this._options.debug === true) {
#         this._log('_creatBait', 'Bait has been created');
#     }
# };

# BlockAdBlock.prototype._checkBait = function(loop) {
#     var detected = false;
#     if (window.document.body.getAttribute('abp') !== null ||
#         this._var.bait.offsetParent === null ||
#         this._var.bait.offsetHeight === 0 ||
#         this._var.bait.offsetLeft === 0 ||
#         this._var.bait.offsetTop === 0 ||
#         this._var.bait.offsetWidth === 0 ||
#         this._var.bait.clientHeight === 0 ||
#         this._var.bait.clientWidth === 0) {
#         detected = true;
#     }
# };
# """
]

# Function to recursively extract features from an AST
def extract_features(node, context, feature_sets):
    if isinstance(node, esprima.nodes.Node):
        node_type = node.type
        current_context = context + [node_type]
        if not node.name == None:
            text = node.name
        elif not node.value == None:
            text = node.value
        else:
            text = ''
        if text:
            feature_sets[0].append(('.'.join(current_context), text))
            if node_type == 'Literal':
                feature_sets[1].append(('.'.join(current_context), text))
            else:
                feature_sets[2].append(('.'.join(current_context), text))

        for key, value in node.items():
            if isinstance(value, (list, esprima.nodes.Node)):
                extract_features(value, current_context, feature_sets)
    elif isinstance(node, list):
        for item in node:
            extract_features(item, context, feature_sets)

# Parse JavaScript code and extract features
def extract_features_from_js(script, feature_sets):
    try:
        ast = esprima.parseScript(script)
        extract_features(getattr(ast, 'body'), [], feature_sets)
    except Exception as e:
        print(f"Error parsing JavaScript code: {e}")

def filter_features(features, number_of_features):
    # Remove duplicates
    features = list(set(features))
    return features[:number_of_features]

all_features = []
literal_features = []
identifier_features = []
feature_sets = [all_features, literal_features, identifier_features]
scripts_map_path = "data/scripts/"
for dir in os.listdir(scripts_map_path):
    url_path = os.path.join(scripts_map_path, dir)
    if os.path.isdir(url_path):
        for dir in os.listdir(url_path):
            script_path = os.path.join(url_path, dir)
            if dir.endswith('.js'):
                with open(script_path, 'r', encoding='utf-8') as f:
                    script = f.read()
                    extract_features_from_js(script, feature_sets)

set_names = ["all", "literal", "identifiers"]
for (features, set_name)  in zip(feature_sets, set_names):
    for number_of_features in [100, 1000, 10000]:
        features = filter_features(features, number_of_features)
        with open(f"data/feature_sets/{set_name}_{number_of_features}.pickle", 'wb') as f:
            pickle.dump(features, f)
    
print(all_features)
print(literal_features)
print(identifier_features)