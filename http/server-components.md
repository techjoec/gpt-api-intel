# React Server Components (RSC) Streaming

**Source**: HAR captures, RSC payload analysis (October-November 2025)

---

## Overview

ChatGPT uses React Server Components (RSC) for server-side rendering with client-side hydration. RSC responses are binary payloads streamed over HTTP with `.data` file extensions.

---

## HTTP Endpoints

### URL Pattern

```
/codex/{route}.data?_routes=routes%2Fcodex.{path}
```

### Examples

| Route | Purpose |
|-------|---------|
| `/codex/settings/data.data` | Settings page data |
| `/codex/settings/code-review.data` | Code review settings |
| `/codex/settings/environments.data` | Environments list |
| `/codex/settings/environment/{id}.data` | Environment detail |
| `/codex/tasks/{task_id}.data` | Task detail page data |

---

## Request/Response Format

### Request Headers

```
Accept: */*
Accept-Encoding: gzip, deflate, br
Content-Type: text/x-component
```

### Response Headers

```
Content-Type: text/x-component; charset=utf-8
Content-Encoding: br
Transfer-Encoding: chunked
```

### Query Parameters

```
?_routes=routes%2Fcodex.{path}
```

Specifies which RSC route to render on the server.

---

## RSC Payload Structure

### Binary Format

RSC responses are binary-encoded React Flight format (similar to Protocol Buffers).

**Structure**:
- Header: Route metadata
- Body: Component tree with pointer references
- Pointer families: `P6`, `P8`, `P2828`, etc.

### Pointer Families (Decoded)

| Pointer | Content |
|---------|---------|
| `P6` | AccountState |
| `P8` | Profile basics |
| `2828`, `2926`, `2936` | Upgrade & checkout configs |
| `2835`, `3108`, `3636` | Model catalogue |
| `2837`, `3638`, `3639` | Homepage prompts |
| `3773` | Session env, marketing cohorts |

---

## Statsig Integration

### Dynamic Configs in RSC

RSC payloads embed Statsig feature flags and dynamic configs.

**Example Pointer**:
```
Config 3436367576: {
  enable_ux: boolean,
  enable_local_indexing: boolean
}
```

### Hashed Config Handles

| Hash | Role |
|------|------|
| `401278363` | Root Statsig bucket |
| `2173548801` | Upgrade/banner configuration |
| `2323171423` | UI variant selector |
| `3678527908` | FannyPack auto account selection gate |
| `550560761` | FannyPack modal limits |

---

## Hydration Process

### Client-Side Flow

1. **Initial HTML load** - SSR page with RSC data embedded
2. **Fetch `.data` endpoint** - Client fetches RSC payload
3. **Parse binary format** - Deserialize React Flight format
4. **Hydrate component tree** - Match server-rendered HTML with client components
5. **Apply pointers** - Resolve pointer references to actual data

### Lazy Loading

```javascript
// Bundle initialization
const rscData = await fetch('/codex/tasks/task_e_EXAMPLE.data?_routes=...')
const flight = parseFlightStream(rscData)
hydrate(flight)
```

---

## HTTP Streaming

### Chunked Transfer

RSC responses use `Transfer-Encoding: chunked` for incremental rendering.

**Benefits**:
- Server can start sending response before complete render
- Client can start hydration before full response received
- Reduces Time To Interactive (TTI)

### Chunk Format

```
{chunk_size_hex}\r\n
{binary_data}\r\n
{chunk_size_hex}\r\n
{binary_data}\r\n
0\r\n\r\n
```

---

## Caching Strategy

### Server-Side

```
Cache-Control: private, no-cache, no-store, must-revalidate
```

RSC responses are NOT cached - always fresh server-rendered content.

### Client-Side

React maintains RSC tree in memory for navigation within same session.

**Router Cache**:
- Cached for 30 seconds by default
- Invalidated on mutations
- Shared across route navigations

---

## SSR Metadata

### Hreflang & OG Tags

Gate `3125419433` enables locale-aware metadata during server render:

```html
<link rel="alternate" hreflang="en" href="..." />
<link rel="alternate" hreflang="es" href="..." />
<meta property="og:title" content="..." />
<meta property="og:description" content="..." />
```

Rendered server-side based on user locale.

---

## Performance Characteristics

### Response Size

| Route Type | Typical Size (compressed) |
|------------|--------------------------|
| Settings pages | ~5-15KB |
| Task detail | ~20-50KB |
| Environment list | ~10-30KB |

### Timing

- **TTFB (Time To First Byte)**: 50-200ms
- **Complete response**: 100-500ms
- **Hydration**: 50-150ms

---

## Error Handling

### HTTP Errors

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 401 | Unauthorized - invalid session |
| 404 | Route not found |
| 500 | Server render error |

### Fallback Behavior

On RSC fetch failure:
1. Client falls back to client-side rendering
2. Shows loading skeleton
3. Retries up to 3 times with exponential backoff
4. Surfaces error boundary if all retries fail

---

## Related Documentation

- **bundle-loading.md** - JavaScript bundle architecture
- **realtime-channels.md** - WebSocket streaming for real-time updates
- **api/chatgpt-endpoints.md** - REST API endpoints
- **api/codex-wham-endpoints.md** - WHAM API endpoints
