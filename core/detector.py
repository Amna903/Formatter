import re
from core.language_manager import LanguageManager

class CodeIssueDetector:
    def __init__(self, language='java', style='google'):
        self.language = language
        self.style = style
        self.language_manager = LanguageManager()
        self.rules = self.language_manager.get_rules(language)
    
    def detect_issues(self, tokens, original_code):
        """Detect all formatting issues for the specific language"""
        issues = []
        
        try:
            # Common issues for all languages
            issues.extend(self._check_operator_spacing(tokens))
            issues.extend(self._check_comma_spacing(tokens))
            issues.extend(self._check_bracket_spacing(tokens))
            issues.extend(self._check_semicolon_spacing_after(tokens))
            issues.extend(self._check_keyword_spacing(tokens))
            
            # Language-specific issues
            if self.language == 'java':
                issues.extend(self._check_java_specific_issues(tokens, original_code))
                issues.extend(self._check_java_array_declaration(tokens))
            elif self.language == 'python':
                issues.extend(self._check_python_specific_issues(tokens, original_code))
            elif self.language == 'cpp':
                issues.extend(self._check_cpp_specific_issues(tokens, original_code))
            
            # Style-specific issues
            issues.extend(self._check_blank_lines(original_code))
            issues = self._remove_duplicate_issues(issues)
        except Exception as e:
            print(f"❌ Error in issue detection: {e}")
        
        return issues

    def _check_java_specific_issues(self, tokens, code):
        """Java-specific formatting issues"""
        issues = []
        
        # Check package and import formatting
        issues.extend(self._check_java_imports(code))
        issues.extend(self._check_java_package(code))
        
        # Check class/method brace placement
        issues.extend(self._check_java_braces(tokens, code))
        issues.extend(self._check_java_class_declaration(tokens))
        issues.extend(self._check_java_method_declaration(tokens))
        
        # Check annotation formatting
        issues.extend(self._check_java_annotations(tokens))
        issues.extend(self._check_java_modifiers(tokens))
        
        # Check specific Java patterns
        issues.extend(self._check_java_string_concatenation(tokens))
        issues.extend(self._check_java_keyword_spacing(tokens))
        
        return issues
    
    def _check_operator_spacing(self, tokens):
        """Check operator spacing for all languages - FIXED COMPOUND OPERATORS"""
        issues = []
        # Include all relevant operators
        operators = ['=', '==', '!=', '>', '<', '>=', '<=', '+', '-', '*', '/', '%', '&&', '||', ':', '?', '+=', '-=', '*=', '/=', '%=']
        
        for i in range(1, len(tokens) - 1):
            current_token = tokens[i]
            
            if current_token in operators:
                prev_token = tokens[i-1]
                next_token = tokens[i+1]
                
                # Skip increment/decrement operators
                skip_patterns = ['i++', 'i--', '++i', '--i']
                if (prev_token + current_token + next_token) in skip_patterns:
                    continue
                
                # Skip unary operators (assuming _is_unary_operator handles this correctly)
                if self._is_unary_operator(current_token, i, tokens):
                    continue
                
                # --- CRITICAL PYTHON COLON HANDLING ---
                if current_token == ':':
                    if self.language == 'python':
                        # Python colons (block, dictionary, slicing) must be tight to the left token.
                        # Rule: Must have NO space before the colon.
                        if prev_token == ' ':
                             issues.append({
                                'type': 'extra_space_before_colon',
                                'position': i,
                                'description': f'Extra space before ":" in Python',
                                'tokens': [prev_token, current_token, next_token],
                                'old_pattern': f"{prev_token}{current_token}",
                                'new_pattern': f"{current_token}",
                                'language': self.language,
                                'severity': 'medium'
                            })
                        
                        # We let the CodeFixer handle the space AFTER the colon for blocks/dicts.
                        continue # Skip standard operator check for Python colons
                    
                    # Java/JavaScript Colon Handling (Enhanced For, Ternary, Switch Case)
                    # We only enforce spaces if the tokens are immediately adjacent AND it's not a Java/JS keyword.
                    if self.language != 'python' and prev_token != ' ' and next_token != ' ':
                        # This covers "for(s:strings)" (Enhanced For) or "case 1:break" (Switch)
                        old_pattern = f"{prev_token}{current_token}{next_token}"
                        new_pattern = f"{prev_token} {current_token} {next_token}"
                        
                        issues.append({
                            'type': 'missing_spaces_around_operator',
                            'position': i,
                            'description': f'Missing spaces around ":" operator',
                            'tokens': [prev_token, current_token, next_token],
                            'old_pattern': old_pattern,
                            'new_pattern': new_pattern,
                            'language': self.language,
                            'severity': 'medium'
                        })
                    continue # Finished colon handling
                
                # --- STANDARD OPERATOR HANDLING ---

                # SPECIAL HANDLING FOR COMPOUND OPERATORS
                compound_ops = ['+=', '-=', '*=', '/=', '%=', '==', '!=', '&&', '||']
                if current_token in compound_ops:
                    # Check if spaces are missing around the compound operator
                    if prev_token != ' ' or next_token != ' ':
                        old_pattern = f"{prev_token}{current_token}{next_token}"
                        new_pattern = f"{prev_token} {current_token} {next_token}"
                        
                        issues.append({
                            'type': 'missing_spaces_around_operator',
                            'position': i,
                            'description': f'Missing spaces around "{current_token}" operator',
                            'tokens': [prev_token, current_token, next_token],
                            'old_pattern': old_pattern,
                            'new_pattern': new_pattern,
                            'language': self.language,
                            'severity': 'medium'
                        })
                    continue
                
                # Regular binary operator spacing check
                needs_spaces = (
                    (prev_token != ' ' and not prev_token.isspace()) and 
                    (next_token != ' ' and not next_token.isspace())
                )
                
                if needs_spaces:
                    # Create the replacement pattern
                    old_pattern = f"{prev_token}{current_token}{next_token}"
                    new_pattern = f"{prev_token} {current_token} {next_token}"
                    
                    issues.append({
                        'type': 'missing_spaces_around_operator',
                        'position': i,
                        'description': f'Missing spaces around "{current_token}" operator',
                        'tokens': [prev_token, current_token, next_token],
                        'old_pattern': old_pattern,
                        'new_pattern': new_pattern,
                        'language': self.language,
                        'severity': 'medium'
                    })
        
        return issues
    def _is_unary_operator(self, operator, position, tokens):
        """Check if operator is being used as unary"""
        if operator in ['+', '-', '!', '~']:
            # Check if it's at start of expression or after another operator
            if position == 0:
                return True
            prev_token = tokens[position-1]
            if prev_token in ['(', '=', ',', '[', '{', ';', ' ']:
                return True
        return False
    
    def _check_keyword_spacing(self, tokens):
        """Check spacing after control structure keywords (if, for, while, switch, catch, try, do, else)"""
        issues = []
        keywords = ['if', 'for', 'while', 'switch', 'catch', 'try', 'do', 'else']

        
        i = 0  
        while i < len(tokens) - 1:  
            token = tokens[i]  

            # Handle else and else if  
            if token == 'else':  
                next_token = tokens[i+1] if i+1 < len(tokens) else ''  
                if next_token == '{':  
                    issues.append({  
                        'type': 'missing_space_before_brace_after_else',  
                        'position': i,  
                        'description': 'Missing space before brace after "else"',  
                        'tokens': ['else', '{'],  
                        'old_pattern': 'else{',  
                        'new_pattern': 'else {',  
                        'severity': 'medium'  
                    })  
                elif next_token == 'if':  
                    # Skip spacing here for "else if"  
                    pass  
                else:  
                    if next_token != ' ' and next_token != '':  
                        issues.append({  
                            'type': 'missing_space_after_else',  
                            'position': i,  
                            'description': 'Missing space after "else"',  
                            'tokens': ['else', next_token],  
                            'old_pattern': f'else{next_token}',  
                            'new_pattern': f'else {next_token}',  
                            'severity': 'medium'  
                        })  

            # Handle other control keywords followed by '('  
            elif token in ['if', 'for', 'while', 'switch', 'catch', 'try', 'do']:  
                if i+1 < len(tokens) and tokens[i+1] == '(':  
                    issues.append({  
                        'type': 'missing_space_after_keyword',  
                        'position': i,  
                        'description': f'Missing space after "{token}" keyword',  
                        'tokens': [token, '('],  
                        'old_pattern': f'{token}(',  
                        'new_pattern': f'{token} (',  
                        'severity': 'medium'  
                    })  

                    # Extract inner tokens of parentheses to check operator spacing  
                    paren_tokens, end_index = self._extract_parenthesis_tokens(tokens, i+1)  
                    issues.extend(self._check_operator_spacing(paren_tokens))  
                    i = end_index  # Skip to end of parentheses  

            i += 1  
        return issues  
        

    def _extract_parenthesis_tokens(self, tokens, start_index):
        """Return tokens inside parentheses and the closing index"""
        inner_tokens = []
        depth = 0
        i = start_index
 
        while i < len(tokens):  
            token = tokens[i]  
            if token == '(':  
                depth += 1  
                if depth > 1:  
                    inner_tokens.append(token)  
            elif token == ')':  
                depth -= 1  
                if depth == 0:  
                    return inner_tokens, i  
                else:  
                    inner_tokens.append(token)  
            else:  
                inner_tokens.append(token)  
            i += 1  

        return inner_tokens, i  
         

    def _check_operator_spacing(self, tokens):
        """Check spacing around operators including compound operators"""
        issues = []
        compound_ops = ['==', '!=', '+=', '-=', '*=', '/=', '%=', '&&', '||', ':', '?']
        single_ops = ['=', '+', '-', '*', '/', '%', '<', '>', '&', '|', '^']

    
        i = 0  
        while i < len(tokens):  
            token = tokens[i]  

            if token in compound_ops + single_ops:  
                prev_token = tokens[i-1] if i-1 >= 0 else ''  
                next_token = tokens[i+1] if i+1 < len(tokens) else ''  

                # Skip unary operators at start or after another operator  
                if self._is_unary_operator(token, i, tokens):  
                    i += 1  
                    continue  

                # Check spacing around token  
                missing_space = False  
                if prev_token not in [' ', ''] and next_token not in [' ', '']:  
                    missing_space = True  

                if missing_space:  
                    issues.append({  
                        'type': 'missing_spaces_around_operator',  
                        'position': i,  
                        'description': f'Missing spaces around "{token}" operator',  
                        'tokens': [prev_token, token, next_token],  
                        'old_pattern': f'{prev_token}{token}{next_token}',  
                        'new_pattern': f'{prev_token} {token} {next_token}',  
                        'severity': 'medium'  
                    })  

            i += 1  
        return issues  

    def _check_java_braces(self, tokens, code):
        """Check Java brace placement - ENHANCED VERSION"""
        issues = []
        
        for i in range(len(tokens) - 1):
            # Check for class/interface/enum name followed by {
            if self._is_java_identifier(tokens[i]) and tokens[i+1] == '{':
                # This is: class Name{
                issues.append({
                    'type': 'missing_space_before_class_brace',
                    'position': i,
                    'description': f'Missing space before brace after "{tokens[i]}"',
                    'tokens': [tokens[i], '{'],
                    'old_pattern': f'{tokens[i]}{{',
                    'new_pattern': f'{tokens[i]} {{',
                    'severity': 'medium'
                })
            
            # Check for ) followed by {
            if tokens[i] == ')' and tokens[i+1] == '{':
                # This is: method(){ 
                issues.append({
                    'type': 'missing_space_before_method_brace',
                    'position': i,
                    'description': 'Missing space before method brace',
                    'tokens': [')', '{'],
                    'old_pattern': '){',
                    'new_pattern': ') {',
                    'severity': 'medium'
                })
            
            # Check for { followed by non-space content (except })
            if tokens[i] == '{' and i + 1 < len(tokens) and tokens[i+1] != ' ' and tokens[i+1] != '}':
                # This is: {void, {case, {private, etc.
                issues.append({
                    'type': 'missing_space_after_opening_brace',
                    'position': i,
                    'description': 'Missing space after opening brace',
                    'tokens': ['{', tokens[i+1]],
                    'old_pattern': f'{{{tokens[i+1]}',
                    'new_pattern': f'{{ {tokens[i+1]}',
                    'severity': 'medium'
                })
            
            # Check for else followed by {
            if tokens[i] == 'else' and i + 1 < len(tokens) and tokens[i+1] == '{':
                # This is: else{
                issues.append({
                    'type': 'missing_space_before_brace_after_else',
                    'position': i,
                    'description': 'Missing space before brace after "else"',
                    'tokens': ['else', '{'],
                    'old_pattern': 'else{',
                    'new_pattern': 'else {',
                    'severity': 'medium'
                })
        
        return issues

    def _fix_java_control_structures(self, tokens):
        """Fix spacing for Java control structures and operators"""
        issues = []
        keywords = ['if', 'for', 'while', 'switch', 'catch', 'do', 'else']

        i = 0
        while i < len(tokens):
            token = tokens[i]

            # Handle keyword spacing
            if token in keywords:
                # Space after keyword (except 'else' which is before brace)
                if token != 'else':
                    if i + 1 < len(tokens) and tokens[i+1] != '(':
                        issues.append({
                            'type': 'keyword_parenthesis_spacing',
                            'position': i,
                            'description': f'Missing space after "{token}"',
                            'old_pattern': token + tokens[i+1],
                            'new_pattern': token + ' ' + tokens[i+1],
                            'severity': 'medium'
                        })
                else:
                    # Ensure space before brace
                    if i + 1 < len(tokens) and tokens[i+1] == '{':
                        issues.append({
                            'type': 'keyword_brace_spacing',
                            'position': i,
                            'description': 'Missing space before brace after "else"',
                            'old_pattern': 'else{',
                            'new_pattern': 'else {',
                            'severity': 'medium'
                        })

            # Fix operators spacing
            if token in ['=', '+', '-', '*', '/', '<', '>', '&&', '||', '==', '!=', '<=', '>=', '+=', '-=', '*=', '/=']:
                # Ensure operators have spaces around (except compound like +=, -=)
                prev_token = tokens[i-1] if i > 0 else ''
                next_token = tokens[i+1] if i + 1 < len(tokens) else ''
                if prev_token not in [' ', '(', '{'] and token not in ['+=', '-=', '*=', '/=']:
                    issues.append({
                        'type': 'operator_spacing',
                        'position': i,
                        'description': f'Missing space before operator "{token}"',
                        'severity': 'medium'
                    })
                if next_token not in [' ', ')', ';', '{'] and token not in ['+=', '-=', '*=', '/=']:
                    issues.append({
                        'type': 'operator_spacing',
                        'position': i,
                        'description': f'Missing space after operator "{token}"',
                        'severity': 'medium'
                    })

            # Fix for-loop semicolon spacing
            if token == ';' and i > 0 and i + 1 < len(tokens):
                prev_token = tokens[i-1]
                next_token = tokens[i+1]
                if next_token != ' ':
                    issues.append({
                        'type': 'semicolon_spacing_for',
                        'position': i,
                        'description': 'Missing space after semicolon in for-loop',
                        'old_pattern': ';' + next_token,
                        'new_pattern': '; ' + next_token,
                        'severity': 'medium'
                    })

            i += 1

        return issues


    def _check_python_specific_issues(self, tokens, code):
        """Python-specific formatting issues"""
        issues = []
        
        # Check indentation
        issues.extend(self._check_python_indentation(code))
        issues.extend(self._check_python_tabs_vs_spaces(code))
        
        # Check import order and formatting
        issues.extend(self._check_python_imports(code))
        issues.extend(self._check_python_import_spacing(code))
        
        # Check line length and formatting
        issues.extend(self._check_python_line_length(code))
        issues.extend(self._check_python_trailing_commas(code))
        issues.extend(self._check_python_quotes(code))
        
        # Check Python-specific syntax
        issues.extend(self._check_python_function_definitions(tokens))
        issues.extend(self._check_python_class_definitions(tokens))
        issues.extend(self._check_python_decorators(tokens))
        
        # Check whitespace
        issues.extend(self._check_trailing_whitespace(code))
        issues.extend(self._check_python_whitespace_around_operators(code))
        issues.extend(self._check_python_whitespace_in_parentheses(code))
        
        return issues
    
    def _check_cpp_specific_issues(self, tokens, code):
        """C++-specific formatting issues"""
        issues = []
        
        # Check include order and formatting
        issues.extend(self._check_cpp_includes(code))
        issues.extend(self._check_cpp_include_guard(code))
        
        # Check pointer/reference spacing
        issues.extend(self._check_cpp_pointers_references(tokens))
        issues.extend(self._check_cpp_reference_declarations(tokens))
        
        # Check namespace formatting
        issues.extend(self._check_cpp_namespaces(tokens, code))
        issues.extend(self._check_cpp_class_declarations(tokens))
        issues.extend(self._check_cpp_function_declarations(tokens))
        
        # Check C++ specific patterns
        issues.extend(self._check_cpp_template_syntax(tokens))
        issues.extend(self._check_cpp_initialization_lists(tokens))
        issues.extend(self._check_cpp_access_specifiers(tokens))
        
        return issues
    
    
    def _is_compound_operator(self, operator, prev_token, next_token):
        """Check if this is a compound operator that shouldn't be split"""
        compound_ops = ['==', '!=', '+=', '-=', '*=', '/=', '%=', '&&', '||']
        return operator in compound_ops
   
    
    def _check_comma_spacing(self, tokens):
        """Check comma spacing - FIXED for multiple commas"""
        issues = []
        
        for i in range(len(tokens) - 1):
            if tokens[i] == ',' and i + 1 < len(tokens):
                next_token = tokens[i+1]
                if next_token and next_token != ' ' and next_token != ')' and next_token != ']':
                    # Create context-aware pattern
                    if i > 0:
                        prev_token = tokens[i-1]
                        old_pattern = f"{prev_token},{next_token}"
                        new_pattern = f"{prev_token}, {next_token}"
                    else:
                        old_pattern = f",{next_token}"
                        new_pattern = f", {next_token}"
                    
                    issues.append({
                        'type': 'missing_space_after_comma',
                        'position': i,
                        'description': 'Missing space after comma',
                        'tokens': [',', next_token],
                        'old_pattern': old_pattern,
                        'new_pattern': new_pattern,
                        'severity': 'medium'
                    })
        
        return issues
    def _remove_duplicate_issues(self, issues):
        """Remove duplicate issues from the list"""
        seen = set()
        unique_issues = []
        
        for issue in issues:
            # Create a unique key for each issue
            key = (
                issue.get('type', ''),
                issue.get('old_pattern', ''),
                issue.get('new_pattern', ''),
                issue.get('position', 0)
            )
            
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)
        
        return unique_issues

    def _check_bracket_spacing(self, tokens):
        """Check spacing around brackets and parentheses - FIXED ARRAY INIT"""
        issues = []
        
        for i in range(len(tokens) - 1):
            # Check space after opening parenthesis (
            if tokens[i] == '(' and i + 1 < len(tokens) and tokens[i+1] == ' ':
                issues.append({
                    'type': 'extra_space_after_opening_paren',
                    'position': i,
                    'description': 'Extra space after opening parenthesis',
                    'tokens': ['(', tokens[i+1]],
                    'old_pattern': '( ',
                    'new_pattern': '(',
                    'severity': 'low'
                })
            
            # Check space before closing parenthesis )
            if tokens[i] == ' ' and i + 1 < len(tokens) and tokens[i+1] == ')':
                issues.append({
                    'type': 'extra_space_before_closing_paren',
                    'position': i,
                    'description': 'Extra space before closing parenthesis',
                    'tokens': [tokens[i], ')'],
                    'old_pattern': ' )',
                    'new_pattern': ')',
                    'severity': 'low'
                })
            
            # Check for extra space after opening brace in array initialization
            if tokens[i] == '{' and i + 1 < len(tokens) and tokens[i+1] == ' ':
                # But only flag this if it's likely an array initialization, not a block
                if i > 0 and tokens[i-1] == '=':
                    issues.append({
                        'type': 'extra_space_after_opening_brace',
                        'position': i,
                        'description': 'Extra space after opening brace in array initialization',
                        'tokens': ['{', ' '],
                        'old_pattern': '{ ',
                        'new_pattern': '{',
                        'severity': 'low'
                    })
        
        return issues
    def _check_semicolon_spacing(self, tokens):
        """Check semicolon spacing"""
        issues = []
        
        for i in range(len(tokens)):
            if tokens[i] == ';' and i > 0 and tokens[i-1] == ' ':
                issues.append({
                    'type': 'extra_space_before_semicolon',
                    'position': i-1,
                    'description': 'Extra space before semicolon',
                    'tokens': [tokens[i-1], ';'],
                    'old_pattern': ' ;',
                    'new_pattern': ';',
                    'severity': 'low'
                })
        
        return issues
    
    def _check_java_imports(self, code):
        """Check Java import formatting and order"""
        issues = []
        lines = code.split('\n')
        
        import_lines = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('import'):
                import_lines.append((i, stripped))
        
        if len(import_lines) > 1:
            # Check for wildcard imports
            for i, (line_num, import_stmt) in enumerate(import_lines):
                if '.*;' in import_stmt:
                    issues.append({
                        'type': 'java_wildcard_import',
                        'line': line_num + 1,
                        'description': 'Avoid wildcard imports',
                        'fix': 'Use specific imports instead of wildcards',
                        'severity': 'medium'
                    })
            
            # Check import order (java, javax, third-party)
            current_group = None
            for i, (line_num, import_stmt) in enumerate(import_lines):
                if 'import java.' in import_stmt:
                    group = 'java'
                elif 'import javax.' in import_stmt:
                    group = 'javax'
                else:
                    group = 'third-party'
                
                if current_group is not None and group != current_group:
                    # Check if groups are out of order
                    if (current_group == 'javax' and group == 'java') or \
                       (current_group == 'third-party' and group in ['java', 'javax']):
                        issues.append({
                            'type': 'java_import_order',
                            'line': line_num + 1,
                            'description': f'Import group order violation: {group} after {current_group}',
                            'fix': 'Reorder imports: java -> javax -> third-party',
                            'severity': 'low'
                        })
                current_group = group
        
        return issues
    
    def _check_java_package(self, code):
        """Check Java package declaration"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('package'):
                # Check package naming convention
                if not re.match(r'^package [a-z][a-z0-9]*(\.[a-z][a-z0-9]*)*;$', stripped):
                    issues.append({
                        'type': 'java_package_naming',
                        'line': i + 1,
                        'description': 'Package name should follow naming conventions',
                        'severity': 'medium'
                    })
                break
        
        return issues
    
    
    def _check_java_class_declaration(self, tokens):
        """Check Java class declaration formatting"""
        issues = []
        
        for i in range(len(tokens) - 3):
            if tokens[i] == 'class' and i + 2 < len(tokens):
                class_name = tokens[i+1]
                # Check class name follows conventions
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', class_name):
                    issues.append({
                        'type': 'java_class_naming',
                        'position': i + 1,
                        'description': f'Class name "{class_name}" should start with uppercase letter',
                        'severity': 'high'
                    })
        
        return issues
    
    def _check_java_method_declaration(self, tokens):
        """Check Java method declaration formatting"""
        issues = []
        
        for i in range(len(tokens) - 4):
            # Look for method patterns: [modifiers] type name(
            if tokens[i+2] == '(' and self._is_java_type(tokens[i+1]):
                method_name = tokens[i+1]
                # Check method name follows conventions
                if not re.match(r'^[a-z][a-zA-Z0-9]*$', method_name):
                    issues.append({
                        'type': 'java_method_naming',
                        'position': i + 1,
                        'description': f'Method name "{method_name}" should start with lowercase letter',
                        'severity': 'high'
                    })
        
        return issues
    
    def _check_java_annotations(self, tokens):
        """Check Java annotation formatting"""
        issues = []
        
        for i in range(len(tokens)):
            if tokens[i].startswith('@'):
                # Check annotation spacing
                if i + 1 < len(tokens) and tokens[i+1] != ' ' and not tokens[i+1].startswith('('):
                    issues.append({
                        'type': 'java_annotation_spacing',
                        'position': i,
                        'description': 'Missing space after annotation',
                        'tokens': [tokens[i], tokens[i+1]],
                        'old_pattern': f'{tokens[i]}{tokens[i+1]}',
                        'new_pattern': f'{tokens[i]} {tokens[i+1]}',
                        'severity': 'low'
                    })
        
        return issues
    
    def _check_java_modifiers(self, tokens):
        """Check Java modifier order"""
        issues = []
        modifier_order = ['public', 'protected', 'private', 'abstract', 'static', 'final', 'transient', 'volatile']
        
        i = 0
        while i < len(tokens):
            if tokens[i] in modifier_order:
                modifiers = []
                j = i
                while j < len(tokens) and tokens[j] in modifier_order:
                    modifiers.append(tokens[j])
                    j += 1
                
                # Check if modifiers are in correct order
                sorted_modifiers = sorted(modifiers, key=lambda x: modifier_order.index(x))
                if modifiers != sorted_modifiers:
                    issues.append({
                        'type': 'java_modifier_order',
                        'position': i,
                        'description': f'Modifiers out of order: {modifiers}',
                        'fix': f'Should be: {sorted_modifiers}',
                        'severity': 'low'
                    })
                
                i = j
            else:
                i += 1
        
        return issues
    
    def _check_java_string_concatenation(self, tokens):
        """Check Java string concatenation formatting"""
        issues = []
        
        for i in range(1, len(tokens) - 1):
            if tokens[i] == '+' and tokens[i-1] == '"' and tokens[i+1] == '"':
                issues.append({
                    'type': 'java_string_concatenation',
                    'position': i,
                    'description': 'Unnecessary string concatenation',
                    'fix': 'Combine string literals',
                    'severity': 'low'
                })
        
        return issues

    def _check_java_keyword_spacing(self, tokens):
        """Check spacing after Java keywords"""
        issues = []
        keywords = ['for', 'if', 'while', 'switch', 'catch']
        
        for i in range(len(tokens) - 1):
            if tokens[i] in keywords and tokens[i+1] == '(':
                # This is: for(, if(, while(
                issues.append({
                    'type': 'missing_space_after_keyword',
                    'position': i,
                    'description': f'Missing space after "{tokens[i]}" keyword',
                    'tokens': [tokens[i], '('],
                    'old_pattern': f'{tokens[i]}(',
                    'new_pattern': f'{tokens[i]} (',
                    'severity': 'medium'
                })
        
        return issues

    def _check_semicolon_spacing_after(self, tokens):
        """Check for missing space after semicolons - IMPROVED"""
        issues = []
        
        for i in range(len(tokens) - 1):
            if tokens[i] == ';' and i + 1 < len(tokens):
                next_token = tokens[i+1]
                
                # More specific conditions for when we need space after semicolon
                needs_space = (
                    next_token and 
                    next_token != ' ' and 
                    next_token != ')' and 
                    next_token != '}' and 
                    next_token != ';' and
                    next_token != '' and
                    not next_token.isspace() and
                    next_token != ')'  # Don't add space before closing paren
                )
                
                if needs_space:
                    # Create context-specific pattern
                    if i > 0:
                        prev_token = tokens[i-1]
                        old_pattern = f"{prev_token};{next_token}"
                        new_pattern = f"{prev_token}; {next_token}"
                    else:
                        old_pattern = f";{next_token}"
                        new_pattern = f"; {next_token}"
                    
                    issues.append({
                        'type': 'missing_space_after_semicolon',
                        'position': i,
                        'description': f'Missing space after semicolon before "{next_token}"',
                        'tokens': [';', next_token],
                        'old_pattern': old_pattern,
                        'new_pattern': new_pattern,
                        'severity': 'medium'
                    })
        
        return issues
        
    def _check_java_array_declaration(self, tokens):
        """Check Java array declaration formatting - FIXED VERSION"""
        issues = []
        
        for i in range(len(tokens) - 3):
            # Pattern: String args[] - THIS IS WRONG
            if (self._is_java_type(tokens[i]) and 
                self._is_java_identifier(tokens[i+1]) and 
                tokens[i+2] == '[' and tokens[i+3] == ']'):
                # This is WRONG: String args[] - should be String[] args
                correct_pattern = f"{tokens[i]}[] {tokens[i+1]}"
                wrong_pattern = f"{tokens[i]} {tokens[i+1]}[]"
                
                issues.append({
                    'type': 'java_array_declaration',
                    'position': i,
                    'description': f'Array declaration should be: {correct_pattern}',
                    'tokens': [tokens[i], tokens[i+1]],
                    'old_pattern': wrong_pattern,
                    'new_pattern': correct_pattern,
                    'severity': 'medium'
                })
        
        return issues
    
    def _check_python_indentation(self, code):
        """Check Python indentation consistency"""
        issues = []
        lines = code.split('\n')
        indent_size = self.rules['indentation']['size']
        
        for i, line in enumerate(lines):
            if line.strip():  # Non-empty line
                # Count leading spaces
                leading_spaces = len(line) - len(line.lstrip())
                if leading_spaces % indent_size != 0:
                    issues.append({
                        'type': 'python_indentation',
                        'line': i + 1,
                        'description': f'Indentation not multiple of {indent_size} spaces',
                        'fix': f'Use {indent_size}-space indentation consistently',
                        'severity': 'high'
                    })
        
        return issues
    
    def _check_python_tabs_vs_spaces(self, code):
        """Check for mixed tabs and spaces in Python"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            if '\t' in line:
                issues.append({
                    'type': 'python_tabs_spaces',
                    'line': i + 1,
                    'description': 'Tabs should not be used for indentation',
                    'fix': 'Convert tabs to spaces',
                    'severity': 'high'
                })
        
        return issues
    
    def _check_python_imports(self, code):
        """Check Python import formatting and order"""
        issues = []
        lines = code.split('\n')
        
        import_groups = {'stdlib': [], 'third_party': [], 'first_party': []}
        current_group = None
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                # Categorize imports
                if any(pkg in stripped for pkg in ['sys', 'os', 'math', 'json', 're']):
                    group = 'stdlib'
                elif any(pkg in stripped for pkg in ['numpy', 'pandas', 'django', 'flask']):
                    group = 'third_party'
                else:
                    group = 'first_party'
                
                import_groups[group].append((i, stripped))
        
        # Check import order
        last_line = -1
        for group in ['stdlib', 'third_party', 'first_party']:
            for line_num, _ in import_groups[group]:
                if line_num < last_line:
                    issues.append({
                        'type': 'python_import_order',
                        'line': line_num + 1,
                        'description': f'Import out of order: {group} imports should come before',
                        'fix': 'Reorder imports: standard library -> third party -> first party',
                        'severity': 'medium'
                    })
                last_line = line_num
        
        return issues
    
    def _check_python_import_spacing(self, code):
        """Check spacing between Python import groups"""
        issues = []
        lines = code.split('\n')
        
        import_lines = [i for i, line in enumerate(lines) 
                       if line.strip().startswith(('import ', 'from '))]
        
        if len(import_lines) > 1:
            expected_blank_lines = self.rules['blank_lines'].get('after_imports', 2)
            
            for i in range(1, len(import_lines)):
                lines_between = import_lines[i] - import_lines[i-1] - 1
                if lines_between != expected_blank_lines:
                    issues.append({
                        'type': 'python_import_spacing',
                        'line': import_lines[i] + 1,
                        'description': f'Expected {expected_blank_lines} blank lines between import groups, found {lines_between}',
                        'severity': 'low'
                    })
        
        return issues
    
    def _check_python_line_length(self, code):
        """Check Python line length (PEP8)"""
        issues = []
        max_length = self.rules.get('line_length', 79)
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            # Skip comments and strings for line length check
            if len(line) > max_length and not line.strip().startswith('#') and not any(char in line for char in ['"""', "'''"]):
                issues.append({
                    'type': 'python_line_length',
                    'line': i + 1,
                    'description': f'Line too long ({len(line)} > {max_length} characters)',
                    'severity': 'low'
                })
        
        return issues
    
    def _check_python_trailing_commas(self, code):
        """Check Python trailing commas"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            # Check for missing trailing comma in multi-line collections
            if stripped.endswith(',') and i + 1 < len(lines) and lines[i+1].strip():
                # This line ends with comma but next line has content - might need trailing comma
                pass
        
        return issues
    
    def _check_python_quotes(self, code):
        """Check Python quote consistency"""
        issues = []
        lines = code.split('\n')
        
        prefer_single = self.rules['quotes'].get('prefer_single', True)
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if prefer_single and '"' in stripped and "'" not in stripped and not any(x in stripped for x in ['"""', "'''"]):
                # Double quotes used where single quotes could be used
                issues.append({
                    'type': 'python_quotes',
                    'line': i + 1,
                    'description': 'Use single quotes for strings',
                    'severity': 'low'
                })
        
        return issues
    
    def _check_python_function_definitions(self, tokens):
        """Check Python function definition formatting"""
        issues = []
        
        for i in range(len(tokens) - 3):
            if tokens[i] == 'def' and i + 2 < len(tokens):
                func_name = tokens[i+1]
                # Check function name follows snake_case
                if not re.match(r'^[a-z_][a-z0-9_]*$', func_name):
                    issues.append({
                        'type': 'python_function_naming',
                        'position': i + 1,
                        'description': f'Function name "{func_name}" should be snake_case',
                        'severity': 'high'
                    })
        
        return issues
    
    def _check_python_class_definitions(self, tokens):
        """Check Python class definition formatting"""
        issues = []
        
        for i in range(len(tokens) - 2):
            if tokens[i] == 'class' and i + 1 < len(tokens):
                class_name = tokens[i+1]
                # Check class name follows CapWords convention
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', class_name):
                    issues.append({
                        'type': 'python_class_naming',
                        'position': i + 1,
                        'description': f'Class name "{class_name}" should be CapWords',
                        'severity': 'high'
                    })
        
        return issues
    
    def _check_python_decorators(self, tokens):
        """Check Python decorator formatting"""
        issues = []
        
        for i in range(len(tokens)):
            if tokens[i] == '@' and i + 1 < len(tokens):
                # Check decorator is on its own line (handled by tokenizer)
                pass
        
        return issues
    
    def _check_trailing_whitespace(self, code):
        """Check for trailing whitespace in all languages"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            if line.rstrip() != line:
                issues.append({
                    'type': 'trailing_whitespace',
                    'line': i + 1,
                    'description': 'Trailing whitespace at end of line',
                    'fix': 'Remove trailing whitespace',
                    'severity': 'low'
                })
        
        return issues
    
    def _check_python_whitespace_around_operators(self, code):
        """Check Python operator spacing rules"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            # Check for spaces around assignment operators
            if '=' in line and ' == ' not in line and ' != ' not in line:
                if ' =' not in line and '= ' not in line:
                    issues.append({
                        'type': 'python_operator_spacing',
                        'line': i + 1,
                        'description': 'Missing spaces around assignment operator',
                        'fix': 'Add spaces around =',
                        'severity': 'medium'
                    })
        
        return issues
    
    def _check_python_whitespace_in_parentheses(self, code):
        """Check Python spacing in parentheses"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            # Check for space after opening parenthesis
            if '( ' in line:
                issues.append({
                    'type': 'python_parenthesis_spacing',
                    'line': i + 1,
                    'description': 'Extra space after opening parenthesis',
                    'fix': 'Remove space after (',
                    'severity': 'low'
                })
            
            # Check for space before closing parenthesis
            if ' )' in line:
                issues.append({
                    'type': 'python_parenthesis_spacing',
                    'line': i + 1,
                    'description': 'Extra space before closing parenthesis',
                    'fix': 'Remove space before )',
                    'severity': 'low'
                })
        
        return issues
    
    def _check_cpp_includes(self, code):
        """Check C++ include formatting and order"""
        issues = []
        lines = code.split('\n')
        
        system_includes = []
        user_includes = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('#include'):
                if stripped.startswith('#include <'):
                    system_includes.append((i, stripped))
                else:
                    user_includes.append((i, stripped))
        
        # Check include order (system before user)
        if system_includes and user_includes:
            last_system = system_includes[-1][0]
            first_user = user_includes[0][0]
            if first_user < last_system:
                issues.append({
                    'type': 'cpp_include_order',
                    'line': first_user + 1,
                    'description': 'User includes should come after system includes',
                    'severity': 'medium'
                })
        
        return issues
    
    def _check_cpp_include_guard(self, code):
        """Check C++ include guard presence"""
        issues = []
        lines = code.split('\n')
        
        has_include_guard = any('#ifndef' in line for line in lines[:10])
        if not has_include_guard and any(line.strip().startswith('#include') for line in lines):
            issues.append({
                'type': 'cpp_include_guard',
                'line': 1,
                'description': 'Missing include guard in header file',
                'fix': 'Add #ifndef/#define/#endif include guard',
                'severity': 'high'
            })
        
        return issues
    
    def _check_cpp_pointers_references(self, tokens):
        """Check C++ pointer and reference spacing"""
        issues = []
        
        for i in range(len(tokens) - 1):
            if tokens[i] in ['*', '&']:
                # Check pointer/reference placement: Type* name vs Type *name
                if i > 0 and self._is_cpp_type(tokens[i-1]) and i + 1 < len(tokens) and self._is_cpp_identifier(tokens[i+1]):
                    if self.rules['spacing'].get('before_pointer', False):
                        # Should be: Type *name
                        if tokens[i-1] != ' ':
                            issues.append({
                                'type': 'cpp_pointer_spacing',
                                'position': i,
                                'description': 'Missing space before pointer/reference',
                                'tokens': [tokens[i-1], tokens[i], tokens[i+1]],
                                'old_pattern': f'{tokens[i-1]}{tokens[i]}{tokens[i+1]}',
                                'new_pattern': f'{tokens[i-1]} {tokens[i]}{tokens[i+1]}',
                                'severity': 'medium'
                            })
                    else:
                        # Should be: Type* name
                        if tokens[i+1] == ' ':
                            issues.append({
                                'type': 'cpp_pointer_spacing',
                                'position': i,
                                'description': 'Extra space after pointer/reference',
                                'tokens': [tokens[i], tokens[i+1]],
                                'old_pattern': f'{tokens[i]} ',
                                'new_pattern': f'{tokens[i]}',
                                'severity': 'medium'
                            })
        
        return issues
    
    def _check_cpp_reference_declarations(self, tokens):
        """Check C++ reference declarations"""
        issues = []
        
        for i in range(len(tokens) - 2):
            if tokens[i] == '&' and tokens[i+1] == '&':
                # Check for move reference: Type&& name
                if i + 2 < len(tokens) and self._is_cpp_identifier(tokens[i+2]):
                    pass  # This is fine
        
        return issues
    
    def _check_cpp_namespaces(self, tokens, code):
        """Check C++ namespace formatting"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('namespace'):
                # Check namespace brace placement
                if '{' in stripped and self.rules['braces'].get('namespace_brace') == 'next_line':
                    issues.append({
                        'type': 'cpp_namespace_brace',
                        'line': i + 1,
                        'description': 'Namespace opening brace should be on next line',
                        'fix': 'Move opening brace to next line',
                        'severity': 'medium'
                    })
        
        return issues
    
    def _check_cpp_class_declarations(self, tokens):
        """Check C++ class declaration formatting"""
        issues = []
        
        for i in range(len(tokens) - 2):
            if tokens[i] in ['class', 'struct'] and i + 1 < len(tokens):
                class_name = tokens[i+1]
                # Check class name follows conventions
                if not re.match(r'^[A-Z][a-zA-Z0-9_]*$', class_name):
                    issues.append({
                        'type': 'cpp_class_naming',
                        'position': i + 1,
                        'description': f'Class name "{class_name}" should start with uppercase letter',
                        'severity': 'high'
                    })
        
        return issues
    
    def _check_cpp_function_declarations(self, tokens):
        """Check C++ function declaration formatting"""
        issues = []
        
        for i in range(len(tokens) - 4):
            # Look for function patterns: [return_type] name(
            if tokens[i+2] == '(' and self._is_cpp_type(tokens[i+1]):
                func_name = tokens[i+1]
                # Check function name follows conventions
                if not re.match(r'^[a-z][a-zA-Z0-9_]*$', func_name):
                    issues.append({
                        'type': 'cpp_function_naming',
                        'position': i + 1,
                        'description': f'Function name "{func_name}" should start with lowercase letter',
                        'severity': 'high'
                    })
        
        return issues
    
    def _check_cpp_template_syntax(self, tokens):
        """Check C++ template syntax formatting"""
        issues = []
        
        for i in range(len(tokens) - 1):
            if tokens[i] == 'template' and i + 1 < len(tokens) and tokens[i+1] == '<':
                # Check template parameter spacing
                pass
        
        return issues
    
    def _check_cpp_initialization_lists(self, tokens):
        """Check C++ initialization list formatting"""
        issues = []
        
        for i in range(len(tokens) - 1):
            if tokens[i] == ':' and i > 0 and tokens[i-1] == ')':
                # This is likely an initialization list
                pass
        
        return issues
    
    def _check_cpp_access_specifiers(self, tokens):
        """Check C++ access specifier formatting"""
        issues = []
        
        for i in range(len(tokens)):
            if tokens[i] in ['public:', 'private:', 'protected:']:
                # Check access specifier indentation
                pass
        
        return issues
    
    def _check_style_issues(self, tokens, original_code):
        """Check style-specific formatting issues"""
        issues = []
        
        if self.style == 'google':
            issues.extend(self._check_google_style(tokens, original_code))
        elif self.style == 'pep8':
            issues.extend(self._check_pep8_style(tokens, original_code))
        elif self.style == 'allman':
            issues.extend(self._check_allman_style(tokens, original_code))
        
        return issues
    
    def _check_google_style(self, tokens, code):
        """Check Google style guide violations"""
        issues = []
        lines = code.split('\n')
        
        # Google style specific checks
        if self.language == 'java':
            # Google Java style: 2-space indentation
            pass
        elif self.language == 'cpp':
            # Google C++ style checks
            pass
        
        return issues
    
    def _check_pep8_style(self, tokens, code):
        """Check PEP8 style violations (Python only)"""
        issues = []
        
        if self.language == 'python':
            # PEP8 specific checks
            pass
        
        return issues
    
    def _check_allman_style(self, tokens, code):
        """Check Allman style violations"""
        issues = []
        lines = code.split('\n')
        
        # Allman style: braces on next line
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and stripped[0] == '{' and i > 0:
                prev_line = lines[i-1].strip()
                if prev_line and prev_line[-1] not in ['{', '}', ';']:
                    # Brace should be on same line according to other styles
                    pass
        
        return issues
    
    def _check_blank_lines(self, code):
        """Check blank line formatting"""
        issues = []
        lines = code.split('\n')
        
        blank_line_rules = self.rules.get('blank_lines', {})
        
        # Check for consecutive blank lines
        blank_count = 0
        for i, line in enumerate(lines):
            if not line.strip():
                blank_count += 1
                if blank_count > 1:
                    issues.append({
                        'type': 'consecutive_blank_lines',
                        'line': i + 1,
                        'description': 'Consecutive blank lines',
                        'fix': 'Remove extra blank lines',
                        'severity': 'low'
                    })
            else:
                blank_count = 0
        
        return issues
    
    def _check_indentation(self, code):
        """Check general indentation issues"""
        issues = []
        lines = code.split('\n')
        indent_size = self.rules['indentation']['size']
        
        indent_stack = [0]  # Track expected indentation levels
        
        for i, line in enumerate(lines):
            if line.strip():  # Non-empty line
                current_indent = len(line) - len(line.lstrip())
                expected_indent = indent_stack[-1]
                
                if current_indent != expected_indent:
                    issues.append({
                        'type': 'incorrect_indentation',
                        'line': i + 1,
                        'description': f'Expected indentation of {expected_indent}, found {current_indent}',
                        'severity': 'high'
                    })
                
                # Update indentation stack based on line content
                # (This is simplified - real implementation would parse block structure)
                if line.strip().endswith('{') or line.strip().endswith(':'):
                    indent_stack.append(expected_indent + indent_size)
                elif line.strip().startswith('}') or line.strip() == 'else':
                    if len(indent_stack) > 1:
                        indent_stack.pop()
        
        return issues
    
    # Helper methods for type and identifier checking
    def _is_java_type(self, token):
        """Check if token is a Java type"""
        java_types = ['void', 'int', 'long', 'float', 'double', 'boolean', 'char', 
                     'String', 'Integer', 'Long', 'Float', 'Double', 'Boolean', 'Character']
        return token in java_types or (token and token[0].isupper())
    
    def _is_java_identifier(self, token):
        """Check if token is a Java identifier"""
        return token and (token[0].isalpha() or token[0] == '_')
    
    def _is_cpp_type(self, token):
        """Check if token is a C++ type"""
        cpp_types = ['void', 'int', 'long', 'float', 'double', 'bool', 'char', 
                    'string', 'vector', 'map', 'set', 'unordered_map']
        return token in cpp_types or (token and token[0].isupper())
    
    def _is_cpp_identifier(self, token):
        """Check if token is a C++ identifier"""
        return token and (token[0].isalpha() or token[0] == '_')