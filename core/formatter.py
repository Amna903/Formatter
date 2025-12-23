from .detector import CodeIssueDetector
from .fixer import CodeFixer
from .language_manager import LanguageManager
from utils.tokenizer import AdvancedTokenizer

class CodeFormatter:
    def __init__(self, language='java', style='google'):
        self.language = language
        self.style = style
        self.language_manager = LanguageManager()
        self.tokenizer = AdvancedTokenizer(language)
        self.detector = CodeIssueDetector(language, style)
        self.fixer = CodeFixer(self.tokenizer)  # FIXED: Only pass tokenizer
    
    def format_file(self, file_path):
        """Format a code file with language-specific rules"""
        try:
            # Read original code
            with open(file_path, 'r') as f:
                original_code = f.read()
            
            print(f"🌐 Processing {self.language.upper()} code...")
            print(f"📝 Original code ({len(original_code)} chars)")
            
            # Tokenize code with language-specific rules
            tokens = self.tokenizer.tokenize(original_code)
            print(f"🔍 Tokenized {len(tokens)} tokens")
            
            # Detect issues with language-specific rules
            issues = self.detector.detect_issues(tokens, original_code)
            print(f"🎯 Found {len(issues)} formatting issues")
            
            # Show detected issues
            for issue in issues[:5]:  # Show first 5 issues
                print(f"   - {issue['description']}")
            
            if len(issues) > 5:
                print(f"   ... and {len(issues) - 5} more issues")
            
            # Apply fixes
            formatted_code = self.fixer.apply_fixes(original_code, issues)
            
            # Calculate metrics
            formatting_score = self._calculate_formatting_score(issues, len(self.fixer.applied_fixes))
            
            return {
                'original_code': original_code,
                'formatted_code': formatted_code,
                'issues_found': issues,
                'formatting_score': formatting_score,
                'fixes_applied': len(self.fixer.applied_fixes),
                'language': self.language,
                'style': self.style
            }
            
        except Exception as e:
            print(f"❌ Error in format_file: {e}")
            # Return original code as fallback
            with open(file_path, 'r') as f:
                original_code = f.read()
            return {
                'original_code': original_code,
                'formatted_code': original_code,
                'issues_found': [],
                'formatting_score': 0.0,
                'fixes_applied': 0
            }
    
    def _calculate_formatting_score(self, issues, fixes_applied):
        """Calculate formatting score with severity weighting"""
        if not issues:
            return 100.0
        
        success_rate = fixes_applied / len(issues) if issues else 1.0
        return success_rate * 100