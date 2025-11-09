# ChatGPT Connector Integration Architecture

> **Purpose**: Document ChatGPT's third-party connector system including OAuth flows, API endpoints, feature gates, and integration patterns
> **Source**: HAR captures + bundle analysis (October 2025)
> **Last Updated**: November 2025

---

## Overview

ChatGPT's connector system enables third-party integrations for Google Drive, GitHub, Notion, SharePoint, and other services. The architecture consists of:

- **Connector Catalog**: 22+ available connectors with OAuth/API key authentication
- **Link Management**: OAuth token storage and connection lifecycle
- **Feature Gates**: Granular rollout control per connector type
- **API Layer**: `/aip/connectors/*` and `/ca/v2/*` endpoint families
- **UI Integration**: Onboarding flows, permission requests, usage tracking

**Total Connectors**: 22 catalog entries (as of October 2025)
**Active OAuth Scopes**: GitHub (repo, PR access), Google Drive (read-only)
**Gate-Controlled Connectors**: Box, Google Calendar, MCP, Google Drive, SharePoint/OneDrive

---

## Connector Catalog

### Available Connectors

The `/aip/connectors/list_accessible` endpoint returns the full catalog:

| Connector | Type | Auth Methods | Primary Use Case |
|-----------|------|--------------|------------------|
| **GitHub** | Code hosting | OAuth (repo, PR scopes) | Repository access, PR review |
| **Google Drive** | File storage | OAuth (read-only) | Document access, file search |
| **Google Calendar** | Calendar | OAuth | Event access, scheduling |
| **Notion** | Knowledge base | OAuth | Database queries, page access |
| **Box** | File storage | OAuth | Enterprise file access |
| **SharePoint** | Document management | OAuth | Enterprise document access |
| **OneDrive** | File storage | OAuth (personal + business) | File access, search |
| **MCP** | Model Context Protocol | API integration | Custom tool integration |
| *[14+ additional connectors]* | Various | OAuth/API key | Various integrations |

**Catalog Response Shape**:
```json
{
  "items": [
    {
      "id": "string",
      "domain": "string",
      "namespace": "string",
      "name": "string",
      "description": "string",
      "auth_type": "oauth|api_key|none",
      "supported_auth_flows": ["string"],
      "action_schemas": [{...}]
    }
  ]
}
```

---

## Feature Gates

### Connector Allowlist Gate

**Hash**: `733205176`
**HAR Frequency**: 21 crossrefs
**Function**: Third-party connector access control

**Allowed Connectors** (when gate enabled):
- `box` - Box integration
- `google_calendar` - Google Calendar
- `mcp` - Model Context Protocol

**Category**: `connector/connector_admin`

**Purpose**: Controls which connectors are available to users based on plan tier, experiment enrollment, or enterprise policy.

---

### Google Drive Rollout Gates

**Hash**: `51772912` + `108590566`
**HAR Frequency**: 18 crossrefs

**Feature Flags**:
- `gdrivePercentage` - Rollout percentage (gradual rollout control)
- `o365Link` - Office 365 integration toggle
- `loadTestPercentage` - Load testing control
- `loaderData` - Data loader configuration

**Category**: `connector/model`

**Purpose**: Gradual rollout of Google Drive connector with A/B testing support.

---

### SharePoint/OneDrive UX Refresh

**Hash**: `3206655705`

**Feature Flags**:
- `enable_new_ux` - New connector UI experience
- `web_enable_for_existing_users` - Migration flag for existing users

**Purpose**: Refreshed SharePoint/OneDrive connector experience with improved UI.

---

## API Endpoints

### Connector Management

**List Accessible Connectors**:
```
GET /aip/connectors/list_accessible
```
Returns catalog of all available connectors with auth requirements and action schemas.

**List Active Links**:
```
GET /aip/connectors/links/list_accessible
```
Returns OAuth links currently authorized by user.

**Example Response**:
```json
{
  "links": [
    {
      "connector_id": "github",
      "link_id": "string",
      "status": "active|pending|revoked",
      "scopes": ["repo", "read:user", "write:discussion"],
      "created_at": "timestamp",
      "last_used": "timestamp"
    }
  ]
}
```

---

### Connection Status

**Check Status**:
```
GET /ca/v2/user/connection_status
```
Returns active connector instances.

**Example Response**:
```json
{
  "connections": [
    {
      "id": "ks--github-{random_id}",
      "connector": "github",
      "status": "active",
      "user_configuration_count": 5
    }
  ]
}
```

**User Configuration**:
```
GET /ca/v2/user_configuration
```
Returns detailed configuration for each connector (e.g., synced GitHub repos).

**Connector Readiness Check**:
```
GET /connectors/check?connector_type={type}
```
Advertises connector readiness flags (e.g., OneDrive personal/business link availability).

---

### GitHub Integration

**Active Scopes**:
- `repo` - Full repository access
- `read:user` - User profile reading
- `write:discussion` - Discussion participation
- Additional PR/code review scopes

**Configuration**:
- Up to 5 repositories can be synced
- Tracks last sync time per repository
- Supports PR review workflows

**Events Emitted**:
- `connector_github_linked` - OAuth flow completion
- `connector_github_sync_started` - Repository sync initiated
- `connector_github_sync_completed` - Sync finished

---

### Google Drive Integration

**Current State** (as of October 2025):
- Read-only OAuth scope
- Gradual rollout via `gdrivePercentage` gate
- Integration with Office 365 via `o365Link` flag

**Readiness Check**:
```
GET /connectors/check?connector_type=gdrive
Response: { "enabled": false, "reason": "percentage_rollout" }
```

---

### SharePoint/OneDrive Integration

**Link Types**:
- **OneDrive Personal**: Consumer accounts
- **OneDrive Business**: Enterprise/work accounts
- **SharePoint**: Site-level access

**Readiness Status**:
```
GET /connectors/check?connector_type=onedrive_personal
Response: { "link_enabled": true }

GET /connectors/check?connector_type=onedrive_business
Response: { "link_enabled": true }
```

**UX Refresh**:
- `enable_new_ux` flag controls modern UI
- `web_enable_for_existing_users` manages migration
- Improved file picker and permission flows

---

## OAuth Flow Architecture

### Standard OAuth Flow

**Step 1: Initiation**
```
POST /aip/connectors/oauth/initiate
{
  "connector_id": "github",
  "redirect_uri": "https://chatgpt.com/aip/oauth/callback"
}

Response:
{
  "authorization_url": "https://github.com/login/oauth/authorize?...",
  "state": "random_state_token"
}
```

**Step 2: Callback Handling**
```
GET /aip/oauth/callback?code={auth_code}&state={state}
```
Server exchanges code for access token, stores securely.

**Step 3: Link Activation**
```
GET /aip/connectors/links/list_accessible
```
Confirms link is now active.

---

### Scope Management

**GitHub Example Scopes**:
```json
{
  "scopes": [
    "repo",           // Full repository access
    "read:user",      // User profile
    "write:discussion" // Discussions
  ]
}
```

**Google Drive Example Scopes**:
```json
{
  "scopes": [
    "https://www.googleapis.com/auth/drive.readonly"
  ]
}
```

---

## Onboarding & Settings

### User Settings Integration

Connector states stored in `/backend-api/settings/user`:

```json
{
  "connector_onboarding_completed": {
    "github": true,
    "google_drive": false
  },
  "connector_preferences": {
    "github": {
      "auto_sync": true,
      "sync_interval_hours": 24
    }
  }
}
```

### Base64 Token System

**Token Pattern**: `oai/apps/connectors/{connector_id}/{state}`

**Tracked States**:
- `hasSeenConnectorOnboarding_{connector_id}`
- `hasCompletedConnectorAuth_{connector_id}`
- `hasUsedConnector_{connector_id}`

**Storage**: `localStorage` via `ve(Ce.hasSeen...)` pattern

---

## Statsig Integration

### Event Tracking

**Connector-Related Events** (from `hnw079jsdm76umup` bundle):

| Event Name | Trigger | Payload |
|------------|---------|---------|
| `connector_oauth_initiated` | OAuth flow start | `{ connector_id, timestamp }` |
| `connector_oauth_completed` | OAuth success | `{ connector_id, scopes, timestamp }` |
| `connector_oauth_failed` | OAuth failure | `{ connector_id, error, timestamp }` |
| `connector_sync_started` | Data sync start | `{ connector_id, resource_count }` |
| `connector_sync_completed` | Sync finish | `{ connector_id, duration_ms, items_synced }` |
| `connector_usage` | Connector used in conversation | `{ connector_id, action_type }` |

**Telemetry Integration**: All events logged via `V.addFeatureFlagEvaluation` when gate `4011688770` enabled.

---

## UI Integration Points

### Sidebar Entry

**Gate Check Pattern**:
```javascript
// Simplified from bundle analysis
const showConnector = he(i, "733205176") &&
                      connectorAllowlist.includes(connectorId);
```

**Rendering**:
- Connector icons in sidebar
- Badge for new/unlinked connectors
- Status indicators (linked/unlinked/error)

---

### Settings Panel

**Location**: Settings → Connectors

**Features**:
- List of available connectors
- OAuth link/unlink buttons
- Configuration per connector (repos, folders, etc.)
- Usage statistics
- Permission review

---

### Conversation Context

**Usage Pattern**:
```
User: "Show me my latest PRs on GitHub"
System: [Checks connector_status → uses GitHub link → queries API → responds]
```

**Permission Prompts**:
- First-time use triggers consent modal
- Shows requested scopes
- Allows selective permission grants

---

## Connector Action Schemas

### Example: GitHub Connector

**Action Schema**:
```json
{
  "actions": [
    {
      "id": "list_repositories",
      "name": "List Repositories",
      "description": "Get user's accessible repositories",
      "parameters": {
        "type": "object",
        "properties": {
          "visibility": { "type": "string", "enum": ["all", "public", "private"] }
        }
      }
    },
    {
      "id": "get_pull_requests",
      "name": "Get Pull Requests",
      "description": "Fetch PRs for a repository",
      "parameters": {
        "type": "object",
        "properties": {
          "repo": { "type": "string", "required": true },
          "state": { "type": "string", "enum": ["open", "closed", "all"] }
        }
      }
    }
  ]
}
```

---

### Example: Google Drive Connector

**Action Schema**:
```json
{
  "actions": [
    {
      "id": "search_files",
      "name": "Search Files",
      "description": "Search for files and folders",
      "parameters": {
        "type": "object",
        "properties": {
          "query": { "type": "string", "required": true },
          "mime_type": { "type": "string" }
        }
      }
    },
    {
      "id": "read_file",
      "name": "Read File",
      "description": "Read file contents",
      "parameters": {
        "type": "object",
        "properties": {
          "file_id": { "type": "string", "required": true }
        }
      }
    }
  ]
}
```

---

## Error Handling

### Common Error Responses

**OAuth Errors**:
```json
{
  "error": "oauth_failed",
  "message": "User denied authorization",
  "connector_id": "github",
  "retry_available": true
}
```

**API Errors**:
```json
{
  "error": "connector_api_error",
  "message": "Rate limit exceeded",
  "connector_id": "github",
  "retry_after_seconds": 3600
}
```

**Link Errors**:
```json
{
  "error": "link_expired",
  "message": "OAuth token expired, reauthorization required",
  "connector_id": "google_drive",
  "reauth_url": "/aip/connectors/oauth/initiate?connector_id=google_drive"
}
```

---

### Error Normalization

Uses `RequestError` class from `dmck639k4dv7claj` bundle:
- Distinguishes `client` vs `server` errors
- Preserves raw error for debugging
- Sanitizes URLs before logging
- Feeds into Datadog telemetry

---

## Security & Privacy

### Token Storage

- OAuth tokens stored server-side only
- Never exposed to client JavaScript
- Encrypted at rest
- Automatic rotation for long-lived tokens

### Scope Minimization

**Principle**: Request minimum scopes needed

**Examples**:
- Google Drive: Read-only (no write access)
- GitHub: Specific repo access (not org-wide)

### Revocation

**User-Initiated**:
```
DELETE /aip/connectors/links/{link_id}
```
Revokes OAuth token and clears stored data.

**Automatic Revocation**:
- Token expiration (if refresh unavailable)
- User account deletion
- Security incident response

---

## Rate Limiting

### Connector-Specific Limits

**GitHub**:
- 5000 API calls/hour (authenticated)
- Cached for 5 minutes per query

**Google Drive**:
- 1000 queries/user/100 seconds
- Cached for 15 minutes

**Handling**:
- `429 Too Many Requests` → queue retry
- Exponential backoff
- User notification after 3 retries

---

## Analytics & Monitoring

### Usage Metrics

**Tracked Metrics**:
- OAuth flow completion rate
- Connector activation rate
- Average time to first use
- Daily active connectors
- Error rate by connector type

**Statsig Experiments**:
- A/B test new connector UX flows
- Measure impact of permission scope changes
- Optimize onboarding conversion

---

### Telemetry Pipeline

**Flow**:
```
User Action → Connector Event → Statsig Log → Datadog → Analytics Dashboard
```

**Enrichment**:
- Plan type (Free/Plus/Pro)
- Connector gate status
- Experiment enrollment
- Geographic region

---

## Model Context Protocol (MCP)

### Special Integration

**MCP Connector** enables custom tool integration:

**Authentication**: API key-based

**Action Schema**:
```json
{
  "actions": [
    {
      "id": "call_tool",
      "name": "Call MCP Tool",
      "description": "Execute custom MCP tool",
      "parameters": {
        "type": "object",
        "properties": {
          "tool_name": { "type": "string", "required": true },
          "arguments": { "type": "object" }
        }
      }
    }
  ]
}
```

**Use Cases**:
- Custom API integrations
- Internal tool access
- Specialized workflows

**Gate**: Controlled via `733205176` allowlist

---

## Future Connectors

### Observed in Bundle Analysis

**Potential Upcoming Connectors** (referenced in code):
- Slack (workspace integration)
- Jira (issue tracking)
- Confluence (documentation)
- Salesforce (CRM)
- Additional Microsoft 365 services

**Evidence**: Gate hashes and translation strings exist but not yet activated.

---

## Integration Patterns

### Pattern 1: File Access

**Flow**:
1. User mentions file by name
2. System checks for active file storage connector
3. Queries connector API for file
4. Retrieves file content
5. Processes in conversation context

**Connectors**: Google Drive, OneDrive, Box, SharePoint

---

### Pattern 2: Code Repository Access

**Flow**:
1. User asks about code/PRs
2. System checks GitHub/GitLab connector
3. Queries repository API
4. Analyzes code/diffs
5. Responds with insights

**Connectors**: GitHub, GitLab (future)

---

### Pattern 3: Calendar Integration

**Flow**:
1. User asks about schedule
2. System checks Google Calendar connector
3. Queries events API
4. Returns relevant events
5. Offers scheduling assistance

**Connectors**: Google Calendar, Outlook (future)

---

## Development Guidelines

### Adding New Connectors

**Requirements**:
1. Action schema definition
2. OAuth 2.0 implementation (or API key support)
3. Feature gate configuration
4. Onboarding flow design
5. Error handling patterns
6. Telemetry integration
7. Documentation

### Testing Checklist

- [ ] OAuth flow (happy path)
- [ ] OAuth failures (denial, timeout, invalid state)
- [ ] Token refresh handling
- [ ] API error responses
- [ ] Rate limit handling
- [ ] Link revocation
- [ ] Multi-account support
- [ ] Cross-browser compatibility
- [ ] Mobile responsiveness

---

## Related Documentation

- **[Feature Gate Catalog](research/gate_catalog.md)** - Connector-specific gates
- **[Hash Resolution Catalog](research/hash_resolution_catalog.md)** - Complete hash mappings
- **[Bundle Architecture](../architecture/bundle_architecture.md)** - Connector UI bundle loading

---

## Maintenance

**Last API Capture**: October 2025
**Active Connectors**: 22 catalog entries
**Documented Integrations**: GitHub, Google Drive, SharePoint/OneDrive complete
**Completeness**: Core patterns documented, additional connectors require HAR captures

**Known Gaps**:
- Notion connector action schemas (not captured)
- Box connector implementation details
- Slack/Jira connectors (referenced but not activated)
- MCP custom tool examples

---

**Note**: This documentation reflects the connector architecture as of October 2025. New connectors may be added, OAuth flows may change, and feature gates may rotate. Use this as a reference for understanding integration patterns and API contracts.
