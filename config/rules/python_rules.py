PYTHON_RULES = {
    'indentation': {
        'size': 4,
        'use_tabs': False
    },
    'spacing': {
        'after_commas': True,
        'around_operators': True,
        'around_assignment': True,
        'around_comparison': True,
        'around_arithmetic': True,
        'after_colon': True,
        'before_colon': False,
        'around_keyword_parameters': True,
        'in_function_def': True,
    },
    'blank_lines': {
        'top_level': 2,
        'within_class': 1,
        'within_function': 0,
        'after_imports': 2,
        'before_class': 2,
        'before_function': 2,
    },
    'imports': {
        'order': 'standard,third-party,local',
        'groups': ['stdlib', 'third_party', 'first_party'],
        'single_line_imports': True,
        'absolute_imports': True,
    },
    'quotes': {
        'prefer_single': True,
        'multiline_string': 'triple_double',  # """ for multiline
    },
    'naming': {
        'class_case': 'PascalCase',      # MyClass
        'function_case': 'snake_case',   # my_function
        'variable_case': 'snake_case',   # my_variable
        'constant_case': 'UPPER_SNAKE',  # MY_CONSTANT
        'method_case': 'snake_case',     # my_method
    },
    'line_length': 79,
    'trailing_commas': {
        'enabled': True,
        'multiline': True,
    },
    'function_def': {
        'blank_lines_after': 2,
        'blank_lines_before': 2,
    }
}