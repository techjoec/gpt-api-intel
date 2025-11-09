# JavaScript Obfuscation & Encoding Patterns

**Source**: Bundle deobfuscation, HAR capture analysis (October-November 2025)
**Artifacts Analyzed**: 4,732 obfuscation artifacts (3,537 inline base64 blobs, 1,194 API strings, 1 hex-escape)

---

## Obfuscation Techniques

### 1. Identifier Hashing

**Pattern**: Hash-based feature gate identifiers

```javascript
// Statsig gate check
he(i, "3678527908")  // FannyPack auto account selection
he(i, "2067628123")  // Preview backend switcher
he(i, "948657827")   // Streaming favicon enrichment
```

**Purpose**: Prevent feature discovery via source code inspection.

---

### 2. Base64 Encoding

**Usage**: 3,537 inline base64 blobs across bundles

**Common Patterns**:

```javascript
// localStorage keys
atob("b2FpL2FwcHMvaXNOb0F1dGhDaGF0VHJhaW5pbmdFbmFibGVk")
// → "oai/apps/isNoAuthChatTrainingEnabled"

// API endpoints
atob("L2JhY2tlbmQtYXBpL3NlbnRpbmVsL2NoYXQtcmVxdWlyZW1lbnRz")
// → "/backend-api/sentinel/chat-requirements"
```

---

### 3. String Array Concatenation

**Pattern**: Strings split across multiple array entries

```javascript
const strings = ["backend", "-", "api", "/", "tasks"];
const endpoint = strings.join(""); // "backend-api/tasks"
```

**Purpose**: Evade simple string scanning.

---

### 4. Module Hash Obfuscation

**Pattern**: Bundle names are cryptographic hashes

```
cs7toih8jegb7teq.js  // Foundation bundle
dmck639k4dv7claj.js  // UI Shell bundle
hnw079jsdm76umup.js  // Router bundle
```

**Note**: Export names remain stable across rotations.

---

## Decoded Artifacts

### localStorage Keys

**Total**: 257 tokens analyzed

**Prefix Distribution**:
- 120 begin with `oai/apps/`
- 67 include `hasSeen*` pattern
- Remainder: Tatertot, Projects, connectors, Moonshine, PromoRedemption, Canvas

**High-Signal Keys**:
```
oai/apps/isNoAuthChatTrainingEnabled
oai/apps/noAuthRateLimitState
oai/apps/hasSeenTatertotUpsell
oai/apps/l1239dk1/codexOnboardingState
oai/apps/restoreMessageAfterOauthRedirect
```

---

### API Endpoints

**Total**: 1,194 suspicious API strings

**Examples**:
```
/backend-api/sentinel/chat-requirements
/backend-api/aip/connectors/list_accessible
/backend-api/wham/tasks/{task_id}/turns
/backend-api/celsius/ws/user
/v1/initialize
```

See `api/chatgpt-endpoints.md` and `api/codex-wham-endpoints.md` for complete endpoint catalogs.

---

### Feature Gate Hashes

**Total**: 996 hash pointers resolved

**High-Frequency Hashes**:
| Hash | Feature |
|------|---------|
| `2067628123` | Preview web / SA-server backend switcher |
| `948657827` | Streaming favicon enrichment |
| `2711769261` | Projects migration NUX |
| `491279851` | Projects Snorlax guard |
| `3125419433` | SSR hreflang + metadata |
| `4011688770` | OpenTelemetry bootstrap |
| `1627380539` | GPT-4o → GPT-5 favouring heuristics |
| `3678527908` | FannyPack auto account selection |
| `1422501431` | FannyPack V2 account selection |

See `research/feature-gates.md` for complete catalog.

---

## Statsig Integration

### Hash Cross-Reference

**Deobfuscated Patterns**:

```javascript
// Gate evaluation
this.$emt({ name: "gate_evaluation", gate: "3678527908" })

// Experiment evaluation
this.$emt({ name: "experiment_evaluation", experiment: "1792765184" })

// Dynamic config
getConfig("3436367576") // FannyPack config
```

### Telemetry Obfuscation

**Statsig Events**: 182+ unique event names extracted from bundles

**Pattern**:
```javascript
_getStatsigGlobal()
_getStatsigGlobalFlag()
StatsigMetadataProvider()
StatsigSession()
StatsigUser()
```

---

## Sentinel Anti-Bot System

### HTTP Flow

1. **Initial Page Load**: HTML includes Sentinel bootstrap code
2. **SDK Load**: Fetch `/backend-api/sentinel/sdk.js`
3. **Challenge**: SDK generates proof-of-work challenge
4. **Submission**: POST `/backend-api/sentinel/chat-requirements`
5. **Token**: Server returns session token
6. **Headers**: Token attached to subsequent API requests

### Obfuscation

Sentinel SDK heavily obfuscated:
- Variable names minified
- Control flow flattened
- String literals base64-encoded
- Proof-of-work algorithm obscured

**Purpose**: Prevent bot automation.

---

## HTTP Response Obfuscation

### Binary Payloads

React Server Components (RSC) use binary-encoded payloads:

```
Content-Type: text/x-component
```

**Format**: React Flight format (proprietary binary serialization)

**Deobfuscation**: Requires React Flight deserializer.

---

## Deobfuscation Tools

### Analysis Scripts (in `tools/` directory)

| Script | Purpose |
|--------|---------|
| `tools/hash_scanner.py` | Extract hashed identifiers from bundles |
| `tools/obfuscation_scanner.py` | Identify obfuscation patterns and encoded artifacts |
| `tools/statsig_inventory.py` | Build feature flag inventories from payloads |
| `tools/statsig_resolver.py` | Resolve feature gate hashes to readable names |
| `tools/service_function_scanner.py` | Extract service function signatures |

### Raw Data

| File | Contents |
|------|----------|
| `data/decoded_strings_sources.json` | 87KB - Base64 decoded strings with sources |
| `data/gibberish_decoded.json` | 46KB - Obfuscated string corpus (internal) |
| `data/gibberish_decoded_external.json` | 10KB - Obfuscated strings (external captures) |
| `data/statsig_inventory.json` | 174KB - Complete Statsig gate/experiment inventory |

---

## Security Implications

### What's Obfuscated

✅ Feature gate names
✅ localStorage key names
✅ API endpoint paths
✅ Statsig event names
✅ Internal function names
✅ Sentinel anti-bot logic

### What's NOT Obfuscated

❌ HTTP endpoints (visible in network traffic)
❌ Request/response formats (observable via HAR)
❌ WebSocket messages (plaintext JSON)
❌ localStorage values (readable in DevTools)
❌ Cookie values (readable in DevTools)

---

## HTTP Traffic Analysis

### Identifying Obfuscated Requests

**Pattern**: Base64-encoded query parameters

```
GET /api/some-endpoint?param=eyJmZWF0dXJlIjoiZmFubnlwYWNrIn0
```

**Decoded**:
```json
{"feature":"fannypack"}
```

### Header Obfuscation

None observed - all HTTP headers use standard names:
- `Authorization`
- `ChatGPT-Account-Id`
- `Oai-Device-Id`
- `Content-Type`

---

## Bypassing Obfuscation

### Network-Based Analysis

✅ **Recommended**: Capture HTTP traffic via HAR exports
✅ **Recommended**: Analyze WebSocket messages (plaintext)
✅ **Recommended**: Inspect actual API requests/responses

❌ **Avoid**: Trying to deobfuscate minified JavaScript
❌ **Avoid**: Reverse-engineering Sentinel SDK

---

## Related Documentation

- **bundle-loading.md** - Bundle architecture (where obfuscation lives)
- **client-storage.md** - localStorage keys (many base64-encoded)
- **research/feature-gates.md** - Decoded gate catalog
- **data/** - Raw decoded data artifacts
