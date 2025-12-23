import re

class CodeFixer:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.applied_fixes = []
        self.language = 'java'
    def apply_fixes(self, original_code, issues, language='java'):
        self.language = language
        """Apply fixes in optimal order to avoid conflicts"""
        if not issues:
            return original_code
       # Prevent Python ':' from being "fixed" as an operator
        unique_issues = self._remove_duplicate_issues(issues) # <-- Define unique_issues here

        # Prevent Python ':' from being "fixed" as an operator
        if language == 'python':
            filtered_issues = []
            for issue in unique_issues:
                fix_type = issue.get('type')
                operator = issue.get('tokens', [None, None])[1]
                
                # Check 1: Is it the generic "missing_spaces_around_operator" fix for a colon?
                is_bad_colon_fix = (
                    fix_type == 'missing_spaces_around_operator' and 
                    operator == ':'
                )
                
                # Check 2: Is the fix pattern for a colon trying to insert spaces? (e.g., ':' -> ' : ')
                is_dict_colon_fix = (
                    fix_type == 'missing_spaces_around_operator' and 
                    issue.get('new_pattern', '').strip() == ' : '
                )
                
                # If we detect a fix trying to add spaces around a block colon, SKIP it.
                if not (is_bad_colon_fix or is_dict_colon_fix):
                    filtered_issues.append(issue)
            
            # Use the filtered list for the rest of the application
            unique_issues = filtered_issues 
            # Note: The second call to self._remove_duplicate_issues(issues) later must be REMOVED.

        formatted_code = original_code
        self.applied_fixes = []
       
       
        # Group by type and apply in specific order
        fixes_by_type = {}
        for issue in unique_issues:
            fix_type = issue.get('type', 'unknown')
            if fix_type not in fixes_by_type:
                fixes_by_type[fix_type] = []
            fixes_by_type[fix_type].append(issue)
       
        # CRITICAL: Apply fixes in this specific order
        apply_order = [
            'missing_space_after_keyword',
            'missing_space_after_else',
            'missing_space_before_brace_after_else',
            'extra_space_after_opening_brace',
            'missing_spaces_around_operator',
            'java_array_declaration',
            'missing_space_before_class_brace',
            'missing_space_after_opening_brace',
            'missing_space_before_method_brace',
            'missing_space_after_comma',
            'missing_space_after_semicolon',
            # 'python_block_indent',
        ]
       
        # Apply in order
        for fix_type in apply_order:
            if fix_type in fixes_by_type:
                for issue in fixes_by_type[fix_type]:
                    fix_result = self._apply_single_fix_smart(formatted_code, issue)
                    if fix_result['success']:
                        formatted_code = fix_result['code']
                        self.applied_fixes.append(issue)
       
        # FINAL CLEANUP WITH LANGUAGE SUPPORT
        formatted_code = self._post_cleanup_pass(formatted_code, language)
        return formatted_code
    
    def _post_cleanup_pass(self, code, language='java'):
        """Final cleanup pass with language-specific handling"""
        if language == 'python':
            return self._python_cleanup_pass(code)
        else:
            return self._java_cleanup_pass(code)
    
    def _python_cleanup_pass(self, code):
        """Python-specific cleanup with proper indentation"""
        import re

        # CRITICAL FIX A: AGGRESSIVELY TIGHTEN ALL COLONS IMMEDIATELY.
        # This removes spaces added in the main fix loop (e.g., ' : ')
        code = re.sub(r'\s*:\s*', ':', code) 

        # Step 1: Basic Python formatting (Fixes commas, operators, parentheses)
        # Note: We can now remove the redundant colon tightening from _basic_python_formatting
        code = self._basic_python_formatting(code)

        # Step 2: Handle Python block indentation (uses the now-tightened colons)
        code = self._fix_python_blocks(code)

        # Step 3: Final Python cleanup (Restores dictionary spacing, cleans multiple spaces)
        code = self._final_python_cleanup(code)

        return code
    def _basic_python_formatting(self, code):
        """Apply basic Python formatting rules (Avoids breaking block colons)"""
        import re
        
        # 1. Operators: Simple spacing for binary operators (protecting against adjacent characters)
        # Using the protected map approach from the Java cleaner is safer, but for simple fix:
        operators = ['=', '!=', '+=', '-=', '*=', '/=', '<', '>', '<=', '>=', r'\+', r'-', r'\*', r'/', r'%']
        for op in operators:
            # Add space around operator, protecting against the operator being at the start/end of the line
            pattern = r'(\S)' + op + r'(\S)'
            replacement = r'\1 ' + op.replace('\\', '') + r' \2'
            code = re.sub(pattern, replacement, code)
        
        # 2. Fix commas: (a,b) -> (a, b)
        code = re.sub(r',(\S)', r', \1', code)
        
        # 3. Fix parentheses: Remove spaces *after* opening and *before* closing (essential for Python calls)
        code = re.sub(r'\(\s*', '(', code)
        code = re.sub(r'\s*\)', ')', code)
        
      
        return code
    def _fix_python_blocks(self, code):
        """Handle Python block structure with proper indentation (4 spaces)"""
        import re
        indent_size = 4
        indent_str = ' ' * indent_size
        
        # --- CRITICAL FIX: AGGRESSIVELY ENSURE COLON IS FOLLOWED BY A NEWLINE ---
        # 1. Tighten all colons, whether spaced or not.
        # This fixes the ' : ' issue from the main fix loop.
        code = re.sub(r'\s*:\s*', ':', code)
        
        # 2. Force newline insertion loop. This must run multiple times 
        # to catch nested single-line blocks (e.g., 'if x:if y:pass').
        while True:
            # Matches a colon NOT followed by a newline, OR a colon immediately
            # followed by non-whitespace characters (like 'class Test:def').
            # We explicitly replace the colon followed by a character (group 1)
            new_code = re.sub(r':(\S)', r':\n\1', code)
            
            # Also handle single-line body following a newline (e.g., in Test 18's 'pass')
            new_code = re.sub(r'\n(\s*)(pass|break|continue|return)\b', r'\n\1\4', new_code)
            
            if new_code == code:
                break
            code = new_code
        # ----------------------------------------------------------------------
        
        output_lines = []
        indentation_level = 0
        
        for line in code.split('\n'):
            stripped_line = line.strip()
            if not stripped_line:
                output_lines.append('')
                continue

            is_transition_keyword = stripped_line.startswith(('elif', 'else', 'except', 'finally'))
            is_simple_body_statement = stripped_line in ['pass', 'break', 'return', 'continue']
            
            # --- Indent Decrement for Transition Keywords (BEFORE applying indent) ---
            if is_transition_keyword:
                indentation_level = max(0, indentation_level - 1)
                    
            # --- Apply Indentation ---
            current_indent = indent_str * indentation_level
            output_lines.append(current_indent + stripped_line)
            
            # --- Calculate NEXT Indentation Change ---
            next_indent_change = 0
            
            # 1. Block Starter: Always increases indentation for the next line
            if stripped_line.endswith(':') and not stripped_line.startswith('#'):
                next_indent_change = 1
                
            # 2. Simple Statement: Decrements indentation for the next line (IF it wasn't a block starter)
            elif is_simple_body_statement and not is_transition_keyword:
                 next_indent_change = -1
            
            # --- Apply Indentation Change for the NEXT Line ---
            indentation_level = max(0, indentation_level + next_indent_change)
        
        # 2. Final Cleanup
        code = '\n'.join(output_lines)
        code = re.sub(r'\n{3,}', '\n\n', code) # Remove excessive blank lines
        
        return code
    def _is_python_block_starter(self, line):
        """Check if line starts a Python block"""
        line = line.strip()
        if not line.endswith(':'):
            return False
        
        # Don't count colons in strings or comments
        if '#' in line:
            line = line.split('#')[0].strip()
        if '"' in line or "'" in line:
            # Simple string check
            return True
            
        # Check if it's a valid block starter
        block_keywords = ['def', 'class', 'if', 'elif', 'else', 'for', 'while', 'try', 'except', 'finally', 'with']
        for keyword in block_keywords:
            if re.match(rf'^{keyword}\b', line):
                return True
                
        return True  # Assume it's a block if it ends with colon
    
    def _final_python_cleanup(self, code):
        """Final Python-specific cleanup (Restoring dictionary spacing)"""
        import re
        
        # 1. Fix dictionary/type hint colons (space after, no space before)
        # Targets 'key:value' -> 'key: value'. We use \S+ to match the key/value.
        # This addresses Test 15: "my_dict = {'a' : 1, 'b' : 2}" -> "my_dict = {'a': 1, 'b': 2}"
        code = re.sub(r"(\S+):(\S+)", r"\1: \2", code)

        # 2. Fix slice colons (no spaces, e.g. [1:5:2])
        # This is very context-dependent. Let's rely on the previous pass's tight packing for now.
        
        # 3. Clean up multiple spaces
        code = re.sub(r'  +', ' ', code)
        
        return code.strip()
    
    def _java_cleanup_pass(self, code):
        """Java-specific cleanup (your existing logic)"""
        import re
        # -------------------------------------------------------
        # 0. Protect double operators BEFORE fixing singles
        # -------------------------------------------------------
        protect_map = {
            "==": "__EQ__",
            "!=": "__NE__",
            ">=": "__GE__",
            "<=": "__LE__",
            "&&": "__AND__",
            "||": "__OR__",
            "++": "__INC__",
            "--": "__DEC__",
            "+=": "__PA__",
            "-=": "__MA__",
            "*=": "__TA__",
            "/=": "__DA__",
            "%=": "__RA__"
        }
        for op, tag in protect_map.items():
            code = code.replace(op, tag)
        # -------------------------------------------------------
        # 1. Fix spacing for SINGLE operators
        # -------------------------------------------------------
        code = re.sub(r"(?<![=!<>])\s*=\s*(?![=])", " = ", code)
        code = re.sub(r"(?<![\+])\s*\+\s*(?![\+=])", " + ", code)
        code = re.sub(r"(?<![\-])\s*\-\s*(?![\-=])", " - ", code)
        code = re.sub(r"(?<![\*])\s*\*\s*(?![\*=])", " * ", code)
        code = re.sub(r"(?<![/])\s*/\s*(?![/=])", " / ", code)
        code = re.sub(r"(?<![<])\s*<\s*(?![<>=])", " < ", code)
        code = re.sub(r"(?<![>])\s*>\s*(?![<>=])", " > ", code)
        # -------------------------------------------------------
        # 2. Restore protected multi-char operators WITH spacing
        # -------------------------------------------------------
        restore_map = {
            "__EQ__": " == ",
            "__NE__": " != ",
            "__GE__": " >= ",
            "__LE__": " <= ",
            "__AND__": " && ",
            "__OR__": " || ",
            "__INC__": "++",
            "__DEC__": "--",
            "__PA__": " += ",
            "__MA__": " -= ",
            "__TA__": " *= ",
            "__DA__": " /= ",
            "__RA__": " %= "
        }
        for tag, op in restore_map.items():
            code = code.replace(tag, op)
        # -------------------------------------------------------
        # 🎯 PATCH 1 (REFINED): CRITICAL OPERATOR CLEANUP
        # Fixes operators split by the single operator spacing rules
        code = re.sub(r"=\s*=", " == ", code) 
        code = re.sub(r"\+\s*=", " += ", code) 
        code = re.sub(r"!\s*=", " != ", code) 
        code = re.sub(r"&\s*&", " && ", code)
        code = re.sub(r"\|\s*\|", " || ", code)
        # -------------------------------------------------------
        # 3. Fix colon spacing (ternary + switch + enhanced for)
        # -------------------------------------------------------
        # Switch case specific — normalize spacing
        code = re.sub(r"case\s*(\w+)\s*:\s*", r"case \1:", code)
        # Enhanced for-loop: "s: strings" → "s : strings"
        code = re.sub(r"for\s*\((.*?)\s*:\s*(.*?)\)", r"for (\1 : \2)", code)
        # Ternary specific
        code = re.sub(r"\?\s*(\w+)\s*:\s*(\w+)", r"? \1 : \2", code)
        # -------------------------------------------------------
        # 🎯 PATCH 2: SWITCH STATEMENT CLEANUP
        # Ensures space before 'break' inside a case
        code = code.replace(":break;", ": break;")
        # -------------------------------------------------------
        # 4. Braces spacing fixes
        # -------------------------------------------------------
        # "{x" → "{ x"
        code = re.sub(r"\{(?=\w)", "{ ", code)
        # "x{" → "x {"
        code = re.sub(r"(\w)\{", r"\1 {", code)
        # "x}" → "x }"
        code = re.sub(r"(\w)\}", r"\1 }", code)
        # ";}" → "; }"
        code = code.replace(";}", "; }")
        # "}else" → "} else"
        code = re.sub(r"}\s*else", "} else", code)
        code = re.sub(r"}\s*if", "} if", code)
        code = re.sub(r"}\s*catch", "} catch", code)
        code = re.sub(r"}\s*finally", "} finally", code)
        # -------------------------------------------------------
        # 5. Java do-while fix
        code = re.sub(r"\}\s*while", "} while", code)
        # -------------------------------------------------------
        # 6. Fix bitwise OR spacing in expressions
        code = re.sub(r"(\w)\|(\w)", r"\1 | \2", code)
        # -------------------------------------------------------
        # 7. Clean up doubled spaces
        code = re.sub(r"\s{2,}", " ", code)
        # -------------------------------------------------------
        # PATCH 3: KEYWORD SPACING FIX
        keywords = ['if', 'else', 'while', 'for', 'switch', 'do', 'try', 'catch', 'finally']
        for kw in keywords:
            code = re.sub(rf"{re.escape(kw)}\s*\(\s*", rf"{kw} (", code) 
            code = re.sub(rf"{re.escape(kw)}\s*{{\s*", rf"{kw} {{", code) 
        # -------------------------------------------------------
        # Array init spaces
        code = re.sub(r"{\s+(?=[-\d\"'])", "{", code)
        code = re.sub(r"([-\d\"'])\s+}", r"\1}", code)
        # -------------------------------------------------------
        # Method param closing ) {
        code = re.sub(r"\)\s*\{", r") {", code)
        # -------------------------------------------------------
        # Add spaces after } before next word or }
        code = re.sub(r"}\s*(\w)", r"} \1", code)
        code = re.sub(r"}\s*}", "} }", code)
        # -------------------------------------------------------
        # Add space after semicolon if not followed by space, newline, or }
        code = re.sub(r";(?![ \n}])", "; ", code)
        # -------------------------------------------------------
        # Clean up doubled spaces again
        code = re.sub(r"\s{2,}", " ", code)
        return code
       
    def _apply_operator_fix(self, code, issue):
        """Apply operator spacing fixes with proper compound operator support"""
        old_pattern = issue.get('old_pattern', '')
        new_pattern = issue.get('new_pattern', '')
       
        # --- CRITICAL PYTHON COLON FIX ---
        if self.language == 'python' and old_pattern == ':' and new_pattern == ' : ':
            return {'success': False, 'code': code, 'reason': 'Python block colon fix deferred.'}
        # ---------------------------------
        
        # Handle compound operators specially
        compound_ops = ['+=', '-=', '*=', '/=', '%=', '==', '!=', '&&', '||']
       
        # Check if this is a compound operator
        for op in compound_ops:
            if op in old_pattern and op in new_pattern:
                # First, fix any broken operators (like "x + = 5")
                broken_patterns = [
                    f"{op[0]} {op[1]}", # "x + = 5"
                    f"{op[0]} {op[1]}", # "x + = 5"
                ]
                for broken in broken_patterns:
                    if broken in code:
                        code = code.replace(broken, op)
               
                # Now apply proper spacing around the compound operator
                if old_pattern in code:
                    return {'success': True, 'code': code.replace(old_pattern, new_pattern, 1)}
       
        # For regular operators
        if old_pattern in code:
            return {'success': True, 'code': code.replace(old_pattern, new_pattern, 1)}
       
        return {'success': False, 'code': code, 'reason': 'operator pattern not found'}
        
    def _remove_duplicate_issues(self, issues):
        """Remove duplicate issues that have the same fix pattern"""
        seen_patterns = set()
        unique_issues = []
       
        for issue in issues:
            pattern_key = (issue.get('old_pattern', ''), issue.get('new_pattern', ''))
           
            # Skip if we've already seen this exact pattern
            if pattern_key in seen_patterns:
                continue
               
            # Skip if the pattern is empty
            if not pattern_key[0] or not pattern_key[1]:
                continue
               
            seen_patterns.add(pattern_key)
            unique_issues.append(issue)
       
        print(f"🔍 Removed {len(issues) - len(unique_issues)} duplicate issues")
        return unique_issues
    
    def _apply_single_fix_smart(self, code, issue):
        """Apply a single fix with intelligent pattern matching"""
        try:
            old_pattern = issue.get('old_pattern', '')
            new_pattern = issue.get('new_pattern', '')
           # Python-specific: block colon must NOT be replaced early
            if issue.get("old_pattern") == ":" and self.language == "python":
                # This is an extra check, but _apply_operator_fix has the hard guard now
                return {'success': False, 'code': code, 'reason': 'colon deferred to cleanup'}
            if not old_pattern or not new_pattern:
                return {'success': False, 'code': code, 'reason': 'missing pattern'}
           
            # Check if fix is already applied
            if self._is_fix_already_applied(code, old_pattern, new_pattern):
                return {'success': False, 'code': code, 'reason': 'already fixed'}
           
            # Special handling for different fix types
            fix_type = issue.get('type', '')
           
            if fix_type == 'java_array_declaration':
                return self._apply_array_declaration_fix(code, issue)
            elif 'brace' in fix_type:
                return self._apply_brace_fix(code, issue)
            elif 'operator' in fix_type:
                return self._apply_operator_fix(code, issue)
            elif 'keyword' in fix_type:
                return self._apply_keyword_fix(code, issue)
            elif 'semicolon' in fix_type:
                return self._apply_semicolon_fix(code, issue)
            elif fix_type == 'python_block_indent': 
                return self._apply_python_block_fix(code, issue)
            else:
                return self._apply_generic_fix(code, issue)
               
        except Exception as e:
            print(f"Error applying fix: {e}")
            return {'success': False, 'code': code, 'reason': str(e)}
   
    def _is_fix_already_applied(self, code, old_pattern, new_pattern):
        """Check if the fix has already been applied"""
        # If new pattern exists and old pattern doesn't exist in the same context
        if new_pattern in code:
            # Check if old pattern is still present nearby
            new_index = code.find(new_pattern)
            if new_index != -1:
                # Look for old pattern in the surrounding area
                context_start = max(0, new_index - 20)
                context_end = min(len(code), new_index + len(new_pattern) + 20)
                context = code[context_start:context_end]
               
                # If old pattern is not in the context, fix is already applied
                return old_pattern not in context
        return False
   
    def _apply_generic_fix(self, code, issue):
        """Apply a generic pattern replacement fix"""
        old_pattern = issue.get('old_pattern', '')
        new_pattern = issue.get('new_pattern', '')
       
        if old_pattern in code:
            # Replace only the first occurrence to be safe
            code = code.replace(old_pattern, new_pattern, 1)
            return {'success': True, 'code': code}
        else:
            # Try alternative patterns
            alternatives = self._generate_alternative_patterns(old_pattern)
            for alt_pattern in alternatives:
                if alt_pattern in code:
                    alt_new = self._generate_alternative_new_pattern(alt_pattern, new_pattern)
                    code = code.replace(alt_pattern, alt_new, 1)
                    return {'success': True, 'code': code}
           
            return {'success': False, 'code': code, 'reason': 'pattern not found'}
   
    def _apply_brace_fix(self, code, issue):
        """Apply brace spacing fixes with context awareness"""
        old_pattern = issue.get('old_pattern', '')
        new_pattern = issue.get('new_pattern', '')
       
        # For brace fixes, be more precise about the replacement
        if old_pattern in code:
            # Count occurrences to understand the context
            occurrences = code.count(old_pattern)
           
            if occurrences == 1:
                # Simple replacement for single occurrence
                code = code.replace(old_pattern, new_pattern)
                return {'success': True, 'code': code}
            else:
                # For multiple occurrences, be more careful
                # Replace only the first occurrence that makes sense
                lines = code.split('\n')
                for i, line in enumerate(lines):
                    if old_pattern in line and new_pattern not in line:
                        lines[i] = line.replace(old_pattern, new_pattern, 1)
                        return {'success': True, 'code': '\n'.join(lines)}
               
                return {'success': False, 'code': code, 'reason': 'ambiguous brace pattern'}
        else:
            return {'success': False, 'code': code, 'reason': 'brace pattern not found'}
   
    def _apply_keyword_fix(self, code, issue):
        """Apply keyword spacing fixes"""
        old_pattern = issue.get('old_pattern', '')
        new_pattern = issue.get('new_pattern', '')
       
        if old_pattern in code:
            code = code.replace(old_pattern, new_pattern, 1)
            return {'success': True, 'code': code}
        else:
            return {'success': False, 'code': code, 'reason': 'keyword pattern not found'}
   
    def _apply_array_declaration_fix(self, code, issue):
        """Special handling for Java array declaration fixes"""
        try:
            tokens = issue.get('tokens', [])
            if len(tokens) >= 4:
                type_name = tokens[0] # e.g., "String"
                var_name = tokens[1] # e.g., "args"
               
                # Look for the specific pattern in context
                target_pattern = f"{type_name} {var_name}[]"
                if target_pattern in code:
                    code = code.replace(target_pattern, f"{type_name}[] {var_name}", 1)
                    return {'success': True, 'code': code}
               
                # Try alternative pattern with space
                alt_pattern = f"{type_name} {var_name} []"
                if alt_pattern in code:
                    code = code.replace(alt_pattern, f"{type_name}[] {var_name}", 1)
                    return {'success': True, 'code': code}
           
            return {'success': False, 'code': code, 'reason': 'array pattern not found'}
        except Exception as e:
            return {'success': False, 'code': code, 'reason': str(e)}
   
    def _apply_python_block_fix(self, code, issue):
        """
        Applies a direct replacement for python block indentation issue
        NOTE: This is now bypassed as the fix is handled globally in _post_cleanup_pass.
        """
        # This fix type is deferred to the final _python_cleanup_pass
        return {'success': False, 'code': code, 'reason': 'Python block fix deferred to global cleanup'}
   
    def _generate_alternative_patterns(self, pattern):
        """Generate alternative patterns that might match the code"""
        alternatives = []
       
        # For brace patterns
        if pattern.endswith('{'):
            base = pattern[:-1]
            alternatives.extend([
                f'{base} {{',
                f'{base} {{',
                f'{base}{{ ',
            ])
       
        # For operator patterns
        if '=' in pattern and ' = ' not in pattern:
            parts = pattern.split('=')
            if len(parts) == 2:
                alternatives.extend([
                    f'{parts[0]}= {parts[1]}',
                    f'{parts[0]} ={parts[1]}',
                ])
       
        return alternatives
   
    def _generate_operator_alternatives(self, pattern):
        """Generate alternative operator patterns"""
        alternatives = []
       
        # For assignment operators
        if '=' in pattern:
            if ' = ' not in pattern: # Not already spaced
                parts = pattern.split('=')
                if len(parts) == 2:
                    alternatives.extend([
                        f'{parts[0]}= {parts[1]}', # Space after
                        f'{parts[0]} ={parts[1]}', # Space before
                    ])
       
        return alternatives
        
    def _apply_semicolon_fix(self, code, issue):
        """Apply semicolon spacing fix - HANDLES MULTIPLE OCCURRENCES"""
        try:
            old_pattern = issue.get('old_pattern', '')
            new_pattern = issue.get('new_pattern', '')
           
            if not old_pattern or not new_pattern:
                return {'success': False, 'code': code, 'reason': 'missing pattern'}
           
            # Count how many times this pattern appears
            occurrences = code.count(old_pattern)
            new_occurrences = code.count(new_pattern)
           
            # If all occurrences are already fixed, skip
            if occurrences == 0 and new_occurrences > 0:
                return {'success': False, 'code': code, 'reason': 'already fixed'}
           
            # If there are multiple occurrences, replace them all
            if occurrences > 0:
                # Replace ALL occurrences to handle multiple semicolons in for loops
                code = code.replace(old_pattern, new_pattern)
                return {'success': True, 'code': code}
            else:
                # Try alternative patterns
                alternatives = self._generate_semicolon_alternatives(old_pattern)
                for alt_pattern in alternatives:
                    if alt_pattern in code:
                        code = code.replace(alt_pattern, new_pattern)
                        return {'success': True, 'code': code}
               
                return {'success': False, 'code': code, 'reason': 'pattern not found'}
        except Exception as e:
            return {'success': False, 'code': code, 'reason': str(e)}
   
    def _generate_semicolon_alternatives(self, pattern):
        """Generate alternative semicolon patterns"""
        alternatives = []
       
        # For semicolon patterns like "0;i"
        if ';' in pattern:
            parts = pattern.split(';')
            if len(parts) == 2:
                # Try patterns with different spacing
                alternatives.extend([
                    f"{parts[0]}; {parts[1]}", # Already has space
                    f"{parts[0]} ;{parts[1]}", # Space before semicolon
                    f"{parts[0]} ; {parts[1]}", # Space both sides
                ])
       
        return alternatives
       
    def _generate_alternative_new_pattern(self, old_pattern, new_pattern):
        """Generate new pattern corresponding to alternative old pattern"""
        # For most cases, the new pattern remains the same
        return new_pattern

def fix_java_tokens(tokens):
    fixed_tokens = []
    i = 0
    while i < len(tokens):
        token = tokens[i]

        # Space after control keywords
        if token in ['if', 'for', 'while', 'switch', 'catch', 'do']:
            if i + 1 < len(tokens) and tokens[i+1] == '(':
                fixed_tokens.append(token)
                fixed_tokens.append(' ')
                i += 1
                continue

        # else spacing
        if token == 'else':
            if i + 1 < len(tokens) and tokens[i+1] == '{':
                fixed_tokens.append(token)
                fixed_tokens.append(' ')
                i += 1
                continue

        # For-loop semicolons spacing
        if token == ';' and fixed_tokens and i + 1 < len(tokens):
            if tokens[i+1] not in [' ', ')', '{', ';']:
                fixed_tokens.append(';')
                fixed_tokens.append(' ')
                i += 1
                continue

        # Default: append token
        fixed_tokens.append(token)
        i += 1

    return fixed_tokens