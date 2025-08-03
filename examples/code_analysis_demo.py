"""
Code Analysis Demo for JARVIS
---------------------------
This script demonstrates how to use the CodeAnalyzer class
with JARVIS for code analysis tasks.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from jarvis.utils.code_analyzer import CodeAnalyzer

def main():
    # Initialize the code analyzer with the desired model
    print("Initializing Code Analyzer...")
    analyzer = CodeAnalyzer(model="codellama:7b-instruct")
    
    # Display system information
    model_info = analyzer.get_model_info()
    print("\n=== System Information ===")
    print(f"Current Model: {model_info['current_model']}")
    print(f"Available Models: {', '.join(model_info['available_models'])}")
    
    gpu_available, gpu_name = model_info['gpu_enabled']
    print(f"GPU Available: {gpu_available}")
    if gpu_available:
        print(f"GPU Name: {gpu_name}")
    
    # Interactive code analysis
    print("\n=== Interactive Code Analysis ===")
    print("Enter your code (press Ctrl+Z then Enter when done):")
    
    # Read multi-line input
    code_lines = []
    try:
        while True:
            line = input()
            code_lines.append(line)
    except EOFError:
        pass
    
    code = '\n'.join(code_lines).strip()
    
    if not code:
        print("No code provided. Using example code...")
        code = """
        def calculate_fibonacci(n):
            if n <= 1:
                return n
            a, b = 0, 1
            for _ in range(2, n + 1):
                a, b = b, a + b
            return b
        """
    
    # Perform different types of analysis
    print("\n=== Code Explanation ===")
    print(analyzer.analyze_code(code, "explain"))
    
    print("\n=== Code Optimization ===")
    print(analyzer.analyze_code(code, "optimize"))
    
    print("\n=== Code Documentation ===")
    print(analyzer.analyze_code(code, "document"))

if __name__ == "__main__":
    main()
