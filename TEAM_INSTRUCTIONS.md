# Team Implementation Guide: GraphRAG vs. VectorRAG

Welcome to the GraphRAG Hackathon project! Our goal is to empirically prove that native graph databases outperform standard vector search approaches for complex, multi-hop reasoning tasks (specifically, semantic lineage auditing).

This document outlines how we will split up the work, implement the pipelines, and build our final presentation.

---

## 1. Local Environment Setup

Before starting, ensure everyone is working with the same environment.

```bash
# 1. Clone the repository
git clone https://github.com/Yeetl3r/graphrag-hackathon.git
cd graphrag-hackathon

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# 3. Install dependencies (we will populate requirements.txt as we go)
pip install -r requirements.txt
```

---

## 2. Understanding the Dataset

Our dataset consists of 6 CSV files located in the `data/` directory. These files represent a synthetic codebase with a mix of "golden path" signal and a lot of noisy functions.

**Nodes (The Entities):**
* `Nodes_Files.csv`: Represents individual source code files.
* `Nodes_Functions.csv`: Represents functions within those files.
* `Nodes_Prompts.csv`: Represents system prompts injected into the agent.

**Edges (The Relationships):**
* `Edges_Calls.csv`: Function A `CALLS` Function B.
* `Edges_ResidesIn.csv`: Function A or Prompt B `RESIDES_IN` File C.
* `Edges_InjectsContext.csv`: Function A `INJECTS_CONTEXT` into Prompt B.

**The Golden Path (Our Test Case):**
The pipeline must successfully trace this exact lineage:
`amx_vectorize` -> `tensor_precision_cast` -> `orchestrate_thinking_mode` -> `SYS_PROMPT_SNR_GATE`

---

## 3. The Three Workstreams

To move fast, we should divide and conquer across three distinct workstreams. 

### 👨‍💻 Workstream 1: The Baseline RAG Pipeline
**Goal:** Build the "control group" pipeline that fails or struggles gracefully.
* **Task:** Ingest the text from the 3 Node CSVs into a standard Vector Database (e.g., ChromaDB, FAISS, or Pinecone).
* **Task:** Build a standard LangChain/LlamaIndex retrieval pipeline.
* **Query:** Ask the LLM to trace the lineage from `amx_vectorize` to the prompt it injects.
* **Expected Result:** It should struggle with multi-hop reasoning, pull in noisy/irrelevant functions, burn through tokens, and take longer to return an accurate result.

### 🕸️ Workstream 2: The TigerGraph GraphRAG Pipeline
**Goal:** Build the optimized, high-performance graph pipeline.
* **Task:** Spin up a TigerGraph instance (TigerGraph Cloud free tier is recommended).
* **Task:** Create the schema and load the 6 CSV files (Nodes + Edges) into TigerGraph.
* **Task:** Write a simple GSQL query (or use pyTigerGraph) to traverse from `amx_vectorize` directly through the `CALLS` and `INJECTS_CONTEXT` edges.
* **Task:** Feed the deterministic traversal path to the LLM.
* **Expected Result:** Sub-second latency, minimal token usage, 100% accuracy.

### 📊 Workstream 3: Telemetry & Dashboard (The "Wow" Factor)
**Goal:** Build a simple, compelling UI to present to the judges.
* **Task:** Spin up a Streamlit or Gradio app.
* **Task:** Create a side-by-side view where we input the query once, and both pipelines run simultaneously.
* **Task:** Implement telemetry wrappers to track and display:
  * **Latency:** (e.g., 614ms GraphRAG vs 3400ms Baseline)
  * **Token Count:** (e.g., 150 context tokens vs 4000 context tokens)
  * **Accuracy/Correctness:** Did it find the exact path?
* **Task:** Add a visual graph representation (using PyVis or similar) to show the traversal path.

---

## 4. The Core Pitch (For the Judges)

Keep this narrative in mind for everything you build. Every feature should point back to this argument:

> *"The baseline Vector RAG failed because its architecture forced it to throw away 50% of our dataset—the relationship data. It relied on semantic guessing. Our GraphRAG engine utilized all 6 files, allowing it to natively and deterministically trace the execution lineage, resulting in a 5x speedup and a 95% reduction in token costs."*

---

## Next Steps
1. **Assign Workstreams:** Claim Workstream 1, 2, or 3.
2. **Update `requirements.txt`:** As you add libraries (e.g., `streamlit`, `langchain`, `pyTigerGraph`), add them to the requirements file and commit.
3. **Branching:** Work on your own branches (e.g., `git checkout -b feature/baseline-rag`) and merge into `main` via Pull Requests to avoid merge conflicts. 

Let's build this! 🚀
