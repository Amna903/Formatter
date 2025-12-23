# Formatting rules and settings
class FormattingRules:
    JAVA_RULES = {
        'spaces_after_keywords': ['if', 'for', 'while', 'switch', 'catch'],
        'spaces_around_operators': ['=', '==', '!=', '<', '>', '<=', '>=', '+', '-', '*', '/', '%', '&&', '||'],
        'spaces_after_commas': True,
        'space_before_braces': True,
        'space_after_class_names': True,
        'space_after_method_names': True,
        'indentation_size': 4
    }
    
    PYTHON_RULES = {
        # --- Indentation ---
        'indentation_size': 4,
        
        # --- Spacing: Operators & Commas ---
        'spaces_after_commas': True,
        'spaces_around_operators': True,  # Generic rule for +, -, *, etc.
        'spaces_around_comparison': True, # ==, !=, <, >
        'spaces_around_assignment': True, # =, +=, -=
        
        # --- Spacing: Block Structure (Critical for Python) ---
        'space_after_colon_block': False, # e.g., def func():pass -> def func():
        'space_before_colon_block': False,
        
        # --- Blank Lines (Simplified subset of PEP 8) ---
        'blank_lines_top_level': 2,
        'blank_lines_around_methods': 1,
    }

class ModelConfig:
    LSTM_HIDDEN_SIZE = 128
    LSTM_LAYERS = 2
    VOCAB_SIZE = 10000
    TRAINING_EPOCHS = 10