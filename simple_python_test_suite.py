import os
import time
import json
from core.formatter import CodeFormatter

class SimplePythonFormatterTester:
    def __init__(self):
        # 1. Initialize the formatter for Python
        self.formatter = CodeFormatter(language='python')
        self.results = []
        self.test_cases = self._generate_test_cases()
        self.output_filename = 'python_simple_test_results.json'

    def _generate_test_cases(self):
        """Generate diverse Python test cases"""
        return [
            # Category 1: Function/Class Definitions
            {
                "name": "Simple Function",
                "input": "def hello():pass",
                "expected": "def hello():\n    pass",
                "category": "definitions"
            },
            {
                "name": "Function with Args",
                "input": "def add(a,b):return a+b",
                "expected": "def add(a, b):\n    return a + b",
                "category": "definitions"
            },
            {
                "name": "Simple Class",
                "input": "class MyClass:pass",
                "expected": "class MyClass:\n    pass",
                "category": "definitions"
            },
            {
                "name": "Class with Inheritance",
                "input": "class Dog(Animal):pass",
                "expected": "class Dog(Animal):\n    pass",
                "category": "definitions"
            },
            {
                "name": "Method in Class",
                "input": "class Test:def run(self):pass",
                "expected": "class Test:\n    def run(self):\n        pass",
                "category": "definitions"
            },

            # Category 2: Control Flow (Indentation & Spacing)
            {
                "name": "If/Else Block",
                "input": "if x>0:print('P')\nelse:print('N')",
                "expected": "if x > 0:\n    print('P')\nelse:\n    print('N')",
                "category": "control_flow"
            },
            {
                "name": "For Loop",
                "input": "for i in range(10):print(i)",
                "expected": "for i in range(10):\n    print(i)",
                "category": "control_flow"
            },
            {
                "name": "While Loop",
                "input": "while True:break",
                "expected": "while True:\n    break",
                "category": "control_flow"
            },
            {
                "name": "Try/Except Block",
                "input": "try:1/0\nexcept Exception as e:pass",
                "expected": "try:\n    1 / 0\nexcept Exception as e:\n    pass",
                "category": "control_flow"
            },
            {
                "name": "Nested Block",
                "input": "if x:for y in z:print(y)",
                "expected": "if x:\n    for y in z:\n        print(y)",
                "category": "control_flow"
            },

            # Category 3: Expressions and Assignment (Spacing)
            {
                "name": "Assignment Spacing",
                "input": "x=5",
                "expected": "x = 5",
                "category": "expressions"
            },
            {
                "name": "Arithmetic Operators",
                "input": "result=a+b*c",
                "expected": "result = a + b * c",
                "category": "expressions"
            },
            {
                "name": "Comparison Operators",
                "input": "if a==b and c!=d:pass",
                "expected": "if a == b and c != d:\n    pass",
                "category": "expressions"
            },
            {
                "name": "List Creation",
                "input": "my_list=[1,2,3]",
                "expected": "my_list = [1, 2, 3]",
                "category": "expressions"
            },
            {
                "name": "Dictionary Spacing",
                "input": "my_dict={'a':1,'b':2}",
                "expected": "my_dict = {'a': 1, 'b': 2}",
                "category": "expressions"
            },

            # Category 4: Imports and General Syntax
            {
                "name": "Simple Import",
                "input": "import os,sys",
                "expected": "import os, sys",
                "category": "general"
            },
            {
                "name": "From Import",
                "input": "from module import function1,function2",
                "expected": "from module import function1, function2",
                "category": "general"
            },
            {
                "name": "Docstring Indentation",
                "input": "def func():'''Docstring'''\n    pass",
                "expected": "def func():\n    '''Docstring'''\n    pass",
                "category": "general"
            }
        ]
    
    def run_tests(self):
        """Run all test cases and generate report"""
        print("🚀 SIMPLE PYTHON FORMATTER TEST SUITE")
        print("=" * 70)
        print(f"📊 Testing {len(self.test_cases)} diverse Python code patterns...")
        print("=" * 70)
        
        passed_tests = 0
        category_results = {}
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"🧪 Test {i:2d}/{len(self.test_cases)}: {test_case['name']:<40} ", end="")
            
            # Create temporary file for testing (using .py extension)
            test_file = f"temp_test_{i}.py"
            with open(test_file, 'w') as f:
                f.write(test_case['input'])
            
            try:
                # Format the code
                start_time = time.time()
                # Assuming format_file is used for Python too
                result = self.formatter.format_file(test_file) 
                end_time = time.time()
                
                # Clean up
                os.remove(test_file)
                if os.path.exists(f"temp_test_{i}_formatted.py"):
                    os.remove(f"temp_test_{i}_formatted.py")
                
                # Calculate accuracy
                # Python formatting often involves newlines, so we must normalize both
                formatted_code = result['formatted_code'].strip()
                expected_code = test_case['expected'].strip()
                
                # Check for correct result after normalizing newlines/spaces if needed
                is_correct = formatted_code == expected_code
                
                if is_correct:
                    passed_tests += 1
                    print("✅ PASS")
                else:
                    print("❌ FAIL")
                    print(f"      Input:    {repr(test_case['input'])}")
                    print(f"      Expected: {repr(expected_code)}")
                    print(f"      Got:      {repr(formatted_code)}")
                
                # Track category results
                category = test_case['category']
                if category not in category_results:
                    category_results[category] = {'total': 0, 'passed': 0}
                category_results[category]['total'] += 1
                if is_correct:
                    category_results[category]['passed'] += 1
                
                # Store results
                self.results.append({
                    'test_id': i,
                    'name': test_case['name'],
                    'category': category,
                    'input': test_case['input'],
                    'expected': expected_code,
                    'actual': formatted_code,
                    'is_correct': is_correct,
                    'formatting_score': result.get('formatting_score', 0), # Use .get for robustness
                    'issues_found': len(result.get('issues_found', [])),
                    'fixes_applied': result.get('fixes_applied', 0),
                    'processing_time': end_time - start_time
                })
                
            except Exception as e:
                print(f"💥 ERROR: {e}")
                category = test_case['category']
                if category not in category_results:
                    category_results[category] = {'total': 0, 'passed': 0}
                category_results[category]['total'] += 1
        
        self._generate_report(passed_tests, category_results)
    
    # --- Reporting Methods (Reused from Java Test Suite) ---

    def _generate_report(self, passed_tests, category_results):
        """Generate comprehensive text-based report"""
        # ... (reporting logic)
        total_tests = len(self.test_cases)
        accuracy = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 70)
        print("📈 COMPREHENSIVE PYTHON TEST RESULTS")
        print("=" * 70)
        
        print(f"📊 OVERALL PERFORMANCE:")
        print(f"   ✅ Passed: {passed_tests}/{total_tests} ({accuracy:.1f}%)")
        print(f"   ❌ Failed: {total_tests - passed_tests}/{total_tests}")
        
        # Calculate additional metrics
        # Avoid calculating if results is empty
        if self.results:
            avg_formatting_score = sum(r['formatting_score'] for r in self.results) / total_tests
            avg_processing_time = sum(r['processing_time'] for r in self.results) / total_tests
            total_issues = sum(r['issues_found'] for r in self.results)
            total_fixes = sum(r['fixes_applied'] for r in self.results)
            fix_success_rate = (total_fixes / total_issues * 100) if total_issues > 0 else 100
        else:
            avg_formatting_score, avg_processing_time, total_issues, total_fixes, fix_success_rate = 0, 0, 0, 0, 0
        
        print(f"\n🎯 DETAILED METRICS:")
        print(f"   📝 Average Formatting Score: {avg_formatting_score:.1f}%")
        print(f"   ⚡ Average Processing Time:  {avg_processing_time:.3f}s")
        print(f"   🔍 Total Issues Detected:   {total_issues}")
        print(f"   🔧 Total Fixes Applied:     {total_fixes}")
        print(f"   💯 Fix Success Rate:        {fix_success_rate:.1f}%")
        
        print(f"\n📂 PERFORMANCE BY CATEGORY:")
        print("   " + "-" * 50)
        for category, stats in category_results.items():
            cat_accuracy = (stats['passed'] / stats['total']) * 100 if stats['total'] > 0 else 0
            print(f"   {category:<20} {stats['passed']:2d}/{stats['total']:2d} ({cat_accuracy:5.1f}%)")
        
        print(f"\n📋 TOP FAILING TEST CASES:")
        print("   " + "-" * 50)
        failed_tests = [r for r in self.results if not r['is_correct']]
        for test in failed_tests[:5]:  # Show top 5 failures
            print(f"   ❌ {test['name']}")
            print(f"      Input:    {repr(test['input'][:50])}{'...' if len(test['input']) > 50 else ''}")
            print(f"      Expected: {repr(test['expected'][:50])}{'...' if len(test['expected']) > 50 else ''}")
            print(f"      Got:      {repr(test['actual'][:50])}{'...' if len(test['actual']) > 50 else ''}")
            print()
        
        # Save detailed results
        self._save_detailed_results(accuracy, avg_formatting_score, avg_processing_time)
        
        # Generate ASCII chart
        self._generate_ascii_chart(category_results)
    
    def _generate_ascii_chart(self, category_results):
        """Generate simple ASCII bar chart for category performance"""
        print(f"\n📊 CATEGORY PERFORMANCE CHART:")
        print("   " + "-" * 50)
        
        for category, stats in category_results.items():
            accuracy = (stats['passed'] / stats['total']) * 100 if stats['total'] > 0 else 0
            bar_length = int(accuracy / 2)  # Scale for ASCII display
            bar = "█" * bar_length + " " * (50 - bar_length)
            print(f"   {category:<20} [{bar}] {accuracy:5.1f}%")
    
    def _save_detailed_results(self, accuracy, avg_score, avg_time):
        """Save detailed test results to JSON file"""
        results_summary = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_tests': len(self.results),
            'passed_tests': sum(1 for r in self.results if r['is_correct']),
            'overall_accuracy': accuracy,
            'average_formatting_score': avg_score,
            'average_processing_time': avg_time,
            'category_breakdown': {},
            'detailed_results': self.results
        }
        
        # Calculate category breakdown
        category_stats = {}
        for result in self.results:
            cat = result['category']
            if cat not in category_stats:
                category_stats[cat] = {'total': 0, 'passed': 0}
            category_stats[cat]['total'] += 1
            if result['is_correct']:
                category_stats[cat]['passed'] += 1
        
        for cat, stats in category_stats.items():
            results_summary['category_breakdown'][cat] = {
                'accuracy': (stats['passed'] / stats['total']) * 100,
                'total_tests': stats['total'],
                'passed_tests': stats['passed']
            }
        
        with open(self.output_filename, 'w') as f:
            json.dump(results_summary, f, indent=2)
        
        print(f"\n💾 Detailed results saved to '{self.output_filename}'")

def main():
    """Run the simple Python test suite"""
    tester = SimplePythonFormatterTester()
    tester.run_tests()

if __name__ == "__main__":
    main()