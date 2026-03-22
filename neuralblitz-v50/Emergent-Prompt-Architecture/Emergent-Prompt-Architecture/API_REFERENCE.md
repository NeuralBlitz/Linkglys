

# 🔌 EPA API Reference (v1.0)

## **Core Endpoints**

### **1. Ingest Stimuli**
`POST /api/v1/ingest`

Feeds raw data into the Ontological Lattice.

**Request:**
```json
{
  "source": "user_input",
  "content": "I need to calculate the trajectory of a rocket.",
  "timestamp": "2025-10-27T10:00:00Z",
  "metadata": {
    "user_id": "8821",
    "session_id": "session_alpha"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "trace_id": "T-v1.0-INGEST-a1b2c3d4",
  "activated_nodes": 14,
  "new_nodes_created": 2
}
```

### **2. Crystallize Prompt**
`POST /api/v1/crystallize`

Forces the system to generate a prompt based on current state, without necessarily calling the LLM (useful for debugging).

**Request:**
```json
{
  "session_id": "session_alpha",
  "target_model": "gpt-4-turbo"
}
```

**Response:**
```json
{
  "prompt_object": {
    "system_message": "You are an orbital mechanics expert...",
    "user_message": "Calculate trajectory...",
    "context_window": ["gravity_constants", "mars_atmosphere_data"]
  },
  "provenance": {
    "system_message": "derived_from_node_771",
    "context": "derived_from_vector_cluster_B"
  },
  "goldendag_hash": "e9f0c2a4e6b9d1f3..."
}
```

### **3. Reinforce / Punish**
`POST /api/v1/feedback`

Adjusts the weights of the Ontons used in the previous turn.

**Request:**
```json
{
  "trace_id": "T-v1.0-INGEST-a1b2c3d4",
  "feedback_score": -0.5,
  "reason": "Too technical"
}
```

**Response:**
```json
{
  "status": "updated",
  "nodes_decayed": ["node_technical_jargon"],
  "nodes_boosted": ["node_simple_explanation"]
}
```

---

