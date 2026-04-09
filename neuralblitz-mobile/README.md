# NeuralBlitz Mobile — React Native App

**Location:** `/home/runner/workspace/neuralblitz-mobile/`  
**Technology:** React Native (Expo) + TypeScript  
**Platform:** iOS + Android

---

## Overview

The NeuralBlitz Mobile app is a **React Native application** built with Expo, providing on-the-go access to the NeuralBlitz platform. Users can control agents, receive notifications, and issue voice commands from their mobile devices.

---

## Components

### Directory Structure

```
neuralblitz-mobile/
├── package.json                         # React Native package config
├── App.tsx                              # Root component
├── 📂 navigation/
│   └── AppNavigator.tsx                 # React Navigation setup
├── 📂 screens/
│   ├── AgentControlScreen.tsx           # Agent management screen
│   ├── NotificationsScreen.tsx          # Notifications list
│   └── VoiceCommandScreen.tsx           # Voice command interface
└── 📂 services/
    ├── ApiService.ts                    # REST API client
    ├── NotificationService.ts           # Push notification service
    └── VoiceService.ts                  # Voice command integration
```

---

## Quick Start

### Prerequisites

- Node.js 18+
- Bun or npm
- Expo CLI
- Expo Go app (for testing on device)

### Install Dependencies

```bash
cd neuralblitz-mobile
bun install
# or
npm install
```

### Start Development Server

```bash
# Start Expo
bun run start
# or
npx expo start

# Scan QR code with Expo Go app on your phone
```

---

## Screens

### 1. AgentControlScreen.tsx

**Purpose:** Manage AI agents from mobile.

**Features:**
- View list of all agents
- Create new agents
- Start/stop/pause agents
- View agent status and metrics
- Send commands to agents

**API Integration:**
- `GET /api/v2/agents` — List agents
- `POST /api/v2/agents` — Create agent
- `POST /api/v2/agents/{id}/command` — Send command
- `GET /api/v2/agents/{id}/metrics` — View metrics

### 2. NotificationsScreen.tsx

**Purpose:** View and manage push notifications.

**Features:**
- Notification list with timestamps
- Filter by type (agent status, alerts, system)
- Mark as read/unread
- Clear all notifications
- Notification settings

**Service:** `NotificationService.ts` handles push notification registration and processing.

### 3. VoiceCommandScreen.tsx

**Purpose:** Issue voice commands to NeuralBlitz.

**Features:**
- Voice input with visual feedback
- Command recognition and display
- Command execution status
- Voice command history
- Text-to-speech responses

**Service:** `VoiceService.ts` integrates with device speech recognition and NeuralBlitz API.

---

## Services

### 1. ApiService.ts

REST API client for all backend communication:

```typescript
class ApiService {
  private baseUrl: string;
  private authToken: string | null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  // Authentication
  async login(username: string, password: string): Promise<TokenResponse> {
    const response = await fetch(`${this.baseUrl}/api/v2/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    return response.json();
  }

  // Agent operations
  async getAgents(): Promise<Agent[]> {
    const response = await fetch(`${this.baseUrl}/api/v2/agents`, {
      headers: { 'Authorization': `Bearer ${this.authToken}` },
    });
    return response.json();
  }

  async createAgent(agent: AgentCreate): Promise<Agent> {
    const response = await fetch(`${this.baseUrl}/api/v2/agents`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.authToken}`,
      },
      body: JSON.stringify(agent),
    });
    return response.json();
  }

  async sendCommand(agentId: string, command: string, params: any): Promise<CommandResult> {
    const response = await fetch(`${this.baseUrl}/api/v2/agents/${agentId}/command`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.authToken}`,
      },
      body: JSON.stringify({ command, params }),
    });
    return response.json();
  }
}
```

### 2. NotificationService.ts

Push notification management:

```typescript
class NotificationService {
  async registerForPushNotifications(): Promise<string> {
    // Request permissions
    const { status } = await Notifications.getPermissionsAsync();
    if (status !== 'granted') {
      throw new Error('Notification permission denied');
    }

    // Get Expo push token
    const token = (await Notifications.getExpoPushTokenAsync()).data;
    return token;
  }

  async sendNotification(title: string, body: string): Promise<void> {
    // Send notification via API
    await apiService.post('/notifications', { title, body });
  }
}
```

### 3. VoiceService.ts

Voice command integration:

```typescript
class VoiceService {
  async startVoiceCommand(onResult: (text: string) => void): Promise<void> {
    // Use device speech recognition
    // Send transcribed text to API
    const response = await apiService.post('/voice/command', { text });
    onResult(response.result);
  }

  async speakText(text: string): Promise<void> {
    // Use device TTS
    await Speech.speak(text, { language: 'en' });
  }
}
```

---

## Navigation

The app uses React Navigation with a stack navigator:

```
AppNavigator
├── AgentControlScreen (Home)
├── NotificationsScreen
└── VoiceCommandScreen
```

---

## Configuration

### Environment Variables

Create `.env` file:

```
API_URL=http://your-server:5000
WS_URL=ws://your-server:5000
```

### App Configuration

In `app.json` or `app.config.ts`:

```json
{
  "expo": {
    "name": "NeuralBlitz Mobile",
    "slug": "neuralblitz-mobile",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#000000"
    }
  }
}
```

---

## Building for Production

### iOS

```bash
# Build for iOS
eas build --platform ios

# Or local build
npx expo run:ios
```

### Android

```bash
# Build for Android
eas build --platform android

# Or local build
npx expo run:android
```

---

## Testing

```bash
# Run tests
bun test
# or
npm test

# Run with coverage
bun test --coverage
```

---

## Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — System architecture
- [neuralblitz-dashboard/README.md](neuralblitz-dashboard/README.md) — Web dashboard
- [src/README.md](src/README.md) — API documentation
- [voice_interface/README.md](voice_interface/README.md) — Voice interface system
