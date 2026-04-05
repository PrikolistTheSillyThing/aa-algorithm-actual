import ast
import time
import importlib.util
import inspect
import os

FORBIDDEN_MODULES = {'os', 'sys', 'subprocess', 'requests', 'numpy', 'pandas', 'socket', 'urllib'}
MAX_EXECUTION_TIME = 0.200  # 200ms limit
VALID_RETURNS = {'C', 'D'}
ROUNDS_TO_TEST = 10

def analyze_code_security(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        file_content = file.read()
    
    try:
        tree = ast.parse(file_content)
    except SyntaxError as e:
        return False, f"Syntax Error in code: {e}"

    for node in ast.walk(tree):
        # Check 'import x'
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split('.')[0] in FORBIDDEN_MODULES:
                    return False, f"Security violation: Forbidden import '{alias.name}' detected."
        # Check 'from x import y'
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split('.')[0] in FORBIDDEN_MODULES:
                return False, f"Security violation: Forbidden import '{node.module}' detected."
                
    return True, "Code passes static security check."

def dummy_opponent(my_history, opponent_history):
    if len(my_history) % 2 == 0:
        return 'C'
    return 'D'

def validate_submission(filepath):
    print(f"\nTesting: {os.path.basename(filepath)}")
    
    # 1. Static security check
    is_safe, msg = analyze_code_security(filepath)
    if not is_safe:
        print(f"❌ FAILED: {msg}")
        return False

    # 2. Dynamic import
    try:
        module_name = os.path.splitext(os.path.basename(filepath))[0]
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        student_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(student_module)
    except Exception as e:
        print(f"❌ FAILED: Could not import file. Error: {e}")
        return False

    # 3. Signature check
    if not hasattr(student_module, 'strategy'):
        print("❌ FAILED: Function 'strategy' not found in file.")
        return False
        
    sig = inspect.signature(student_module.strategy)
    if len(sig.parameters) != 2:
        print(f"❌ FAILED: 'strategy' must take exactly 2 parameters, found {len(sig.parameters)}.")
        return False

    # 4. The sandbox test
    student_history = []
    dummy_history = []
    
    for round_num in range(1, ROUNDS_TO_TEST + 1):
        # Start the clock
        start_time = time.perf_counter()
        
        try:
            # Execute the student's function
            student_move = student_module.strategy(student_history.copy(), dummy_history.copy())
        except Exception as e:
            print(f"❌ FAILED (Round {round_num}): Code crashed during execution. Error: {e}")
            return False
            
        # Stop the clock
        execution_time = time.perf_counter() - start_time
        
        # 5. Validate output constraints
        if execution_time > MAX_EXECUTION_TIME:
            print(f"❌ FAILED (Round {round_num}): Execution time exceeded 200ms ({execution_time:.4f}s).")
            return False
            
        if student_move not in VALID_RETURNS:
            print(f"❌ FAILED (Round {round_num}): Function returned '{student_move}'. Must be 'C' or 'D'.")
            return False

        # Generate dummy move and update histories
        d_move = dummy_opponent(dummy_history, student_history)
        student_history.append(student_move)
        dummy_history.append(d_move)

    print(f"✅ PASSED: Algorithm survived {ROUNDS_TO_TEST} rounds successfully.")
    print(f"   Final Output Log: {student_history}")
    return True

if __name__ == "__main__":
    # Point this to a test file on your machine
    test_file = "team_08.py" 
    
    if os.path.exists(test_file):
        validate_submission(test_file)
    else:
        print(f"Create a file named {test_file} to run the tester.")