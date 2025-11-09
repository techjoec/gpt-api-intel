# ChatGPT Feature Gate Catalog

> **Purpose**: Comprehensive catalog of discovered feature gates in ChatGPT's web application
> **Source**: Extracted from JavaScript bundle analysis (October 2025)
> **Last Updated**: October 2025

---

## Overview

ChatGPT uses numeric hash identifiers as feature gates to control functionality rollout, A/B testing, and user experience variations. This catalog documents gates discovered through systematic reverse-engineering of client-side bundles and runtime analysis.

**Total Gates Documented**: 26+ unique feature gates
**Discovery Method**: JavaScript bundle deobfuscation + HAR capture analysis
**Hash Frequency**: Based on appearance across 23+ captured sessions

---

## Core Infrastructure Gates

### Backend Switching & Preview

**Hash**: `2067628123`
**Bundle**: `hnw079jsdm76umup` (line 9226)
**Function**: Preview web / SA-server backend switcher
**Behavior**: Rewrites the `oai-chat-backend` cookie to pivot between preview and production hosts
**Use Case**: Development/staging environment access

---

### OpenTelemetry & Instrumentation

**Hash**: `4011688770`
**Bundle**: `dmck639k4dv7claj` (line 74242)
**Function**: Lazy loads OpenTelemetry bootstrap
**Behavior**:
- Dynamically loads `ieljay4ufw8jyjph.js` for OTel initialization
- Logs every gate evaluation via `V.addFeatureFlagEvaluation`
- Enables telemetry for all feature flag decisions

**Integration**: Statsig gate evaluation tracking

---

### SSR Metadata Enhancement

**Hash**: `3125419433`
**Bundle**: `dmck639k4dv7claj` (line 18351)
**Function**: Server-side rendering metadata expansion
**Behavior**:
- Enables SSR hreflang tags
- Expands Open Graph metadata
- Activates through `Sse()` flow

**Use Case**: SEO optimization, social media link previews

---

## Model & AI Features

### GPT-5 Model Preference

**Hash**: `1627380539`
**Bundle**: `dmck639k4dv7claj` (line 72099)
**Function**: Marks GPT-4o as GPT-5-preferred
**Behavior**:
- Activates model-switcher heuristics
- Enables "thinking effort" presets
- Controls GPT-4o → GPT-5 migration path

**Related Systems**: Model picker UI, preference persistence

---

### Image History Pagination

**Hash**: `1057463568`
**Bundle**: `hnw079jsdm76umup` (line 87194)
**Function**: Image history API version toggle
**Behavior**: Switches between:
- `/my/recent/image_gen` (v1)
- `/my/recent/v2/image_gen` (v2)

**Use Case**: A/B testing pagination improvements

---

## UI & UX Features

### Streaming Favicon Updates

**Hash**: `948657827`
**Bundle**: `hnw079jsdm76umup` (line 48980)
**Function**: Streaming favicon enrichment
**Behavior**:
- Issues POSTs to `${Ys}/favicons`
- Exposure logging disabled
- Real-time favicon updates during responses

---

### Canvas Image Lightbox

**Hash**: `1520205231`
**Bundle**: `k3ulfqwluwevik5m` (line 41)
**HAR Frequency**: 21 crossrefs
**Function**: Image lightbox archive/download controls
**Features**:
- "Open in Chat" button
- Archive toggle
- Download functionality

**Events Emitted**:
- `chatgpt_web_image_library_lightbox_open`
- `chatgpt_web_image_library_lightbox_archive`
- `chatgpt_web_image_library_lightbox_download`

**Validation**: Checks archive eligibility before state mutation

---

### Report Conversation Menu

**Hash**: `3376455464`
**Bundle**: `l1m3l5lbmhuctzw6` (line 267)
**Function**: "Report conversation" menu entry
**Behavior**: Unlocks menu option when thread/message is selected
**Use Case**: Content moderation, user reporting

---

### Edge-to-Edge Layout

**Hash**: `1536947154`
**Bundle**: `dmck639k4dv7claj` (line 100241)
**HAR Frequency**: 23 crossrefs (highest)
**Function**: Edge-to-edge layout propagation
**Behavior**: Enables responsive layout adjustments in RSC shell
**Integration**: React Server Components architecture

---

### ProseMirror Content Cleaning

**Hash**: `223382091`
**Bundle**: `dmck639k4dv7claj` (line 45487)
**Function**: Content reference node insertion
**Behavior**:
- Exported as `yLe`
- Cleans ProseMirror content references
- Inserts `contentReference` nodes safely

**Use Case**: Rich text editor state management

---

## Projects & Sora

### Sora Sidebar Entry

**Hash**: `317829697`
**Experiment**: `1792765184.sidebar_enabled`
**Bundle**: `hnw079jsdm76umup` (line 76224)
**Function**: Sora sidebar visibility control
**Logic**:
- Enterprise: Bypasses gate (always visible)
- Free seats: Must satisfy BOTH gate AND Statsig enrollment

**Integration**: Sidebar navigation, Sora feature access

---

### Projects NUX Tooltips

**Hash**: `2711769261`
**Bundle**: `oasstlv4rvegny2a` (line 615)
**HAR Frequency**: 23 crossrefs
**Function**: Projects migration NUX flow
**Features**:
- Tooltip cadence control
- Badge display logic
- Projects → Free migration messaging

**Related Tokens**: `oai/apps/hasSeenProjects*` family

---

### Projects Production Toggles

**Hash**: `3768341700`
**HAR Frequency**: 22 crossrefs
**Function**: Projects prompt carousel and upsell control
**Feature Flags**:
- `is_produce_design`
- `is_produce_text`
- `is_produce_text_design`
- `remove_early_access_upsell`

**Categories**: `tatertot/projects/banner`

---

## Tatertot Upsell System

Tatertot is ChatGPT's in-context upsell and education system. Multiple gates control banner display, messaging, and conversion flows.

### Core Tatertot Controller

**Hash**: `1092897457`
**Function**: Tatertot system enablement
**Feature Flags**:
- `is_tatertot_enabled`
- `in_context_upsell_custom_prompt_enabled`
- Plus trial banners
- Team trial banners

**Use Case**: Education banner eligibility, trial promotions

---

### Upsell Banner Management

**Hash**: `1368081792`
**Function**: Dynamic upsell banner control
**Feature Flags**:
- `should_show_deep_research_upsell_banner`
- `should_show_o3_mini_upsell_banner`
- `should_change_model_picker`

**Integration**: Model picker UI modifications

---

### Codex Upsell Integration

**Hash**: `1586944302`
**Rule**: `6Y59g2W4iWZnRxhyTNJwCP`
**Function**: Codex-specific upsell scheduling
**Category**: `tatertot` (rule-only, no plaintext flags yet)

---

### Connector & Banner Admin

**Hash**: `1738106734` + `3861158060`
**Function**: Additional banner state control
**Feature Flags**:
- Codex upsell banners
- Connector admin switches (`ca_*`)
- Banner visibility toggles

---

### Capability Suggestions

**Hash**: `28816792`
**Rule**: `3fMwbmFRAIv8Gi0Ymw0Vqu:100.00:1`
**Function**: Tatertot capability suggestion prompts
**Integration**: Autoprompt system

---

## Connectors & Integrations

### Connector Allowlist

**Hash**: `733205176`
**HAR Frequency**: 21 crossrefs
**Function**: Third-party connector access control
**Allowed Connectors**:
- `box` (Box integration)
- `google_calendar` (Google Calendar)
- `mcp` (Model Context Protocol)

**Categories**: `connector/connector_admin`

---

### Google Drive Rollout

**Hash**: `51772912` + `108590566`
**HAR Frequency**: 18 crossrefs
**Function**: Google Drive feature rollout control
**Feature Flags**:
- `gdrivePercentage` - Rollout percentage
- `o365Link` - Office 365 integration
- `loadTestPercentage` - Load testing control
- `loaderData` - Data loader configuration

**Categories**: `connector/model`

---

### SharePoint/OneDrive UX

**Hash**: `3206655705`
**Function**: SharePoint and OneDrive connector refresh
**Feature Flags**:
- `enable_new_ux` - New connector UI
- `web_enable_for_existing_users` - Migration flag for existing users

**Integration**: Refreshed connector experience

---

## Checkout & Monetization

### Custom Checkout Gates

**Hash**: `3950229590`
**HAR Frequency**: 19 crossrefs
**Function**: Checkout flow customization
**Feature Flags**:
- `enable_mobile_app_upsell_banner`
- `enable_moodeng_upsell_banner`
- `enabled_custom_checkout_for_plus`
- `enabled_custom_checkout_for_pro`

**Categories**: `tatertot/checkout/banner`

---

### Model & Plan Availability

**Hash**: `2304807207`
**Function**: Model and plan feature gates
**Feature Flags**:
- `default_interval` - Subscription interval defaults
- `image_gen` - Image generation availability
- `o1_pro` - O1 Pro model access
- `o3_pro` - O3 Pro model access

**Categories**: Model & checkout gates

---

## Experimental & System

### Request Ledger

**Hash**: `1154002920`
**Bundle**: `dmck639k4dv7claj` (line 96050)
**Function**: Completion request tracking
**Behavior**:
- Retains last 10 completion timings
- Stores completion IDs
- Exported as `PIe`

**Use Case**: Performance monitoring, request debugging

---

### Training Suppression

**Hash**: `2562876640`
**Bundle**: `dmck639k4dv7claj` (line 95963)
**Function**: First completion training hook control
**Behavior**:
- Suppresses "first completion" training hooks
- Disables associated notifications

**Use Case**: User experience personalization

---

### No-Auth Welcome Modal

**Hash**: `1803944755`
**Source**: `sse_handlers.json`
**Function**: Welcome-back modal for anonymous users
**Feature Flag**: `is_no_auth_login_modal_enabled`
**Behavior**: Shows modal before authentication
**Exported As**: `gB`

---

## Contextual Prompts & Autoprompt

### Tools With Label Catalog

**Hash**: `16480203`
**HAR Frequency**: 20 crossrefs
**Function**: Contextual prompt catalog
**Prompt Examples**:
- "Can you create an image for my website? I need something that matches the overall theme and tone."
- "Can you create an image of my pet? I'd love to have a fun and creative representation."
- "Can you summarize the notes from my meeting? If you need more information, ask me a follow up question or ask me to upload a file or image."

**Categories**: `connector/tatertot/projects/checkout/banner/image`
**Integration**: Contextual Answers, Autoprompt experiences

---

## High-Frequency Rule-Only Gates

These gates appear in 20+ captured sessions but have no plaintext feature flag names yet. They are identified only by Statsig rule IDs:

| Hash | Crossrefs | Rule ID | Status |
|------|-----------|---------|--------|
| `879591222` | 23 | `34Jh1rbDZAXR35pvqAZK59:100.00:1` | Rule-only |
| `3492040717` | 22 | `3RJSdztPLwjW69f4hyIj7M:100.00:1` | Rule-only |
| `3536244140` | 21 | `5RBE3v1N1VpZgghEesstC2:100.00:1` | Rule-only |
| `3651421897` | 22 | `3GYoFAa0FRoEk1z8Rl6XCq:100.00:1` | Rule-only |
| `2007094101` | 21 | (no plaintext) | Rule-only |
| `3485296344` | 21 | (no plaintext) | Rule-only |

**Note**: These may control foundational infrastructure or experiments not yet publicly named.

---

## Gate Evaluation Architecture

### Statsig Integration

ChatGPT uses Statsig for feature flag evaluation. The `cs7toih8jegb7teq` bundle provides core infrastructure:

**Key Components**:
- `_getStatsigGlobal` - Global Statsig instance accessor
- `_getStatsigGlobalFlag` - Flag evaluation helper
- `StatsigMetadataProvider` - Context provider for metadata
- `StatsigSession` - Session state management
- `StatsigUser` - User identity handling

**Safety Mechanisms**:
- `no-encode` safeguards prevent encoding issues
- SDK key validation when multiple clients register
- Multi-instance warning system

**Event Emission**:
- 182+ named events in `hnw079jsdm76umup`
- 51+ events in `dmck639k4dv7claj`
- Covers: Tatertot NUX, Golden Hour, connectors, contextual answers

---

## Base64 Token System

**Total Tokens**: 257 discovered
**Prefix Pattern**: 120 begin with `oai/apps/`
**HasSeen Pattern**: 67 contain `hasSeen*` tracking

**Token Families**:
- **Tatertot**: `hasSeenTatertot*` - NUX and quiz completions
- **Projects**: `hasSeenProjects*` - Migration flow tracking
- **Connectors**: Connector onboarding states
- **Moonshine**: Memory experiment tracking
- **PromoRedemption**: Promotion redemption flags
- **Canvas**: `hasSeenCanvasCodeExecution*` - Confirmation dialogs

**Integration**: Local storage persistence via `ve(Ce.hasSeen…)` lookups

---

## Discovery Methodology

### Data Sources

1. **JavaScript Bundle Analysis**:
   - Deobfuscated bundles: `hnw079jsdm76umup`, `dmck639k4dv7claj`, `cs7toih8jegb7teq`, `k3ulfqwluwevik5m`, `l1m3l5lbmhuctzw6`, `oasstlv4rvegny2a`
   - Extracted: gate maps, experiment maps, function maps, Statsig events

2. **HTTP Archive Captures**:
   - 23+ HAR files analyzed
   - Hash frequency tracking
   - Cross-session correlation

3. **React Server Component Payloads**:
   - RSC pointer resolution
   - Hash-to-feature mappings
   - Runtime configuration analysis

### Crossref Interpretation

- **23 crossrefs**: Core functionality (edge-to-edge layout, Projects NUX)
- **21-22 crossrefs**: Major features (connectors, Canvas controls, Tatertot)
- **16-20 crossrefs**: Common features with user/plan dependencies
- **<16 crossrefs**: Experimental or conditional features

---

## Usage Notes

### For Developers

**Gate Evaluation Pattern**:
```javascript
// Typical gate check pattern found in bundles
he(i, "gate_hash_id") // Returns boolean

// With Statsig integration
Z(W, "statsig_rule_id") // Evaluates rule
```

**Event Logging**:
```javascript
V.addFeatureFlagEvaluation(gate_id, value) // OTel logging
```

### For Researchers

**Identifying New Gates**:
1. Deobfuscate latest bundles
2. Search for `he(i, "` patterns
3. Cross-reference with HAR captures
4. Check RSC payloads for hash pointers
5. Correlate with Statsig event logs

**Tracking Changes**:
- Monitor bundle hash rotations
- Diff `oai/apps/*` token additions
- Track `StatsigMetadataProvider` payload changes
- Compare gate evaluation logs across versions

---

## Related Documentation

- **[Hash Resolution Catalog](./hash_resolution_catalog.md)** - Complete 996-entry hash mapping
- **[Amphora Overview](../architecture/amphora_overview.md)** - Amphora lock system
- **[RSC Overview](../architecture/rsc_overview.md)** - React Server Components architecture
- **[Statsig Decoding](./statsig_decoding.md)** - Feature flag decoding techniques

---

## Maintenance

**Last Bundle Analysis**: October 2025
**Bundles Analyzed**: 6 primary bundles
**HAR Captures**: 23+ sessions
**Completeness**: 26+ gates documented (estimated 50-70% of discoverable gates)

**Known Gaps**:
- 68+ hashes appear in ≥10 HARs without plaintext mappings
- Rule-only gates require further RSC pointer resolution
- Enterprise-specific gates may not be captured

---

**Note**: This catalog represents a point-in-time analysis. ChatGPT's feature gates are continuously evolving. Hash IDs may rotate, features may be promoted to stable, and new experiments may be added. Use this as a reference for understanding the platform's architecture and experimentation patterns.
