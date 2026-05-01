# GraphRAG Inference Hackathon

## Core Objective
Proving the empirical value of graph databases over standard approaches for complex semantic lineage auditing.

This project implements a side-by-side comparison of a traditional RAG pipeline against a TigerGraph-powered GraphRAG pipeline to demonstrate advantages in:
1. **Latency:** Fast C++ graph traversal vs slower semantic retrieval.
2. **Token Efficiency:** Feeding the LLM exact context rather than bulky text chunks.
3. **Accuracy:** Discovering multi-hop relationships missed by vector search.

## Project Structure
* `data/`: Contains the generated CSV files (Node and Edge files) that map the dataset structurally, as well as the ChromaDB local vector store.
* `src/`: Python source code:
  * `parse_repo.py`: Parses a massive real-world Python repository and injects our target logic bomb lineage.
  * `baselines.py`: Embeds chunks into ChromaDB and provides functions for LLM-only and Vector RAG baselines.
  * `evaluate.py`: Calculates BERTScore and utilizes an LLM-as-a-judge system to test output accuracy.
* `app.py`: Streamlit dashboard that runs the live 3-column benchmark and visualization.

## Configuration

You must provide API keys for the live models and database:
Create `.streamlit/secrets.toml`:
```toml
HF_TOKEN = "your_huggingface_token"
TG_HOST = "your_tigergraph_host"
TG_USERNAME = "your_username"
TG_PASSWORD = "your_password"
```

## Usage
To regenerate the graph data (requires the target repo cloned in `data/langchain_repo`):
```bash
python3 src/parse_repo.py
```

To pre-compute the baseline ChromaDB index:
```bash
python3 src/baselines.py
```

To launch the live hackathon dashboard:
```bash
streamlit run app.py
```

## The Core Argument
"The baseline Vector RAG failed because its architecture forced it to throw away 50% of our dataset—the relationship data. Our GraphRAG engine utilized all 6 files, allowing it to natively trace the execution lineage."
