import re

class AdvancedTokenizer:
    def __init__(self, language='java'):
        self.language = language
        self.patterns = self._get_language_patterns()
    
    def _get_language_patterns(self):
        """Get tokenization patterns for each language"""
        patterns = {
            'java': r'[a-zA-Z_]\w*|\d+\.\d+|\d+|//.*|/\*.*?\*/|\+\+|\-\-|&&|\|\||[=+\-*/%<>!&|(),;{}[\]\.]|".*?"|\'.*?\'|\S',
            'python': r'[a-zA-Z_]\w*|\d+\.\d+|\d+|#.*|""".*?"""|\'\'\'.*?\'\'\'|[\+\-\*/%&|\^~<>!=]=?|//=|\.\.\.|->|[(),;:\[\]{}@]|".*?"|\'.*?\'|\S',
            'cpp': r'[a-zA-Z_]\w*|\d+\.\d+|\d+|//.*|/\*.*?\*/|#\s*include|\+\+|\-\-|&&|\|\||->|::|[=+\-*/%<>!&|(),;{}[\]\.]|".*?"|\'.*?\'|\S'
        }
        return patterns.get(self.language, patterns['java'])
    
    def tokenize(self, code):
        """Advanced tokenization with language-specific patterns"""
        # Remove string literals first to avoid tokenizing inside them
        string_pattern = r'(""".*?"""|\'\'\'.*?\'\'\'|".*?"|\'.*?\')'
        string_literals = []
        
        def replace_string(match):
            string_literals.append(match.group())
            return f'__STRING_{len(string_literals)-1}__'
        
        # Temporarily replace string literals
        code_no_strings = re.sub(string_pattern, replace_string, code, flags=re.DOTALL)
        
        # Tokenize the code without strings
        tokens = re.findall(self.patterns, code_no_strings)
        
        # Restore string literals
        for i, token in enumerate(tokens):
            if token.startswith('__STRING_') and token.endswith('__'):
                str_index = int(token[9:-2])
                if str_index < len(string_literals):
                    tokens[i] = string_literals[str_index]
        
        return [token for token in tokens if token.strip()]
    
    def detokenize(self, tokens):
        """Convert tokens back to code with proper spacing"""
        return ' '.join(tokens)