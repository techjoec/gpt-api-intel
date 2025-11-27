# JavaScript Bundle Loading & HTTP Resource Management

**Source**: JavaScript bundle analysis, CDN traffic inspection (October-November 2025)

---

## Overview

ChatGPT uses a multi-stage bundle loading architecture with Vite-based code splitting, lazy module loading, and React Server Components (RSC) hydration.

**Key Pattern**: Foundation → Shell → Router → Features

---

## Bundle Loading Sequence

### HTTP Load Order

```
1. cs7toih8jegb7teq  →  Foundation (React + Datadog + Router Primitives)
2. dmck639k4dv7claj  →  UI Shell (Contexts + Logger + Error Handling)
3. ncxb7ms37h0bq0rw  →  Entry Point (Hydration Bootstrap)
4. hnw079jsdm76umup  →  Router + Layout Engine
5. fht24y4dclv5s0v2  →  Conversation Route Adapter
6. dlvfyfqn731e6hy3  →  Conversation Workspace Surface
7. m45qhi5lpgsvsv3e  →  Chat Timeline + Composer
8. [60+ additional lazy chunks via __vite__mapDeps]
```

### HTTP Request Patterns

**Critical Path** (blocking):
- Foundation bundle - React + telemetry
- Shell bundle - Contexts + logger
- Entry bundle - Hydration
- Router bundle - Layout + navigation

**Deferred** (lazy-loaded):
- Route-specific bundles (conversation, workspace, settings)
- Feature chunks (promo, sidebar, attachments)

---

## CDN Resource Delivery

### Base URL

```
https://cdn.oaistatic.com/assets/{bundle_hash}.js
```

### Bundle Sizes

| Type | Size Range | Purpose |
|------|-----------|---------|
| Foundation + Shell | ~200KB | Core React runtime |
| Route bundles | ~50-150KB | Per-route functionality |
| Lazy chunks | ~10-50KB | Feature modules |

### Cache Headers

```
Cache-Control: public, max-age=31536000, immutable
```

Bundle hashes rotate with each deployment, enabling aggressive caching.

---

## Lazy Loading System

### Dependency Mapping

```javascript
__vite__mapDeps([42]) → k4ghje9xipg90eb2 (Promo Redemption)
__vite__mapDeps([83]) → itn5frgf3bcgdkwm (Navigation Sidebar)
```

**Resolution Pattern**:
```javascript
const chunkId = __vite__mapDeps([index])
await import(chunkId) // Dynamic HTTP fetch
```

### Major Lazy Chunks (60+)

- Workspace settings surfaces
- Experiments UI
- Conversation panes
- Promo redemption rail
- Navigation sidebar
- Attachment viewers
- Modal frameworks

---

## Code Splitting Strategy

### Split Boundaries

1. **Per-route splitting**: conversation, workspace, settings
2. **Per-feature splitting**: promo, sidebar, attachments
3. **Vendor splitting**: React, Datadog in foundation

### Benefits

- Initial bundle ~200KB (foundation + shell)
- Route bundles loaded on navigation
- Feature chunks loaded on interaction
- Vendor code cached separately

---

## HTTP/2 Optimizations

### Multiplexing

All bundle requests use HTTP/2 multiplexing over single connection to `cdn.oaistatic.com`.

### Request Headers

```
Accept: */*
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
```

### Response Headers

```
Content-Type: application/javascript; charset=utf-8
Content-Encoding: br
```

Brotli compression typically achieves 70-80% size reduction.

---

## Bundle Hash Rotation

### Deployment Pattern

Bundle hashes change with each deployment while maintaining stable export signatures.

**Tracking Strategy**:
- Monitor CDN URLs for hash changes
- Export names remain consistent (e.g., `yu`, `VK`, `KS`)
- Context factory signatures stable
- Statsig integration points unchanged

---

## Error Handling

### HTTP Layer

| Status | Handling |
|--------|----------|
| 200 | Bundle loaded successfully |
| 404 | Bundle not found (deployment mismatch) |
| 500 | CDN error - retry with exponential backoff |

### Application Layer

**LazyLogger** buffers errors during boot until Datadog SDK loads.

**RequestError** normalizes HTTP failures:
- Distinguishes `client` vs `server` failure types
- Stores sanitized URLs + raw error objects
- Feeds into Datadog error channel

---

## Telemetry Bootstrapping

**HTTP Sequence**:
1. Foundation bundle loads Datadog SDK from CDN
2. Shell bundle creates LazyLogger singleton
3. Entry bundle calls `initialize()`
4. LazyLogger flushes buffer to Datadog via HTTP POST
5. All subsequent logs POST to Datadog directly

---

## Module Interop

### CommonJS Compatibility

```javascript
// Pattern: gv(g) helper for CommonJS compatibility
function gv(module) {
  return module.default || module;
}
```

Enables seamless integration of vendor libraries while maintaining ES module semantics in CDN builds.

---

## Performance Characteristics

### Initial Load

- Foundation bundle: ~80KB compressed
- Shell bundle: ~60KB compressed
- Entry bundle: ~40KB compressed
- Router bundle: ~70KB compressed
- **Total critical path**: ~250KB compressed

### Route Transition

- Route-specific bundle: ~50-150KB compressed
- Loaded on-demand via dynamic import
- Cached for subsequent visits

### Feature Activation

- Feature chunks: ~10-50KB compressed
- Loaded on first interaction
- Cached indefinitely due to hash-based URLs

---

## Related Documentation

- **server-components.md** - React Server Components (RSC) streaming
- **realtime-channels.md** - WebSocket event bus
- **client-storage.md** - Local storage for bundle state
