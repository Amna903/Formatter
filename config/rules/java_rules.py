JAVA_RULES = {
    'indentation': {
        'size': 4,
        'use_tabs': False
    },
    'braces': {
        'class_brace': 'same_line',  # class Name {
        'method_brace': 'same_line', # method() {
        'if_brace': 'same_line',     # if (condition) {
        'else_brace': 'same_line',   # else {
        'try_brace': 'same_line',    # try {
        'catch_brace': 'same_line',  # catch {
    },
    'spacing': {
        'after_keywords': ['if', 'for', 'while', 'switch', 'catch', 'synchronized', 'try'],
        'around_operators': ['=', '==', '!=', '<', '>', '<=', '>=', '+', '-', '*', '/', '%', '&&', '||', '+=', '-=', '*=', '/='],
        'after_commas': True,
        'before_class_brace': True,
        'before_method_brace': True,
        'before_array_brace': False, # int[] arr
        'after_type_cast': False,    # (Type)variable
    },
    'blank_lines': {
        'after_package': 1,
        'after_imports': 1,
        'between_methods': 1,
        'between_classes': 2,
        'before_class': 1,
    },
    'imports': {
        'order': 'java,javax,third-party',
        'wildcards': False,
        'grouping': True,
    },
    'naming': {
        'class_case': 'PascalCase',      # MyClass
        'method_case': 'camelCase',      # myMethod
        'variable_case': 'camelCase',    # myVariable
        'constant_case': 'UPPER_SNAKE',  # MY_CONSTANT
        'package_case': 'lowercase',     # com.example.package
    },
    'line_length': 100,
    'wrap_conditions': True,
}