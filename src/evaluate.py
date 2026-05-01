import evaluate
from huggingface_hub import InferenceClient

def calculate_bertscore(predictions, references):
    """
    Calculate BERTScore.
    predictions: list of generated strings
    references: list of ground truth strings
    """
    try:
        bertscore = evaluate.load("bertscore")
        results = bertscore.compute(predictions=predictions, references=references, lang="en")
        # Return the F1 score of the first item
        return results["f1"][0]
    except Exception as e:
        print(f"Error calculating BERTScore: {e}")
        return 0.0

def llm_as_a_judge(response: str, hf_token: str) -> bool:
    """
    Use an LLM to judge if the response successfully identified the vulnerability lineage.
    We are looking for identification of PRMPT_0, invoke, and tensor_precision_cast.
    """
    client = InferenceClient("meta-llama/Meta-Llama-3.1-8B-Instruct", token=hf_token)
    
    prompt = f"""
    You are an impartial judge evaluating the output of an AI system for a cybersecurity threat-hunting task.
    The goal of the system was to trace a logic bomb vulnerability.
    
    A successful trace MUST identify the following specific components in the lineage:
    1. 'invoke'
    2. 'tensor_precision_cast'
    
    Here is the system's output:
    ---
    {response}
    ---
    
    Did the system successfully identify the required components? 
    Answer ONLY 'PASS' if it did, or 'FAIL' if it did not. No other text.
    """
    
    try:
        messages = [{"role": "user", "content": prompt}]
        judge_response_obj = client.chat_completion(messages, max_tokens=10)
        judge_response = judge_response_obj.choices[0].message.content.strip().upper()
        return "PASS" in judge_response
    except Exception as e:
        print(f"Error in LLM-as-a-judge: {e}")
        return False
