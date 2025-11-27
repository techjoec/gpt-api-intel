# ChatGPT & Codex REST API Documentation

Reverse-engineered HTTP/REST API documentation for ChatGPT and ChatGPT Codex (WHAM API).

**Source**: Network analysis, HAR captures, JavaScript deobfuscation (September-November 2025)

---

## API Endpoints

| Documentation | Endpoints | Description |
|---------------|-----------|-------------|
| [chatgpt-endpoints.md](api/chatgpt-endpoints.md) | 153+ | ChatGPT REST API (conversations, gizmos, automations, connectors, F/Conversation streaming) |
| [codex-wham-endpoints.md](api/codex-wham-endpoints.md) | 65+ | ChatGPT Codex / WHAM API (tasks, environments, GitHub integration, speculative turns) |
| [authentication.md](api/authentication.md) | — | OAuth flow, session management, rate limiting |

---

## HTTP Patterns

| Documentation | Description |
|---------------|-------------|
| [bundle-loading.md](http/bundle-loading.md) | JavaScript bundle loading, CDN caching, lazy loading (11 bundles, 60+ lazy chunks) |
| [server-components.md](http/server-components.md) | React Server Components (RSC) streaming, binary payload format |
| [realtime-channels.md](http/realtime-channels.md) | WebSocket event bus, SSE streaming, FannyPack indexing |
| [obfuscation.md](http/obfuscation.md) | JavaScript obfuscation patterns, base64 encoding, 4,732 artifacts analyzed |
| [client-storage.md](http/client-storage.md) | localStorage, IndexedDB, cookies, 257+ storage keys |

---

## Supporting Materials

| Directory | Contents |
|-----------|----------|
| `schemas/` | 45 JSON schemas for API request/response validation |
| `examples/` | 37 sanitized API response examples |
| `data/` | Raw research data (174KB Statsig inventory, 87KB decoded strings, 46KB obfuscation artifacts) |
| `research/` | Feature gates (26+), hash resolutions (996+), connectors (22+), SDK internals |
| `tools/` | Python analysis scripts (hash scanner, obfuscation scanner, Statsig inventory builder) |

---

## Quick Start

**Find an endpoint**: Check [chatgpt-endpoints.md](api/chatgpt-endpoints.md) or [codex-wham-endpoints.md](api/codex-wham-endpoints.md)
**Understand auth**: Read [authentication.md](api/authentication.md)
**See examples**: Browse `examples/` directory
**Validate payloads**: Use schemas in `schemas/` directory

---

## Legal Notice

**Research Purpose**: This documentation describes publicly observable HTTP behaviors of web applications. No circumvention of security measures, unauthorized access, or proprietary code disclosure.

**Not Included**: No credentials, tokens, session IDs, user data, or security vulnerabilities. All examples sanitized.

**Not Affiliated**: Independent research. Not affiliated with, endorsed by, or connected to OpenAI.

**Your Responsibility**: Users must comply with applicable laws and terms of service.

---

**License**: MIT
