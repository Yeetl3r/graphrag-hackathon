# GraphRAG Inference Hackathon

## Core Objective
Proving the empirical value of graph databases over standard approaches for complex semantic lineage auditing.

This project implements a side-by-side comparison of a traditional RAG pipeline against a TigerGraph-powered GraphRAG pipeline to demonstrate advantages in:
1. **Latency:** Fast C++ graph traversal vs slower semantic retrieval.
2. **Token Efficiency:** Feeding the LLM exact context rather than bulky text chunks.
3. **Accuracy:** Discovering multi-hop relationships missed by vector search.

## Project Structure
* `data/`: Contains the generated 6 CSV files (3 Node files, 3 Edge files) that map the dataset structurally.
* `src/`: Python source code, including `parse_repo.py` which parses a massive real-world Python repository and injects our target logic bomb lineage.

## Usage
To regenerate the graph data (requires the target repo cloned in `data/langchain_repo`):
```bash
python3 src/parse_repo.py
```

## The Core Argument
"The baseline Vector RAG failed because its architecture forced it to throw away 50% of our dataset—the relationship data. Our GraphRAG engine utilized all 6 files, allowing it to natively trace the execution lineage."
