import argparse
import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from core.formatter import CodeFormatter
    from core.language_manager import LanguageManager
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔧 Creating minimal formatter...")
    
    # Fallback minimal formatter
    class MinimalFormatter:
        def __init__(self, language='java'):
            self.language = language
            
        def format_file(self, file_path):
            with open(file_path, 'r') as f:
                code = f.read()
            
            # Simple formatting for demo
            if self.language == 'java':
                formatted = code.replace('){', ') {').replace('for(', 'for (')
            else:
                formatted = code
                
            return {
                'original_code': code,
                'formatted_code': formatted,
                'issues_found': [],
                'formatting_score': 50.0,
                'fixes_applied': 0
            }
    
    CodeFormatter = MinimalFormatter

def main():
    parser = argparse.ArgumentParser(description='Universal Code Formatter')
    parser.add_argument('--input', type=str, required=True, help='Input code file')
    parser.add_argument('--output', type=str, help='Output file for formatted code')
    parser.add_argument('--language', type=str, choices=['java', 'python', 'cpp', 'auto'], 
                       default='auto', help='Programming language')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"❌ Error: File '{args.input}' not found")
        return
    
    # Auto-detect language
    if args.language == 'auto':
        lm = LanguageManager()
        args.language = lm.detect_language(args.input)
        print(f"🔍 Auto-detected language: {args.language}")
    
    try:
        # Initialize formatter
        formatter = CodeFormatter(language=args.language)
        
        # Format the code
        result = formatter.format_file(args.input)
        
        # Save formatted code
        if args.output:
            with open(args.output, 'w') as f:
                f.write(result['formatted_code'])
            print(f"💾 Formatted code saved to: {args.output}")
        
        # Print results
        print(f"\n✅ {args.language.upper()} Formatting complete!")
        print(f"📊 Found {len(result['issues_found'])} issues, fixed {result['fixes_applied']}")
        print(f"💯 Formatting score: {result['formatting_score']:.1f}%")
        
        # Show changes
        if result['original_code'] != result['formatted_code']:
            print(f"\n📝 Original vs Formatted:")
            print("ORIGINAL:")
            print(result['original_code'])
            print("\nFORMATTED:")
            print(result['formatted_code'])
        else:
            print("🎉 Code is already perfectly formatted!")
            
    except Exception as e:
        print(f"❌ Error during formatting: {e}")
        print("🔄 Using fallback formatter...")
        
        # Use minimal formatter as fallback
        formatter = CodeFormatter(args.language)
        result = formatter.format_file(args.input)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(result['formatted_code'])
            print(f"💾 Formatted code saved to: {args.output}")

if __name__ == "__main__":
    main()