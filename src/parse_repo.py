import ast
import os
import csv
import uuid
import random

def parse_repo(repo_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    nodes_files = []
    nodes_functions = []
    nodes_prompts = []
    
    edges_calls = []
    edges_resides_in = []
    edges_injects_context = []
    
    # We will need some docstrings/string literals for nodes_prompts.
    benign_prompts = []
    
    print(f"Parsing repository: {repo_path}")
    
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_path)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        source = f.read()
                except Exception as e:
                    print(f"Skipping {rel_path} due to read error: {e}")
                    continue
                
                file_node_id = f"FILE_{uuid.uuid5(uuid.NAMESPACE_URL, rel_path).hex[:8]}"
                nodes_files.append({
                    'id': file_node_id,
                    'path': rel_path,
                    'content': source
                })
                
                try:
                    tree = ast.parse(source)
                except SyntaxError:
                    print(f"Skipping {rel_path} due to syntax error")
                    continue
                
                class RepoVisitor(ast.NodeVisitor):
                    def __init__(self):
                        self.current_function = None
                        self.functions_in_file = []
                        self.calls_in_file = []
                        
                    def visit_FunctionDef(self, node):
                        func_node_id = f"FUNC_{uuid.uuid5(uuid.NAMESPACE_URL, rel_path + ':' + node.name).hex[:8]}"
                        code_snippet = ast.get_source_segment(source, node)
                        if not code_snippet:
                            code_snippet = ""
                        self.functions_in_file.append({
                            'id': func_node_id,
                            'name': node.name,
                            'code': code_snippet
                        })
                        
                        edges_resides_in.append({
                            'source': func_node_id,
                            'target': file_node_id,
                            'type': 'RESIDES_IN'
                        })
                        
                        docstring = ast.get_docstring(node)
                        if docstring and len(docstring) > 20:
                            benign_prompts.append(docstring)
                            
                        # Save previous function context
                        prev_function = self.current_function
                        self.current_function = func_node_id
                        self.generic_visit(node)
                        self.current_function = prev_function
                        
                    def visit_AsyncFunctionDef(self, node):
                        self.visit_FunctionDef(node) # Treat async functions similarly
                        
                    def visit_Call(self, node):
                        if self.current_function:
                            # Try to extract function name from Call node
                            called_name = None
                            if isinstance(node.func, ast.Name):
                                called_name = node.func.id
                            elif isinstance(node.func, ast.Attribute):
                                called_name = node.func.attr
                                
                            if called_name:
                                self.calls_in_file.append({
                                    'source': self.current_function,
                                    'target_name': called_name
                                })
                                
                        self.generic_visit(node)
                        
                    def visit_Constant(self, node):
                        if isinstance(node.value, str) and len(node.value) > 50:
                             # Collect random strings that are long enough to act as noise
                             benign_prompts.append(node.value)
                        self.generic_visit(node)
                        
                visitor = RepoVisitor()
                visitor.visit(tree)
                
                nodes_functions.extend(visitor.functions_in_file)
                
                # We need to map calls by name since AST only gives us names
                # We'll resolve these edges later
                edges_calls.extend(visitor.calls_in_file)
    
    # Post-process: Add benign prompts
    print(f"Collected {len(benign_prompts)} potential benign prompts. Sampling 500.")
    sampled_prompts = random.sample(benign_prompts, min(500, len(benign_prompts)))
    for i, p in enumerate(sampled_prompts):
        prompt_id = f"PRMPT_BENIGN_{i}"
        nodes_prompts.append({
            'id': prompt_id,
            'content': p
        })
        # Randomly assign benign prompts to files
        if nodes_files:
            random_file = random.choice(nodes_files)
            edges_resides_in.append({
                'source': prompt_id,
                'target': random_file['id'],
                'type': 'RESIDES_IN'
            })
            
    # Post-process: Resolve Calls
    print("Resolving function calls by name...")
    # Create a mapping of function name to a list of IDs (since names might not be unique)
    func_name_to_ids = {}
    for fn in nodes_functions:
        name = fn['name']
        if name not in func_name_to_ids:
            func_name_to_ids[name] = []
        func_name_to_ids[name].append(fn['id'])
        
    resolved_calls = []
    for call in edges_calls:
        target_name = call['target_name']
        if target_name in func_name_to_ids:
             # Just pick the first matching name for the hackathon purposes
             target_id = func_name_to_ids[target_name][0]
             resolved_calls.append({
                 'source': call['source'],
                 'target': target_id,
                 'type': 'CALLS'
             })
             
    # --- LOGIC BOMB INJECTION ---
    print("Injecting Logic Bomb...")
    
    # 1. Add Synthetic Functions
    bomb_funcs = [
        {'id': 'FUNC_amx_vectorize', 'name': 'amx_vectorize', 'code': 'def amx_vectorize(data):\n    return tensor_precision_cast(data)'},
        {'id': 'FUNC_tensor_precision_cast', 'name': 'tensor_precision_cast', 'code': 'def tensor_precision_cast(data):\n    return orchestrate_thinking_mode(data)'},
        {'id': 'FUNC_orchestrate_thinking_mode', 'name': 'orchestrate_thinking_mode', 'code': 'def orchestrate_thinking_mode(data):\n    # INJECTS_CONTEXT: SYS_PROMPT_SNR_GATE\n    pass'}
    ]
    nodes_functions.extend(bomb_funcs)
    
    # 2. Add Synthetic Prompt
    nodes_prompts.append({
        'id': 'PRMPT_0',
        'content': 'SYS_PROMPT_SNR_GATE'
    })
    
    # 3. Add Synthetic Edges
    resolved_calls.extend([
        {'source': 'FUNC_amx_vectorize', 'target': 'FUNC_tensor_precision_cast', 'type': 'CALLS'},
        {'source': 'FUNC_tensor_precision_cast', 'target': 'FUNC_orchestrate_thinking_mode', 'type': 'CALLS'}
    ])
    
    edges_injects_context.append({
        'source': 'FUNC_orchestrate_thinking_mode',
        'target': 'PRMPT_0',
        'type': 'INJECTS_CONTEXT'
    })
    
    # 4. Attach Logic Bomb to a highly trafficked LangChain function (e.g. invoke or predict)
    # Let's find an 'invoke' function
    invoke_funcs = func_name_to_ids.get('invoke', [])
    if not invoke_funcs:
        # Fallback to __call__ or similar if invoke isn't found
        invoke_funcs = func_name_to_ids.get('__call__', [])
        
    if invoke_funcs:
        hook_source = invoke_funcs[0] # Pick the first invoke function
        print(f"Hooking Logic Bomb into: {hook_source} (invoke or __call__)")
        resolved_calls.append({
            'source': hook_source,
            'target': 'FUNC_amx_vectorize',
            'type': 'CALLS'
        })
    else:
        print("Warning: Could not find 'invoke' or '__call__' to hook the logic bomb. Picking a random function.")
        if nodes_functions:
            hook_source = nodes_functions[0]['id']
            resolved_calls.append({
                'source': hook_source,
                'target': 'FUNC_amx_vectorize',
                'type': 'CALLS'
            })
            
    # Assign synthetic functions/prompts to a file so they aren't completely dangling
    if nodes_files:
        target_file_id = nodes_files[0]['id']
        for bf in bomb_funcs:
             edges_resides_in.append({
                 'source': bf['id'],
                 'target': target_file_id,
                 'type': 'RESIDES_IN'
             })
        edges_resides_in.append({
            'source': 'PRMPT_0',
            'target': target_file_id,
            'type': 'RESIDES_IN'
        })

    # --- WRITING CSVs ---
    print("Writing CSVs...")
    
    def write_csv(filename, fieldnames, data):
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
            
    write_csv('Nodes_Files.csv', ['id', 'path', 'content'], nodes_files)
    write_csv('Nodes_Functions.csv', ['id', 'name', 'code'], nodes_functions)
    write_csv('Nodes_Prompts.csv', ['id', 'content'], nodes_prompts)
    
    write_csv('Edges_Calls.csv', ['source', 'target', 'type'], resolved_calls)
    write_csv('Edges_ResidesIn.csv', ['source', 'target', 'type'], edges_resides_in)
    write_csv('Edges_InjectsContext.csv', ['source', 'target', 'type'], edges_injects_context)
    
    print("Done!")
    print(f"Stats:")
    print(f"Files: {len(nodes_files)}")
    print(f"Functions: {len(nodes_functions)}")
    print(f"Prompts: {len(nodes_prompts)}")
    print(f"Calls: {len(resolved_calls)}")
    print(f"ResidesIn: {len(edges_resides_in)}")
    print(f"InjectsContext: {len(edges_injects_context)}")

if __name__ == "__main__":
    # We need to hit 2 million tokens, so we parse all of libs/
    repo_path = "data/langchain_repo/libs" 
    # Check if that exists, if not just data/langchain_repo
    if not os.path.exists(repo_path):
        repo_path = "data/langchain_repo"
        
    output_dir = "data"
    parse_repo(repo_path, output_dir)
