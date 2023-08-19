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
def extract_features(node, context, all_features, literal_features, identifier_features):
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
            all_features.append(('.'.join(current_context), text))
            if node_type == 'Literal':
                literal_features.append(('.'.join(current_context), text))
            else:
                identifier_features.append(('.'.join(current_context), text))

        for key, value in node.items():
            if isinstance(value, (list, esprima.nodes.Node)):
                extract_features(value, current_context, all_features, literal_features, identifier_features)
    elif isinstance(node, list):
        for item in node:
            extract_features(item, context, all_features, literal_features, identifier_features)

# Parse JavaScript code and extract features
def extract_features_from_js(script, all_features, literal_features, identifier_features):
    try:
        ast = esprima.parseScript(script)
        return extract_features(getattr(ast, 'body'), [], all_features, literal_features, identifier_features)
    except Exception as e:
        print(f"Error parsing JavaScript code: {e}")
        return []

all_features = []
literal_features = []
identifier_features = []
for script in scripts:
    extract_features_from_js(script, all_features, literal_features, identifier_features)
    
print(all_features)
print(literal_features)
print(identifier_features)