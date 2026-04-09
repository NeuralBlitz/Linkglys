# Integrations — Vector Database Connectors

**Location:** `src/integrations/`  
**Language:** Python 3.11+

---

## Overview

This directory provides **vector database integration** for embedding storage and semantic search. Three major vector databases are supported: ChromaDB (local), Pinecone (cloud), and Weaviate (semantic).

---

## Supported Databases

### 1. ChromaDB (`chromadb_integration.py` — 795 lines)

**Type:** Local vector database  
**Best for:** Development, small-scale, offline use

**Features:**
- Local embedding storage
- Multiple embedding function support
- Collection management
- Metadata filtering
- Similarity search (cosine, L2, IP)
- Persistence to disk
- Multi-modal support (text, image embeddings)

**Usage:**
```python
from src.integrations.chromadb_integration import ChromaDBIntegration

chroma = ChromaDBIntegration(persist_directory="./chroma_data")

# Store embedding
chroma.add_embedding(
    collection="documents",
    text="Hello world",
    embedding=[0.1, 0.2, ...],
    metadata={"source": "doc1"}
)

# Search
results = chroma.search(
    collection="documents",
    query_embedding=[0.1, 0.2, ...],
    n_results=5
)
```

### 2. Pinecone (`pinecone_integration.py` — 586 lines)

**Type:** Cloud vector database (managed)  
**Best for:** Production, large-scale, high availability

**Features:**
- Managed cloud infrastructure
- Automatic scaling
- Real-time updates
- Namespace isolation
- Metadata filtering
- Hybrid search (dense + sparse)
- API-based management

**Setup:**
```bash
export PINECONE_API_KEY=your-api-key
export PINECONE_ENVIRONMENT=us-east1-gcp
```

### 3. Weaviate (`weaviate_integration.py`)

**Type:** Semantic vector search with GraphQL  
**Best for:** Knowledge graphs, semantic search

**Features:**
- GraphQL API for queries
- Automatic vectorization
- Multi-tenancy support
- Cross-reference queries
- Schema management
- Semantic search with context

**Setup:**
```bash
# Local Docker
docker run -p 8080:8080 semitechnologies/weaviate:latest

# Or use Weaviate Cloud
export WEAVIATE_URL=https://your-instance.weaviate.cloud
export WEAVIATE_API_KEY=your-api-key
```

---

## Comparison

| Feature | ChromaDB | Pinecone | Weaviate |
|---------|----------|----------|----------|
| **Deployment** | Local | Cloud | Cloud/Local |
| **Scaling** | Manual | Auto | Auto |
| **Query Language** | Python API | REST API | GraphQL |
| **Metadata Filtering** | ✅ | ✅ | ✅ |
| **Multi-Modal** | ✅ | ❌ | ✅ |
| **Free Tier** | Unlimited | Limited | Limited |
| **Best For** | Dev/Testing | Production | Knowledge Graphs |

---

## Usage Pattern

```python
# Choose your vector database based on use case
from src.integrations.chromadb_integration import ChromaDBIntegration
from src.integrations.pinecone_integration import PineconeIntegration
from src.integrations.weaviate_integration import WeaviateIntegration

# Development
vector_db = ChromaDBIntegration()

# Production
vector_db = PineconeIntegration(api_key="...", environment="...")

# Knowledge graph
vector_db = WeaviateIntegration(url="...")

# Common interface
vector_db.add_embedding("collection", text, embedding, metadata)
results = vector_db.search("collection", query_embedding, n_results=5)
```

---

## Testing

```bash
# Test integration modules
pytest tests/integrations/ -v

# Test module loading
python -c "
from src.integrations.chromadb_integration import ChromaDBIntegration
db = ChromaDBIntegration(persist_directory='/tmp/test_chroma')
print(f'Collections: {db.list_collections()}')
"
```

---

## Related Documentation

- [src/ README](../README.md) — Main application overview
- [Vector DB Research](../../docs/research_summary.md) — Vector database integration research
- [Graph Databases](../../docs/graph_databases_report.md) — Graph database integrations
