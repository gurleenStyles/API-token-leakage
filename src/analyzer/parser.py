import re
import esprima
from rich.console import Console

console = Console()

class JSAnalyzer:
    def __init__(self, filepath):
        self.filepath = filepath
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            self.content = f.read()

        self.extracted_strings = set()
        self.config_objects = []

    def extract_strings_regex(self):
        """Extract all string literals from the JS file using Regex as a fallback/fast pass."""
        # Match single, double, and backtick quoted strings
        #this function will extract the string from the js file 
        pattern = r"""(?x)
            (?:'(?:\\'|[^'])*') |
            (?:"(?:\\"|[^"])*") |
            (?:`(?:\\`|[^`])*`)
        """
        matches = re.finditer(pattern, self.content)
        for match in matches:
            string_val = match.group(0)[1:-1] # Remove surrounding quotes
            if len(string_val) > 5:  # Ignore very short strings
                self.extracted_strings.add(string_val)
        
        console.print(f"[green]Extracted {len(self.extracted_strings)} unique strings via regex from {self.filepath}[/green]")
        return list(self.extracted_strings)

    def extract_ast(self):
        """Use esprima to parse the JS and confidently extract String Literals and Object Expressions."""
        try:
            #Tolerant mode to parse minified/incomplete files
            #this function will parse the js file and extract the string from the js file
            #this function will extract the string from the js file
            tree = esprima.parseScript(self.content, {"tolerant": True})
            self._walk_ast(tree)
            console.print(f"[green]Successfully parsed AST for {self.filepath}[/green]")
        except Exception as e:
            console.print(f"[yellow]AST parsing failed for {self.filepath}: {e}. Submitting to regex only fallback.[/yellow]")

    def _walk_ast(self, node):
        if not node or not hasattr(node, 'type'):
            return

        if node.type == 'Literal' and isinstance(node.value, str):
            if len(node.value) > 5:
                self.extracted_strings.add(node.value)
        
        elif node.type == 'ObjectExpression':
            # Extract keys/values of objects, potentially configurations
            obj_data = {}
            for prop in node.properties:
                if prop.type == 'Property':
                    key_name = None
                    if prop.key.type == 'Identifier':
                        key_name = prop.key.name
                    elif prop.key.type == 'Literal':
                        key_name = prop.key.value
                    
                    if key_name and prop.value.type == 'Literal' and isinstance(prop.value.value, str):
                        obj_data[key_name] = prop.value.value
            
            if obj_data:
                self.config_objects.append(obj_data)

        # Recursively walk child nodes
        for key, value in vars(node).items():
            if isinstance(value, list):
                for item in value:
                    if hasattr(item, 'type'):
                        self._walk_ast(item)
            elif hasattr(value, 'type'):
                self._walk_ast(value)

    def analyze(self):
        """Full analysis: Extract strings and AST."""
        self.extract_strings_regex()
        self.extract_ast()
        return {
            "file": self.filepath,
            "strings": list(self.extracted_strings),
            "configs": self.config_objects
        }

#It takes a downloaded JS file and tears it apart to extract every string and 
#configuration object hidden inside it.