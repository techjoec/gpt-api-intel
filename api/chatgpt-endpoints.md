# ChatGPT REST API Endpoints

**Source**: HAR captures, network analysis (October-November 2025)
**Total Documented**: 153+ endpoints

---

## Authentication & Session

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/api/auth/session` | GET | 200 | Primary auth document with `user{id, name, email, image}`, `accessToken` (JWT), `expires`, and identity provider metadata |
| `/backend-api/sentinel/chat-requirements` | POST | 200 | Returns session tokens used as headers downstream (body structure varies) |
| `/backend-api/sentinel/frame.html` | GET | 200 | HTML asset used during sentinel challenges |
| `/backend-api/sentinel/sdk.js` | GET | 200 | Sentinel JavaScript bundle (used client-side) |
| `/backend-api/edge` | GET | 204 | Connectivity probe, empty response body |

### Anonymous & Auth Flow Keys

These localStorage entries manage rate limits, disclaimers, and state transitions for anonymous (no-auth) sessions as well as OAuth redirects.

| Constant | Key | Notes |
|----------|-----|-------|
| `t.IsNoAuthChatTrainingEnabled` | `oai/apps/isNoAuthChatTrainingEnabled` | Server-driven flag enabling data retention for logged-out sessions |
| `t.NoAuthRateLimitState` | `oai/apps/noAuthRateLimitState` | JSON blob with soft/hard limit counters used to throttle anonymous usage |
| `t.NoAuthUserMessageCount` | `oai/apps/noAuthUserMessageCount` | Simple counter incremented per message while logged out |
| `t.LoggedInUserMessageCount` | `oai/apps/loggedInUserMessageCount` | Equivalent counter for authenticated users (telemetry / nudges) |
| `t.NoAuthBannerDisclaimerClientThreadId` | `oai/apps/noAuthBannerDisclaimerClientThreadId` | Stores which temporary thread acknowledged the disclaimer banner |
| `t.NoAuthHasAcceptedFooterDisclaimer` | `oai/apps/noAuthHasAcceptedFooterDisclaimer` | Boolean preventing re-show of the anonymous-mode footer disclaimer |
| `t.NoAuthHasDismissedSoftRateLimitModal` | `oai/apps/noAuthHasDismissedSoftRateLimitModal` | Blocks soft rate-limit modal repeat in no-auth state |
| `t.NoAuthHasSeenGpt4oModal` | `oai/apps/noAuthHasSeenGpt4oModal` | Records whether GPT-4o upsell modal appeared for anonymous users |
| `t.NoAuthMadlibsModalState` | `oai/apps/noAuthMadlibsModalState` | Tracks state (`seen`, etc.) of the Madlibs onboarding modal |
| `t.NoAuthGoUpsellModalDismissed` | `oai/apps/noAuthGoUpsellModalDismissed` | Prevents reopening the "Go" upsell modal |
| `t.HasSeenNoAuthImagegenNux` | `oai/apps/hasSeenNoAuthImagegenNux` | Flags the no-auth image generation onboarding as complete |
| `t.RestoreMessageAfterOauthRedirect` | `oai/apps/restoreMessageAfterOauthRedirect` | Stores pending user input across OAuth login redirects |

---

## Account & User Management

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/accounts/check/v4-2023-04-27` | GET | 200 | Account capability flags; redact identifiers before reuse |
| `/backend-api/accounts/data_usage_for_training` | GET | 200 | Privacy opt-in/opt-out status for training usage; response is account-specific |
| `/backend-api/accounts/{account_uuid}/settings` | GET | 401 | Protected resource; requires matching account headers |
| `/backend-api/accounts/mfa_info` | GET | 200 | Lists configured MFA factors (SMS, TOTP, passkeys) |
| `/backend-api/accounts/mfa_push_auth_devices` | GET | 200 | Enumerates devices registered for MFA push notifications |
| `/backend-api/settings/user` | GET | 200 | Returns account settings (`announcements`, `settings`, `permissions`). Includes `settings.sunshine`, `settings.moonshine`, `calpico_who_can_message_me` privacy toggle, and model defaults (`last_used_model_config` with `gpt-5-pro` + `gpt-5-thinking` juice) |
| `/backend-api/settings/user_last_used_model_config?model_slug=gpt-5-thinking` | GET | 200 | Confirms persisted model slug/effort; repeated PATCH/GET cycles observed for changing `thinking_effort` |
| `/backend-api/compliance` | GET | 200 | Compliance envelope describing cookie consent, age gating, terms acceptance flags for the current account |
| `/backend-api/subscriptions?account_id={account_uuid}` | GET | 200 | Subscription metadata (plan, renewal status). Payload is account-specific |
| `/backend-api/checkout_pricing_config/configs/USD` | GET | 200 | Pricing catalog for checkout flows (currency-specific) |
| `/backend-api/shopping/orders` | GET | 200 | Order history for storefront purchases; contains PII, keep internal |

---

## Conversations & Messaging

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/conversation` | POST | 401 | Conversation creation/continuation (requires auth) |
| `/backend-api/conversation/init` | GET | 200 | Seeds conversation limits (`limits_progress`, etc.). Treat payload as session-scoped |
| `/backend-api/conversation/{id}/async-status` | POST | 200 | Poll async task state for long-running operations (`status`, `progress`, `message`) |
| `/backend-api/conversation/{id}/stream_status` | GET | 200 | Check if conversation has active streaming connection (`streaming`, `model`, `started_at`) |
| `/backend-api/conversation/{id}/textdocs` | GET | 200 | Retrieve document attachments from conversation |
| `/backend-api/conversation/experimental/generate_autocompletions` | POST | 200 | Generate message suggestions based on context (`conversation_id`, `message_id`, `num_suggestions`) |
| `/backend-api/conversations` | GET | 200 | Paginated conversation list (`offset`, `limit`, `is_archived`, `is_starred`). Sanitise IDs before sharing |
| `/backend-anon/conversation` | POST | 401 | Anonymous conversation endpoint |
| `/backend-anon/share` | POST | 500 | Anonymous share endpoint |
| `/backend-api/share` | POST | 500 | Authenticated share endpoint |
| `/public-api/conversation` | GET | 404 | Public conversation endpoint (not found) |
| `/public-api/share` | GET | 404 | Public share endpoint (not found) |
| `/public-api/conversation_limit` | GET | 200 | GPT-4 usage quota (`limit`, `remaining`, `reset_interval_minutes`) |

---

## Fast Conversation Streaming (F/Conversation)

High-performance streaming conversation API with enhanced event types and feature-based rate limiting.

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/f/conversation/prepare` | POST | 200 | Pre-flight conversation setup with `conversation_id`, `model`, `parent_message_id` |
| `/backend-api/f/conversation` | POST | SSE | High-performance streaming conversation endpoint with delta encoding and resume tokens |

### Headers

Requires `ChatGPT-Account-Id` header alongside Bearer token:

```
Authorization: Bearer {access_token}
ChatGPT-Account-Id: {account_id}
```

### SSE Event Types

| Event Type | Description |
|------------|-------------|
| `delta_encoding` | Protocol version marker |
| `delta` | Incremental message state changes |
| `resume_conversation_token` | Session continuation JWT |
| `conversation_async_status` | Async task progress |
| `server_ste_metadata` | Conduit state, warmup status, model slug |
| `conversation_detail_metadata` | Feature quotas with reset times |
| `message_stream_complete` | End-of-message marker |
| `[DONE]` | Stream terminator |

### Feature-Based Rate Limiting

The `conversation_detail_metadata` event includes `limits_progress` array tracking feature quotas:

```json
{
  "type": "conversation_detail_metadata",
  "limits_progress": [
    {
      "feature": "deep_research",
      "remaining": 15,
      "total": 20,
      "reset_at": "2025-12-01T00:00:00Z"
    },
    {
      "feature": "odyssey",
      "remaining": 48,
      "total": 50,
      "reset_at": "2025-12-01T00:00:00Z"
    }
  ]
}
```

**Features:**
- `deep_research` - Deep Research queries
- `odyssey` - Extended reasoning sessions

---

## Gizmos (Custom GPTs)

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/gizmos/bootstrap` | GET | 200 | Bootstrap data for user gizmos (body contains personalised content; treat as sensitive) |
| `/backend-api/gizmos/snorlax/sidebar?conversations_per_gizmo=5&owned_only=true` | GET | 200 | Sidebar feed for owned gizmos; payload includes conversation snippets |
| `/backend-api/gizmos/g-p-{hash}` | GET | 200 | Individual gizmo bootstrap (e.g., `g-p-68af9464…`); bodies contain personalised conversations |
| `/backend-api/gizmo_creator_profile` | GET | 200 | Custom GPT creator metadata (`creator_id`, `display_name`, `profile_url`, `social_links`) |

---

## Memories & Personalization

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/memories?include_memory_entries=false` | GET | 200 | Memory metadata envelope (entries omitted when parameter is false) |
| `/backend-api/personality_types` | GET | 200 | Returns trait metadata powering Custom Instructions personality pills |
| `/backend-api/user_system_message_trait_pills` | GET | 200 | Returns trait pill catalog for persona selection UI |
| `/backend-api/user_system_messages` | GET | 200 | Returns system instructions visible to the client (contains personalised content) |

---

## Automations & Tasks

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/agent_automations` | GET | 200 | Lists automation definitions tied to the current account |
| `/backend-api/automations?filter={paused\|scheduled\|finished}` | GET | 200 | Query specific automation states; responses mirror `agent_automations` shape per filter |
| `/backend-api/tasks` | GET | 200 | Task metadata (non-WHAM); treat payload as experimental |

---

## Images & Media

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/images/bootstrap` | GET | 200 | Image generation configuration; review locally before sharing |

---

## Connectors & Integrations

### AIP Connectors

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/aip/connectors/github/has_installations` | POST | 200 | Boolean indicator describing GitHub installation availability |
| `/backend-api/aip/connectors/github/search_repos` | POST | 200 | GitHub repository search (body omitted/redacted; treat as sensitive) |
| `/backend-api/aip/connectors/links/list_accessible` | POST | 200 | Lists connectors actually linked to workspace. See `examples/aip_connectors-links-list-accessible.json` |

### Connection API

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/ca/v2/user/connection_instance/{connector_id}/user_configuration` | GET | 200 | Connector configuration (sanitise IDs/secrets) |
| `/backend-api/ca/v2/user/connection_status` | GET | 200 | Connector availability summary (e.g., GitHub connection) |
| `/backend-api/client_applications` | GET | 200 | Returns first-party application metadata (app IDs, scopes); sensitive, redact tokens |

### Connector Checks

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/connectors/check?connector_names=gdrive&connector_names=o365_personal&connector_names=o365_business` | GET | 200 | Connector readiness check; response enumerates accessible services |

---

## WebSocket & Realtime

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/celsius/ws/user` | GET | 200 | Returns `{websocket_url}` for session bootstrap. See `examples/celsius_user-websocket.json` |

---

## Notifications & UI

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/notifications/settings` | GET | 200 | Notification preference flags; redact addresses before sharing |
| `/backend-api/system_hints` | GET | 200 | Server-provided hint bundle; structure is volatile |
| `/backend-api/user_surveys/active` | GET | 200 | Active survey metadata (if any) |
| `/backend-api/client/strings` | GET | 200 | UI localization strings (e.g., `deep_research.title`, `caterpillar.description`) |

---

## Experimentation & Feature Flags

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/v1/initialize` | GET | 200 | (Desktop client) – Returns the Statsig bootstrap payload |
| `/backend-api/user_is_in_search_holdout_with_web_disabled` | GET | 200 | Boolean flag for search holdout experiments |

---

## Analytics & Telemetry

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/v1/rgstr` | POST | 202 | Posts Segment-style telemetry envelope `{metadata, events[], stats}`; server replies `{accepted:true}` |
| `/ces/v1/i` | POST | 202 | Trio of customer-engagement pings carrying session metadata (`auth_state`, locale, browser, Segment tokens) |
| `/messenger/web/ping` | GET | 200 | Intercom bootstrap event confirming chat widget availability |
| `/backend-api/lat/r` | POST | 202 | Latency telemetry with token timing breakdown (`request_id`, `ttft`, `total_time`, `token_times`, `model`) |

---

## File Operations

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/files/download/{file_id}` | GET | 200 | Download conversation file attachment (returns binary content) |
| `/backend-api/estuary/content` | GET | 200 | CDN-delivered file content with signature verification (`file_id`, `signature`, `expires` query params) |

---

## Notes

- All endpoints use HTTP/2
- Most endpoints require `Authorization: Bearer {token}` header
- Session management handled via cookies + JWT tokens
- Examples sanitized to remove credentials, tokens, session IDs, and personal information
- Full request/response examples available in `examples/` directory
- JSON schemas available in `schemas/` directory
