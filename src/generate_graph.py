import csv
import random
import uuid
import os
def generate_graph_data():
    # 1. Initialize our Golden Path Entities (The Signal)
    golden_file = "core/amx_acceleration.py"
    golden_func_1 = "amx_vectorize"
    golden_func_2 = "tensor_precision_cast"
    golden_func_3 = "orchestrate_thinking_mode"
    golden_prompt = "SYS_PROMPT_SNR_GATE"
    
    files = [{"File_ID": "F_0", "File_Path": golden_file, "Layer": "Core"}]
    functions = [
        {"Func_ID": "FUNC_0", "Name": golden_func_1, "Description": "Handles sub-10ms hardware vectorization", "Return": "float32"},
        {"Func_ID": "FUNC_1", "Name": golden_func_2, "Description": "Casts vectors for LLM consumption", "Return": "int8"},
        {"Func_ID": "FUNC_2", "Name": golden_func_3, "Description": "Injects context into agent thinking mode", "Return": "None"}
    ]
    prompts = [{"Prompt_ID": "PRMPT_0", "System_Instruction": "Analyze SNR-gated signal ensemble...", "Context_Vars": "int8_tensor"}]
    
    calls = [
        {"Caller_ID": "FUNC_0", "Callee_ID": "FUNC_1"},
        {"Caller_ID": "FUNC_1", "Callee_ID": "FUNC_2"}
    ]
    injects = [{"Func_ID": "FUNC_2", "Prompt_ID": "PRMPT_0"}]
    resides_in = [
        {"Entity_ID": "FUNC_0", "File_ID": "F_0"},
        {"Entity_ID": "FUNC_1", "File_ID": "F_0"},
        {"Entity_ID": "FUNC_2", "File_ID": "F_0"},
        {"Entity_ID": "PRMPT_0", "File_ID": "F_0"}
    ]

    # 2. Generate the Noise (1000+ random entities to confuse standard RAG)
    layers = ["UI", "API", "Database", "Auth", "Middleware"]
    returns = ["string", "int", "boolean", "dict", "list", "void"]
    
    for i in range(1, 100):
        f_id = f"F_{i}"
        files.append({"File_ID": f_id, "File_Path": f"src/{random.choice(layers).lower()}/module_{i}.py", "Layer": random.choice(layers)})
        
    for i in range(3, 1000):
        func_id = f"FUNC_{i}"
        functions.append({"Func_ID": func_id, "Name": f"util_process_{i}", "Description": f"Standard data processing task {i}", "Return": random.choice(returns)})
        resides_in.append({"Entity_ID": func_id, "File_ID": f"F_{random.randint(1, 99)}"})
        
        # Create random call graphs (noise edges)
        if i > 10:
            calls.append({"Caller_ID": func_id, "Callee_ID": f"FUNC_{random.randint(3, i-1)}"})
            if random.random() > 0.7:  # 30% chance of calling another function
                calls.append({"Caller_ID": func_id, "Callee_ID": f"FUNC_{random.randint(3, i-1)}"})

    for i in range(1, 50):
        p_id = f"PRMPT_{i}"
        prompts.append({"Prompt_ID": p_id, "System_Instruction": f"General instruction template {i}...", "Context_Vars": "standard_kwargs"})
        resides_in.append({"Entity_ID": p_id, "File_ID": f"F_{random.randint(1, 99)}"})
        injects.append({"Func_ID": f"FUNC_{random.randint(100, 900)}", "Prompt_ID": p_id})

    # 3. Write to CSVs perfectly formatted for Savanna
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), 'data')
    os.makedirs(data_dir, exist_ok=True)

    def write_csv(filename, fieldnames, data):
        filepath = os.path.join(data_dir, filename)
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    write_csv('Nodes_Files.csv', ["File_ID", "File_Path", "Layer"], files)
    write_csv('Nodes_Functions.csv', ["Func_ID", "Name", "Description", "Return"], functions)
    write_csv('Nodes_Prompts.csv', ["Prompt_ID", "System_Instruction", "Context_Vars"], prompts)
    write_csv('Edges_Calls.csv', ["Caller_ID", "Callee_ID"], calls)
    write_csv('Edges_InjectsContext.csv', ["Func_ID", "Prompt_ID"], injects)
    write_csv('Edges_ResidesIn.csv', ["Entity_ID", "File_ID"], resides_in)

    print("✅ Generated 6 CSV files successfully.")
    print("🚀 Golden Path Injected: amx_vectorize -> tensor_precision_cast -> orchestrate_thinking_mode -> SYS_PROMPT_SNR_GATE")

if __name__ == "__main__":
    generate_graph_data()