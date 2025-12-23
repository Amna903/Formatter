import os

# Import all rule files
try:
    from config.rules.java_rules import JAVA_RULES
    from config.rules.python_rules import PYTHON_RULES
    from config.rules.cpp_rules import CPP_RULES
except ImportError:
    # Fallback rules if files don't exist
    JAVA_RULES = {
        'indentation': {'size': 4, 'use_tabs': False},
        'braces': {'class_brace': 'same_line', 'method_brace': 'same_line'},
        'spacing': {'after_keywords': ['if', 'for', 'while'], 'around_operators': ['=', '==', '+', '-']}
    }
    PYTHON_RULES = {
        'indentation': {'size': 4, 'use_tabs': False},
        'spacing': {'after_commas': True, 'around_operators': True}
    }
    CPP_RULES = {
        'indentation': {'size': 2, 'use_tabs': False},
        'braces': {'class_brace': 'same_line', 'function_brace': 'same_line'}
    }

class LanguageManager:
    def __init__(self):
        self.languages = {
            'java': JAVA_RULES,
            'python': PYTHON_RULES, 
            'cpp': CPP_RULES
        }
    
    def get_rules(self, language):
        """Get formatting rules for specific language"""
        return self.languages.get(language, JAVA_RULES)
    
    def detect_language(self, file_path):
        """Auto-detect language from file extension"""
        if not file_path:
            return 'java'
            
        extension = os.path.splitext(file_path)[1].lower()
        extension_map = {
            '.java': 'java',
            '.py': 'python', 
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.c': 'cpp',
            '.h': 'cpp',
            '.hpp': 'cpp',
            '.cxx': 'cpp'
        }
        return extension_map.get(extension, 'java')
    
    def get_file_extensions(self, language):
        """Get valid file extensions for a language"""
        extension_map = {
            'java': ['.java'],
            'python': ['.py', '.pyw'],
            'cpp': ['.cpp', '.cc', '.c', '.h', '.hpp', '.cxx']
        }
        return extension_map.get(language, [])
    
    def validate_language_support(self, file_path):
        """Check if file type is supported"""
        language = self.detect_language(file_path)
        return language in self.languages
    
    def get_supported_languages(self):
        """Get list of all supported languages"""
        return list(self.languages.keys())