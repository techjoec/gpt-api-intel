# WebSocket & Realtime Channels

**Source**: HAR captures, WebSocket traffic analysis (September-November 2025)

---

## WebSocket Event Bus

### Connection Endpoint

```
wss://ws.chatgpt.com/ws/user/{user_id}?verify={token}
```

### HTTP Upgrade Request

```
GET /ws/user/{user_id}?verify={token} HTTP/1.1
Host: ws.chatgpt.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: {base64_key}
Sec-WebSocket-Version: 13
```

### Upgrade Response

```
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: {accept_hash}
```

---

## WebSocket Bootstrap

### Session Bootstrap Endpoint

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/celsius/ws/user` | GET | 200 | Returns `{websocket_url}` for user event streams |

**Response**:
```json
{
  "websocket_url": "wss://ws.chatgpt.com/ws/user/{user_id}?verify={token}"
}
```

---

## WebSocket Protocol

### Frame Format

All frames are JSON-encoded text frames.

**Keep-alive** (sent every 30 seconds):
```json
[]
```

**Command frame**:
```json
{
  "command": "connect",
  "presence": {
    "state": "background"
  }
}
```

---

## Connection Lifecycle

### 1. Connect

**Client sends**:
```json
{
  "command": "connect",
  "presence": {
    "state": "background"
  }
}
```

**Server replies**:
```json
{
  "type": "connect",
  "subscriptions": {}
}
```

### 2. Subscribe

**Client sends**:
```json
{
  "command": "subscribe",
  "topic": "conversations"
}
```

**Server replies**:
```json
{
  "type": "subscribe",
  "topic_id": "conversations",
  "recovered": false
}
```

### 3. Presence Updates

**Client sends**:
```json
{
  "command": "presence",
  "presence": {
    "state": "foreground"
  }
}
```

**Server replies**:
```json
{
  "type": "presence"
}
```

---

## Message Types

### Conversation Updates

**Event**:
```json
{
  "type": "message",
  "payload": {
    "event": "conversation-turn-complete",
    "conversation_id": "{uuid}",
    "turn_id": "{uuid}",
    "timestamp": 1757374911
  }
}
```

**Purpose**: Notify client that assistant turn has completed.

### Presence State

| State | Meaning |
|-------|---------|
| `foreground` | Tab/window is active and visible |
| `background` | Tab/window is inactive or hidden |

Client updates presence when window focus changes.

---

## Topics

### Available Topics

| Topic | Events |
|-------|--------|
| `conversations` | `conversation-turn-complete`, `conversation-created`, `conversation-deleted` |
| `notifications` | User notifications |
| `system` | System-wide announcements |

---

## Local Indexing ("FannyPack")

### WebSocket Integration

**Purpose**: Real-time conversation indexing for local search.

**Implementation**:
- Listens to `conversation-turn-complete` events on WebSocket
- Triggers local IndexedDB updates via Dexie
- Syncs conversation titles and message snippets

### Feature Gate

```javascript
// Statsig layer 3436367576
{
  "enable_local_indexing": true,
  "enable_ux": false
}
```

When `enable_local_indexing` is true:
- WebSocket events trigger `FannyPackInitializer`
- Conversations written to IndexedDB `ConversationsDatabase`
- Local search indexed without UI exposure

---

## HTTP Polling Fallback

### Polling Endpoint

```
GET /backend-api/conversations?offset=0&limit=28
```

If WebSocket connection fails or is unavailable, client falls back to HTTP polling every 10 seconds.

---

## Server-Sent Events (SSE)

### WHAM Task Streaming

**Endpoint**:
```
POST /backend-api/wham/tasks/{task_id}/turns/{turn_id}/stream?item_type=task_turn_event
```

**Response**:
```
Content-Type: text/event-stream; charset=utf-8

event: message
data: {"id":"evt_123","item_type":"work_log_message","timestamp":1234567890,"payload":{...}}

event: message
data: {"id":"evt_124","item_type":"task_turn_event","timestamp":1234567891,"payload":{...}}
```

### Item Types

| Type | Description |
|------|-------------|
| `task_turn_event` | Task execution event |
| `work_log_message` | Worklog message (reasoning, commentary) |
| `log` | Setup/execution logs |
| `task_title_generated` | Task title auto-generated |

---

## Codex Environment Test Streaming

**Endpoint**:
```
POST /backend-api/wham/environments/test
```

**Response**: `text/event-stream; charset=utf-8`

**Purpose**: Streams environment provisioning status in real-time.

**Error**: `net::ERR_HTTP2_PROTOCOL_ERROR` after ~12s if no machines available.

---

## Realtime Telemetry

### Analytics Events

Sent over WebSocket to `analytics` topic:

```json
{
  "command": "analytics",
  "event": "fannypack.web.action_seen",
  "properties": {
    "timestamp": 1234567890
  }
}
```

### Statsig Events

Feature flag evaluations logged via WebSocket:

```json
{
  "command": "statsig",
  "event": "gate_evaluation",
  "gate": "3678527908",
  "value": true
}
```

---

## Connection Recovery

### Reconnection Strategy

On disconnect:
1. Wait 1 second
2. Attempt reconnect
3. On failure, exponential backoff: 2s, 4s, 8s, 16s, 32s (max)
4. After 5 failed attempts, fall back to HTTP polling

### Message Recovery

**Server tracks**:
- Last acknowledged message ID per client
- Buffers messages for offline clients (up to 100 messages or 5 minutes)

**On reconnect**:
- Client sends last received message ID
- Server replays missed messages
- `"recovered": true` in subscribe response indicates replay

---

## Error Handling

| Error | Recovery |
|-------|----------|
| Connection closed | Reconnect with exponential backoff |
| Invalid token | Refresh session token, reconnect |
| Topic subscription failed | Retry subscription once |
| Parse error | Log error, continue processing other messages |

---

## Performance

### Metrics

- **Connection latency**: 50-200ms
- **Keep-alive interval**: 30 seconds
- **Message latency**: 10-100ms
- **Reconnection time**: 1-5 seconds

### Bandwidth

- **Keep-alive frame**: ~10 bytes every 30s
- **Presence updates**: ~50 bytes per focus change
- **Turn complete events**: ~200-500 bytes per event

---

## Related Documentation

- **bundle-loading.md** - JavaScript bundle loading triggers WebSocket init
- **server-components.md** - RSC data fetching complements real-time updates
- **api/authentication.md** - Session tokens for WebSocket auth
- **api/codex-wham-endpoints.md** - SSE streaming endpoints
