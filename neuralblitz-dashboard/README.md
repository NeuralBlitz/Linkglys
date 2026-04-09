# NeuralBlitz Dashboard — React Web Dashboard

**Location:** `/home/runner/workspace/neuralblitz-dashboard/`  
**Technology:** React + Bun  
**Build Tool:** Bun

---

## Overview

The NeuralBlitz Dashboard is a **React-based web application** providing real-time monitoring and management of the NeuralBlitz platform. It displays agent status, ethics compliance, dimensional computing metrics, and system performance data.

---

## Components

### Directory Structure

```
neuralblitz-dashboard/
├── package.json                         # Package config with Bun
├── App.js                               # Main app with routing
├── index.js                             # Entry point
├── 📂 components/
│   ├── AgentMonitoring.js               # Agent status monitoring panel
│   ├── DashboardHeader.js               # Dashboard header with navigation
│   ├── DimensionalComputing.js          # Dimensional computing metrics display
│   ├── EthicsCompliance.js              # Ethics compliance dashboard
│   └── RealTimeMetrics.js               # Real-time performance metrics
└── 📂 public/
    └── README.md                        # Public assets
```

---

## Quick Start

### Install Dependencies

```bash
cd neuralblitz-dashboard
bun install
```

### Development Server

```bash
# Start dev server
bun run dev
# Dashboard available at http://localhost:3000
```

### Production Build

```bash
# Build for production
bun run build
# Output in build/ directory
```

---

## Components Detail

### 1. App.js — Main Application

Sets up routing and layout:
- Routes to different dashboard sections
- Global state management
- API connection configuration
- Theme/styling provider

### 2. AgentMonitoring.js

Displays agent status:
- List of all active agents
- Agent state (idle, running, error)
- Performance metrics per agent
- Agent creation/deletion controls

### 3. DashboardHeader.js

Navigation and branding:
- NeuralBlitz logo and title
- Navigation tabs
- User authentication status
- Settings access

### 4. DimensionalComputing.js

Shows dimensional processing metrics:
- 7-dimensional intent vector visualization
- φ₁-φ₇ values (Dominance, Harmony, Creation, Preservation, Transformation, Knowledge, Connection)
- Dimensional processing rates
- Cross-dimensional coherence

### 5. EthicsCompliance.js

Ethics compliance monitoring:
- Charter clause compliance (φ₁-φ₁₅)
- VPCE (Veritas Phase-Coherence Equation) score
- CECT compliance status
- Ethical drift detection alerts
- Historical compliance trends

### 6. RealTimeMetrics.js

System performance metrics:
- API response times
- Request rates
- Error rates
- Memory/CPU usage
- WebSocket connection count
- Event bus throughput

---

## API Integration

The dashboard connects to the NeuralBlitz API at `http://localhost:5000` (configurable):

```javascript
// Example API calls
const fetchAgents = async () => {
  const response = await fetch('http://localhost:5000/api/v2/agents');
  return response.json();
};

const fetchMetrics = async () => {
  const response = await fetch('http://localhost:5000/api/v2/stats');
  return response.json();
};

const fetchHealth = async () => {
  const response = await fetch('http://localhost:5000/api/v2/health');
  return response.json();
};
```

**WebSocket Connection:**
```javascript
// Real-time updates via WebSocket
const ws = new WebSocket('ws://localhost:5000/ws/connect/dashboard');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  updateMetrics(data);
};
```

---

## Configuration

### Environment Variables

Create `.env` file:

```
API_URL=http://localhost:5000
WS_URL=ws://localhost:5000
```

### Build Configuration

In `package.json`:

```json
{
  "scripts": {
    "dev": "bun run --hot index.js",
    "build": "bun build index.js --outdir build"
  }
}
```

---

## Deployment

### Static Build

```bash
bun run build
# Serve build/ directory with any static server
npx serve build/
```

### Docker

```dockerfile
FROM oven/bun:1
WORKDIR /app
COPY package.json bun.lockb ./
RUN bun install --frozen-lockfile
COPY . .
RUN bun run build
CMD ["npx", "serve", "build"]
```

---

## Testing

```bash
# Run tests (if configured)
bun test

# Lint
bun run lint
```

---

## Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — System architecture
- [src/README.md](src/README.md) — Main API documentation
- [API.md](src/API.md) — API endpoints the dashboard consumes
- [neuralblitz-mobile/README.md](neuralblitz-mobile/README.md) — Mobile app companion
