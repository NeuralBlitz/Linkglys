# IPFS Integration & Management System

A comprehensive InterPlanetary File System (IPFS) integration layer providing unified storage, caching, pinning, and content management across multiple IPFS backends. Supports Pinata, NFT.Storage, Web3.Storage, and Estuary services through a single Python API.

## Overview

The IPFS Integration System abstracts away the complexity of working with IPFS by providing four high-level manager classes:

| Component | Class | Purpose |
|-----------|-------|---------|
| Client Manager | `IPFSClientManager` | Unified IPFS node connectivity and operations |
| Storage Manager | `IPFSStorageManager` | File upload, download, and content addressing |
| Cache Manager | `IPFSCacheManager` | Local caching layer with TTL and eviction |
| Pin Manager | `IPFSPinManager` | Multi-provider pin management (Pinata, NFT.Storage, Web3.Storage, Estuary) |

All managers are exported via `__init__.py` for clean imports:

```python
from ipfs_integration import IPFSClientManager, IPFSStorageManager, IPFSCacheManager, IPFSPinManager
```

## Quick Start

### Prerequisites

- Python 3.9+
- Access to an IPFS node (local or remote via HTTP API)
- API keys for pinning providers (optional, for persistent pinning)

### Installation

```bash
pip install -r requirements.txt
```

### Minimal Example

```python
from ipfs_integration import IPFSClientManager, IPFSStorageManager

# Connect to local IPFS node
client = IPFSClientManager(host="localhost", port=5001, protocol="http")
client.start()

# Upload content
storage = IPFSStorageManager(client)
result = storage.upload_file("path/to/file.txt")
print(f"Content ID: {result.cid}")

# Download content
content = storage.download(result.cid)
print(content.decode())
```

## Architecture & Components

### IPFSClientManager

Manages the connection to an IPFS node (local daemon or remote gateway):

- **Connection management** — HTTP API connectivity with health checks
- **Node info** — Peer ID, version, connected peers
- **Basic operations** — Add, get, pin, unpin content
- **Error handling** — Retry logic with configurable timeouts

### IPFSStorageManager

Handles file storage and retrieval:

- **File upload** — Upload files and directories with CID generation
- **Content retrieval** — Download by CID with streaming support
- **Directory support** — Upload/download directory trees
- **Content validation** — Hash verification on download
- **Batch operations** — Multi-file upload/download

### IPFSCacheManager

Local caching layer to reduce IPFS network calls:

- **TTL-based eviction** — Configurable time-to-live for cached entries
- **LRU eviction** — Least-recently-used eviction when cache exceeds size limits
- **Disk persistence** — Cache survives restarts via local filesystem
- **Cache statistics** — Hit/miss ratios, size, entry count

### IPFSPinManager

Multi-provider pin management for persistent content availability:

| Provider | API | Use Case |
|----------|-----|----------|
| **Pinata** | Pinata API | General-purpose pinning with analytics |
| **NFT.Storage** | NFT.Storage API | NFT metadata and asset storage |
| **Web3.Storage** | Web3.Storage API | General decentralized storage |
| **Estuary** | Estuary API | High-throughput pinning with Content Clout |

**Features:**
- **Multi-provider pinning** — Pin the same CID across multiple providers for redundancy
- **Pin status tracking** — Monitor pin status across all providers
- **Automatic failover** — Retry failed pins on alternative providers
- **Pin metadata** — Store custom metadata with pins (name, description, tags)

## Features

- **Unified API** — Single interface for all IPFS operations across providers
- **Multi-provider support** — Pinata, NFT.Storage, Web3.Storage, Estuary
- **Content addressing** — Automatic CID generation and verification
- **Local caching** — TTL-based cache with disk persistence and LRU eviction
- **Redundant pinning** — Pin content across multiple providers for availability
- **Batch operations** — Upload/download multiple files in a single call
- **Metadata management** — Attach metadata to stored content
- **Health monitoring** — Node health checks and pin status tracking
- **Error resilience** — Retry logic, timeouts, and graceful degradation

## API / Usage Examples

### Upload and Pin Content

```python
from ipfs_integration import IPFSClientManager, IPFSStorageManager, IPFSPinManager

client = IPFSClientManager(host="localhost", port=5001)
client.start()

storage = IPFSStorageManager(client)

# Upload a file
result = storage.upload_file("document.pdf", metadata={"name": "My Document"})
cid = result.cid

# Pin across multiple providers
pin_manager = IPFSPinManager(
    pinata_api_key="your_pinata_key",
    pinata_secret="your_pinata_secret",
    nft_storage_api_key="your_nft_storage_key",
    web3_storage_api_key="your_web3_storage_key",
)

# Pin to all configured providers
pin_manager.pin_to_all(cid, name="My Document")

# Check pin status
status = pin_manager.get_pin_status(cid)
print(status)
```

### Cache Operations

```python
from ipfs_integration import IPFSCacheManager

cache = IPFSCacheManager(
    cache_dir="/tmp/ipfs_cache",
    max_size_mb=512,
    default_ttl_hours=24,
)

# Store in cache
cache.put(cid, content, ttl_hours=48)

# Retrieve from cache (or IPFS if not cached)
content = cache.get(cid)

# Clear expired entries
cache.cleanup_expired()

# Get cache stats
stats = cache.get_stats()
print(f"Hit ratio: {stats.hit_ratio:.2%}")
```

### Directory Operations

```python
# Upload a directory
result = storage.upload_directory("/path/to/directory")
print(f"Directory CID: {result.cid}")

# Download a directory
storage.download_directory(directory_cid, "/output/path")
```

### Batch Upload

```python
files = ["file1.txt", "file2.jpg", "file3.pdf"]
results = storage.upload_files_batch(files)

for r in results:
    print(f"{r.filename} -> {r.cid}")
```

## Testing

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=ipfs_manager --cov-report=html

# Run specific test category
pytest -v -k storage
pytest -v -k cache
pytest -v -k pin
```

## Configuration

### IPFS Node Connection

| Parameter | Default | Description |
|-----------|---------|-------------|
| `host` | `localhost` | IPFS daemon hostname |
| `port` | `5001` | IPFS HTTP API port |
| `protocol` | `http` | Connection protocol (`http`/`https`) |
| `timeout` | `30` | Request timeout in seconds |

### Cache Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `cache_dir` | `/tmp/ipfs_cache` | Local cache directory path |
| `max_size_mb` | `512` | Maximum cache size in megabytes |
| `default_ttl_hours` | `24` | Default TTL for cached entries |

### Pinning Provider Keys

| Parameter | Provider |
|-----------|----------|
| `pinata_api_key` + `pinata_secret` | Pinata |
| `nft_storage_api_key` | NFT.Storage |
| `web3_storage_api_key` | Web3.Storage |
| `estuary_api_key` | Estuary |

## Related Documentation

- [REPORT.md](./REPORT.md) — Full structured report with architecture, API reference, and code examples
- [__init__.py](./__init__.py) — Module exports and package definition
- [requirements.txt](./requirements.txt) — Python dependencies
