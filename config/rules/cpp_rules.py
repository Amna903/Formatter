CPP_RULES = {
    'indentation': {
        'size': 2,
        'use_tabs': False
    },
    'braces': {
        'class_brace': 'same_line',      # class Name {
        'function_brace': 'same_line',   # void function() {
        'if_brace': 'same_line',         # if (condition) {
        'else_brace': 'same_line',       # else {
        'namespace_brace': 'same_line',  # namespace {
        'struct_brace': 'same_line',     # struct Name {
    },
    'spacing': {
        'after_keywords': ['if', 'for', 'while', 'switch', 'catch', 'try'],
        'around_operators': True,
        'after_commas': True,
        'before_pointer': False,         # Type* name
        'before_reference': False,       # Type& name
        'after_template': True,          # template<typename T>
        'in_conditional': True,          # if (condition)
    },
    'includes': {
        'order': 'system,user',
        'angle_brackets_for_system': True,
        'grouping': True,
    },
    'blank_lines': {
        'after_includes': 1,
        'between_functions': 1,
        'between_classes': 2,
        'before_function': 1,
        'after_function': 1,
    },
    'naming': {
        'class_case': 'PascalCase',      # MyClass
        'struct_case': 'PascalCase',     # MyStruct
        'function_case': 'camelCase',    # myFunction
        'variable_case': 'camelCase',    # myVariable
        'constant_case': 'UPPER_SNAKE',  # MY_CONSTANT
        'namespace_case': 'snake_case',  # my_namespace
    },
    'line_length': 80,
    'pointer_reference': {
        'pointer_alignment': 'left',     # Type* name
        'reference_alignment': 'left',   # Type& name
    }
}