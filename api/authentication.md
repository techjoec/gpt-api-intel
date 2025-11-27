# Authentication & Session Management

**Source**: HAR captures, network analysis, localStorage inspection (October-November 2025)

---

## Authentication Flow

### OAuth 2.0 Flow

| Endpoint | Purpose |
|----------|---------|
| `https://auth.openai.com/oauth/authorize` | OAuth authorization endpoint |
| `https://auth.openai.com/oauth/token` | Token exchange endpoint |

### Session Endpoints

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/api/auth/session` | GET | 200 | Primary auth document with `user{id, name, email, image}`, `accessToken` (JWT), `expires`, and identity provider metadata |
| `/backend-api/sentinel/chat-requirements` | POST | 200 | Returns session tokens used as headers downstream (body structure varies) |
| `/backend-api/sentinel/frame.html` | GET | 200 | HTML asset used during sentinel challenges |
| `/backend-api/sentinel/sdk.js` | GET | 200 | Sentinel JavaScript bundle (used client-side) |
| `/backend-api/edge` | GET | 204 | Connectivity probe, empty response body |

---

## Request Headers

### Required Headers (Authenticated Requests)

```
Authorization: Bearer {access_token}
ChatGPT-Account-Id: {account_uuid}
Accept: application/json
Content-Type: application/json
```

### Additional Headers (Device Metadata)

```
User-Agent: {client_string}
Oai-Device-Id: {device_uuid}
Oai-Language: en-US
```

---

## Session State Management

### Cookies

| Cookie | Purpose |
|--------|---------|
| `oai-chat-backend` | Backend routing cookie (can toggle between preview/production hosts) |
| Session cookies | Maintain authenticated session state |

### Local Storage Keys - Anonymous Sessions

| Key | Purpose |
|-----|---------|
| `oai/apps/isNoAuthChatTrainingEnabled` | Server-driven flag enabling data retention for logged-out sessions |
| `oai/apps/noAuthRateLimitState` | JSON blob with soft/hard limit counters used to throttle anonymous usage |
| `oai/apps/noAuthUserMessageCount` | Simple counter incremented per message while logged out |
| `oai/apps/noAuthBannerDisclaimerClientThreadId` | Stores which temporary thread acknowledged the disclaimer banner |
| `oai/apps/noAuthHasAcceptedFooterDisclaimer` | Boolean preventing re-show of the anonymous-mode footer disclaimer |
| `oai/apps/noAuthHasDismissedSoftRateLimitModal` | Blocks soft rate-limit modal repeat in no-auth state |
| `oai/apps/noAuthHasSeenGpt4oModal` | Records whether GPT-4o upsell modal appeared for anonymous users |
| `oai/apps/noAuthMadlibsModalState` | Tracks state (`seen`, etc.) of the Madlibs onboarding modal |
| `oai/apps/noAuthGoUpsellModalDismissed` | Prevents reopening the "Go" upsell modal |
| `oai/apps/hasSeenNoAuthImagegenNux` | Flags the no-auth image generation onboarding as complete |

### Local Storage Keys - Authenticated Sessions

| Key | Purpose |
|-----|---------|
| `oai/apps/loggedInUserMessageCount` | Equivalent counter for authenticated users (telemetry / nudges) |
| `oai/apps/restoreMessageAfterOauthRedirect` | Stores pending user input across OAuth login redirects |

---

## Account Capability Checks

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/accounts/check/v4-2023-04-27` | GET | 200 | Account capability flags; redact identifiers before reuse |
| `/backend-api/accounts/data_usage_for_training` | GET | 200 | Privacy opt-in/opt-out status for training usage; response is account-specific |
| `/backend-api/accounts/{account_uuid}/settings` | GET | 401 | Protected resource; requires matching account headers |
| `/backend-api/compliance` | GET | 200 | Compliance envelope describing cookie consent, age gating, terms acceptance flags for the current account |
| `/backend-api/subscriptions?account_id={account_uuid}` | GET | 200 | Subscription metadata (plan, renewal status). Payload is account-specific |
| `/wham/accounts/check` | GET | 200 | WHAM capability check (rich account payload with features, entitlements) |

---

## Multi-Factor Authentication (MFA)

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/accounts/mfa_info` | GET | 200 | Lists configured MFA factors (SMS, TOTP, passkeys) |
| `/backend-api/accounts/mfa_push_auth_devices` | GET | 200 | Enumerates devices registered for MFA push notifications |

---

## Rate Limiting

### Anonymous User Rate Limits

Managed via `oai/apps/noAuthRateLimitState` localStorage key containing:
```json
{
  "soft_limit": {
    "count": number,
    "reset_at": timestamp
  },
  "hard_limit": {
    "count": number,
    "reset_at": timestamp
  }
}
```

### Authenticated User Rate Limits

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/public-api/conversation_limit` | GET | 200 | GPT-4 usage quota (`limit`, `remaining`, `reset_interval_minutes`) |
| `/backend-api/conversation/init` | GET | 200 | Seeds conversation limits (`limits_progress`, etc.). Treat payload as session-scoped |
| `/backend-api/wham/tasks/rate_limit` | GET | 200 | WHAM task quotas with `allowed`, `limit`, `remaining`, `resets_after`, `user_plan_type`, `windows[]` |

---

## WebSocket Session Bootstrap

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/celsius/ws/user` | GET | 200 | Returns `{websocket_url}` for session bootstrap. Sample: `examples/celsius_user-websocket.json` |

WebSocket URL format:
```
wss://chatgpt.com/backend-api/celsius/ws?token={session_token}
```

---

## Security Notes

- **JWT Tokens**: Access tokens are JWTs with expiration times
- **Token Rotation**: Tokens expire and must be refreshed
- **Sentinel Challenges**: Anti-bot measures via `/backend-api/sentinel/*` endpoints
- **Device Fingerprinting**: `Oai-Device-Id` header tracks devices
- **CORS Protection**: Strict origin policies enforced
- **Session Isolation**: Anonymous and authenticated sessions strictly separated

---

## Error Responses

| Status | Meaning |
|--------|---------|
| 401 | Unauthorized - missing or invalid token |
| 403 | Forbidden - valid token but insufficient permissions |
| 429 | Too Many Requests - rate limit exceeded |
| 500 | Internal Server Error |

Rate limit responses include retry-after information in headers and body.
