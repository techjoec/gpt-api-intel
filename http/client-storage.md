# Client-Side Storage Patterns

**Source**: localStorage inspection, IndexedDB analysis, Cookie analysis (October-November 2025)

---

## localStorage Keys

### Anonymous Session State

| Key | Purpose |
|-----|---------|
| `oai/apps/isNoAuthChatTrainingEnabled` | Server-driven flag enabling data retention for logged-out sessions |
| `oai/apps/noAuthRateLimitState` | JSON blob with soft/hard limit counters for throttling anonymous usage |
| `oai/apps/noAuthUserMessageCount` | Counter incremented per message while logged out |
| `oai/apps/noAuthBannerDisclaimerClientThreadId` | Stores which temporary thread acknowledged disclaimer banner |
| `oai/apps/noAuthHasAcceptedFooterDisclaimer` | Boolean preventing re-show of anonymous-mode footer disclaimer |
| `oai/apps/noAuthHasDismissedSoftRateLimitModal` | Blocks soft rate-limit modal repeat in no-auth state |
| `oai/apps/noAuthHasSeenGpt4oModal` | Records whether GPT-4o upsell modal appeared for anonymous users |
| `oai/apps/noAuthMadlibsModalState` | Tracks state (`seen`, etc.) of the Madlibs onboarding modal |
| `oai/apps/noAuthGoUpsellModalDismissed` | Prevents reopening the "Go" upsell modal |
| `oai/apps/hasSeenNoAuthImagegenNux` | Flags the no-auth image generation onboarding as complete |

### Authenticated Session State

| Key | Purpose |
|-----|---------|
| `oai/apps/loggedInUserMessageCount` | Counter for authenticated users (telemetry / nudges) |
| `oai/apps/restoreMessageAfterOauthRedirect` | Stores pending user input across OAuth login redirects |

### Codex / WHAM Environment State

| Key | Purpose |
|-----|---------|
| `oai/apps/l1239dk1/a3f4b29d` | Last Codex environment ID opened |
| `oai/apps/l1239dk1/c7e2d18f` | Draft prompt text in the Codex composer |
| `oai/apps/l1239dk1/8fa94c1e` | Cached proposed tasks returned by WHAM |
| `oai/apps/l1239dk1/3e2d18f` | Enables React Query devtools overlay for debugging |
| `oai/apps/l1239dk1/49292001` | Manual override for rate-limit diagnostics |
| `oai/apps/l1239dk1/4b7d9e2f` | Timestamp of the last WHAM changelog view |
| `oai/apps/l1239dk1/9182cd99` | Telemetry list of repository download durations |
| `oai/apps/l1239dk1/4b9f42ce` | Map of repo ID → last used branch |
| `oai/apps/l1239dk1/a7c41ef0` | Map of repo ID → list of recently used branches |
| `oai/apps/l1239dk1/109b6e28` | "Best-of-N" preference when generating task proposals |
| `oai/apps/l1239dk1/4kdf92l2` | Serialized screenshot data captured during tasks |
| `oai/apps/l1239dk1/7a8d45ff` | Toggle to show full diffs instead of summaries |
| `oai/apps/l1239dk1/e2b7ab3c` | Preferred diff editor layout (split/unified) |
| `oai/apps/l1239dk1/codexOnboardingState` | Onboarding progression for the code agent |
| `oai/apps/l1239dk1/codexOnboardingStateOverride` | Manual override used for dev/testing |
| `oai/apps/l1239dk1/7f2c4aa2` | Last repository ID opened in Codex |
| `oai/apps/l1239dk1/showDevOnboardingOverrides` | Enables developer onboarding overrides |
| `oai/apps/tasksHasSeenProjectDisclaimerBanner` | Prevents showing the project disclaimer banner again |

### Feature Onboarding & Upsells

Pattern: `oai/apps/hasSeen*` keys

Examples:
- `oai/apps/hasSeenTatertotUpsell`
- `oai/apps/hasSeenProjectsMigrationBanner`
- `oai/apps/hasSeenConnectorOnboarding`
- `oai/apps/hasSeenCanvasIntro`

**Total**: 67+ `hasSeen*` keys documented

---

## IndexedDB Databases

### FannyPack Conversation Indexing

**Database**: `ConversationsDatabase`

**Purpose**: Local conversation search and indexing

**Schema**:
```
conversations:
  - id: string (conversation_id)
  - title: string
  - messages: array[{text, timestamp}]
  - updated_at: timestamp
  - account_id: string
```

**Lifecycle**:
- Created when `enable_local_indexing` Statsig flag is true
- Cleared when account changes
- Updated on `conversation-turn-complete` WebSocket events

**HTTP Integration**:
- No HTTP sync - purely local
- WebSocket events trigger writes
- Search results never leave browser

---

## Cookies

### Session Cookies

| Cookie | Purpose | Domain |
|--------|---------|--------|
| Session cookies | Maintain authenticated session state | `.chatgpt.com` |
| `oai-chat-backend` | Backend routing cookie (preview vs production) | `.chatgpt.com` |

### Backend Switching

Gate `2067628123` enables preview backend switcher:

**Cookie Value**:
```
oai-chat-backend=preview.chatgpt.com
```

**Effect**: Routes API requests to preview environment instead of production.

---

## sessionStorage

### Temporary State

sessionStorage used for:
- Current conversation context
- Scroll position restoration
- Modal state (dismissed during session)
- WebSocket reconnection tokens

**Cleared**: On tab/window close

---

## HTTP Caching (Browser Cache)

### Bundle Caching

```
Cache-Control: public, max-age=31536000, immutable
```

**Stored**:
- JavaScript bundles (`*.js`)
- CSS stylesheets (`*.css`)
- Static assets (images, fonts)

**Size**: ~50-200MB typical cache size

---

## Service Worker

ChatGPT does NOT use Service Worker for offline capabilities.

**Reason**: All features require server-side processing (AI inference).

---

## Storage Quota Management

### Browser Limits

| Storage | Typical Limit |
|---------|--------------|
| localStorage | 5-10MB |
| IndexedDB | 50MB - 2GB (varies by browser) |
| Total Storage | Unlimited (prompts user) |

### Quota Handling

**IndexedDB**:
```javascript
navigator.storage.estimate().then(quota => {
  console.log(`Using ${quota.usage} of ${quota.quota} bytes`);
});
```

**localStorage**:
```javascript
try {
  localStorage.setItem(key, value);
} catch (QuotaExceededError) {
  // Clear old entries, retry
}
```

---

## Data Persistence Patterns

### Write-Through Cache

**Pattern**: Write to HTTP API + localStorage simultaneously

```javascript
// Save user setting
await fetch('/backend-api/settings/user', {
  method: 'PATCH',
  body: JSON.stringify({git_diff_mode: 'unified'})
});
localStorage.setItem('oai/apps/l1239dk1/e2b7ab3c', 'unified');
```

**Benefit**: Immediate UI update, eventual consistency

### Read-Through Cache

**Pattern**: Read from localStorage first, fall back to HTTP

```javascript
let settings = localStorage.getItem('oai/apps/settings');
if (!settings) {
  settings = await fetch('/backend-api/settings/user');
  localStorage.setItem('oai/apps/settings', JSON.stringify(settings));
}
```

---

## Security Considerations

### Sensitive Data in localStorage

❌ **NOT stored**:
- Access tokens (use cookies with httpOnly flag)
- Passwords
- Credit card data
- API keys

✅ **Stored**:
- UI preferences
- Onboarding state
- Draft messages
- Rate limit counters

### XSS Protection

All localStorage writes sanitized:

```javascript
// Sanitize before write
const sanitized = DOMPurify.sanitize(userInput);
localStorage.setItem(key, sanitized);
```

### Cross-Origin Isolation

localStorage scoped to:
- Protocol: `https`
- Domain: `chatgpt.com`
- Port: `443`

Cannot be accessed by:
- `http://chatgpt.com` (different protocol)
- `https://api.chatgpt.com` (different domain)
- Any third-party sites

---

## Storage Cleanup

### Automatic Cleanup

**Triggers**:
- Account change: Clears all `oai/apps/l1239dk1/*` keys
- Logout: Clears all authenticated session state
- Version mismatch: Clears cached settings if schema changes

**Pattern**:
```javascript
// Clear on account change
window.addEventListener('accountChange', () => {
  Object.keys(localStorage)
    .filter(key => key.startsWith('oai/apps/l1239dk1/'))
    .forEach(key => localStorage.removeItem(key));
});
```

---

## HTTP Integration

### Storage → HTTP Sync

**One-way sync**: localStorage changes trigger HTTP PATCH requests

```javascript
// Example: Codex settings sync
function saveSettings(settings) {
  // 1. Update localStorage immediately (optimistic)
  localStorage.setItem('oai/apps/l1239dk1/settings', JSON.stringify(settings));

  // 2. Sync to server
  fetch('/backend-api/wham/settings/user', {
    method: 'PATCH',
    body: JSON.stringify(settings)
  }).catch(err => {
    // Rollback on failure
    localStorage.removeItem('oai/apps/l1239dk1/settings');
  });
}
```

### HTTP → Storage Sync

**WebSocket events trigger storage updates**:

```javascript
// FannyPack indexing
websocket.on('conversation-turn-complete', async (event) => {
  const db = await openDB('ConversationsDatabase');
  await db.put('conversations', {
    id: event.conversation_id,
    title: event.title,
    updated_at: Date.now()
  });
});
```

---

## Related Documentation

- **api/authentication.md** - Session management and auth state
- **realtime-channels.md** - WebSocket events triggering storage updates
- **obfuscation.md** - Base64-encoded localStorage keys
- **bundle-loading.md** - Lazy loading based on cached state
