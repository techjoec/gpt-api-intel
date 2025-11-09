# ChatGPT Hash Pointer Resolution Catalog

> **Purpose**: Reference catalog mapping obfuscated hash identifiers to their functionality
> **Source**: Extracted from reverse-engineering ChatGPT's client-side code (October 2025)
> **Use Case**: Understanding feature flags, gates, and internal identifiers

---

## Overview

ChatGPT's web application uses numeric hash identifiers to reference features, experiments, and configuration values. This catalog documents the mappings discovered through systematic analysis of:
- React Server Component (RSC) payloads
- HTTP Archive (HAR) captures
- JavaScript bundle analysis
- Statsig feature gate evaluations

**Total Mappings**: 996 unique hash identifiers
**Crossref Range**: 23 (highest frequency) to 0 (single occurrence)
**Source Data**: Aggregated from `analysis/intel/hash_pointer_full.json`

---

## High-Frequency Hashes (20+ Crossrefs)

These hashes appear most frequently across captured sessions, indicating core functionality:

| Hash ID | Crossrefs | Resolved Values | Categories |
|---------|-----------|----------------|------------|
| `879591222` | 23 | `1qfecgTGhI41TyPRCHP0cj` | - |
| `1536947154` | 23 | `rule=14TSzLrZM8HTspnFJDo0dg:100.00:1` | Statsig rule |
| `2711769261` | 23 | `2yyPpKFkcyShFLdyBksHG6` | Projects NUX tooltips |
| `3768341700` | 22 | `is_produce_design`, `is_produce_text`, `is_produce_text_design` | tatertot/projects/banner |
| `733205176` | 21 | `box`, `google_calendar`, `mcp` | connector/connector_admin |
| `1520205231` | 21 | `01rYN29WNc33FVGlTeqiAb` | Canvas image lightbox |
| `16480203` | 20 | Contextual prompts: "Can you create an image...", "Help me learn Python..." | connector/tatertot/projects |

### Feature Gate Clusters

**Tatertot Banner System** (in-context upsells):
- `1092897457` - `is_tatertot_enabled`, trial banners, custom prompt upsells
- `1368081792` - Deep research/o3-mini upsell banners, model picker changes
- `1586944302` - Codex upsell integration
- `1738106734` - Connector admin switches
- `3861158060` - Additional banner controls
- `28816792` - Rule-based gating

**Connector Architecture**:
- `733205176` - Connector allowlist (`box`, `google_calendar`, `mcp`)
- `51772912` - Google Drive percentage rollout, load test controls
- `108590566` - Additional connector controls
- `3206655705` - SharePoint/OneDrive + new UX enablement

**Model & Checkout Gates**:
- `2304807207` - `default_interval`, `image_gen`, `o1_pro`, `o3_pro`
- `3950229590` - Mobile app upsell, custom checkout for Plus/Pro

---

## Complete Hash Catalog

### Format
```
Hash ID (Crossrefs: N) → Resolved Values ; Categories
```

Where:
- **Hash ID**: Numeric identifier found in code
- **Crossrefs**: Number of HAR captures containing this hash
- **Resolved Values**: Plaintext strings, feature flags, or experiment names
- **Categories**: Classification tags (tatertot, connector, model, etc.)
- **no_plaintext**: Hash found but no plaintext mapping yet (rule-only)

---

### A-G (Hashes 0-999999999)

`16480203` (20) → `5Jlrd9pFV0UhGDfWGHkhQO`; Contextual prompts catalog ; categories:connector/tatertot/projects/checkout/banner/image

`28816792` (18) → `rule=3fMwbmFRAIv8Gi0Ymw0Vqu:100.00:1`

`46455729` (16) → no_plaintext

`51772912` (18) → `7Clvb0QOWPUx3qCVJyHAEf`; `gdrivePercentage`; `loadTestPercentage`; `loaderData` ; categories:connector/model

`108590566` (16) → `7Clvb0QOWPUx3qCVJyHAEf`

`156153730` (16) → `rule=796hV3C1QluuOjarZFV38U:0.00:1`

`174366048` (20) → `rule=bhPM7FsN2H1vnBUrxrg6v:100.00:3`

`218915747` (16) → no_plaintext

`222560275` (19) → `rule=5pv2QpbgXNDB0QnBo3LTti:100.00:2`

`223382091` (16) → `1fKkxDiVebEKfTj8nDAjHe`

`232791851` (16) → no_plaintext

`294957382` (16) → `rule=2emhZXyf2pgPHaRJS4mO3O:100.00:1`

`296452287` (17) → `rule=4qrPR4YgnMDXGxt5PaOi2C:0.00:1`

`317829697` (16) → `rule=598ORr5O5ZardhhzMhz8k0:100.00:15` ; Sora sidebar experiment

`369193424` (17) → `rule=598ORr5O5ZardhhzMhz8k0:100.00:15`

`392240685` (16) → `rule=5GxJyyvuXiX6JrRFmDz5TK:100.00:2`

`402391964` (16) → `14sAQaGJDosUKVV0DFZsAL`

`417039829` (16) → `14sAQaGJDosUKVV0DFZsAL`

`422449809` (18) → `rule=6UXSkSjZSEzqA7fq1pvVZN:100.00:1`

`471233253` (16) → `rule=6UXSkSjZSEzqA7fq1pvVZN:100.00:1`

`491279851` (16) → `rule=4qtiGNNqqVtvmya19HUPfJ:100.00:1` ; Projects/Snorlax route guard

`537200474` (21) → `rule=267h9QJDQxrNtH1xDKNWKR:100.00:1`

`547652119` (18) → `rule=muV45DjtwM1FqEVQdfU48:0.00:7`

`550432558` (16) → no_plaintext

`550560761` (19) → `P`; `history_results_limit`; `is_experiment_active`; `is_user_in_experiment`

`555198838` (16) → no_plaintext

`571174949` (16) → `rule=4kfyoZAXBVLtFe22ng71gq:0.00:2`

`614413305` (16) → `4dJRDSQ21TM2T9VfKwgErx`

`616577762` (16) → no_plaintext

`638971034` (19) → `5Wveq7GtTwSkw53xGh43IJ`

`645560164` (17) → `rule=6N7KWRPlr8htwuCTM1PK8P:100.00:2`

`667937038` (17) → `rule=6N7KWRPlr8htwuCTM1PK8P:100.00:2`

`713974087` (16) → no_plaintext

`727502549` (16) → no_plaintext

`733205176` (21) → `box`; `google_calendar`; `mcp` ; categories:connector/connector_admin

`735368229` (20) → `Tgpx2sWrjJFvrIQz5i2Rj`

`766296922` (20) → `5M80Kzz2tbfdgNONyvZ4yt`; `Tgpx2sWrjJFvrIQz5i2Rj`

`773249106` (21) → `5M80Kzz2tbfdgNONyvZ4yt` ; Projects conversation feed gate

`785520609` (16) → `rule=3Pv3bKbjUQIOMSDClknPPU:0.00:6`

`878458344` (16) → `1qfecgTGhI41TyPRCHP0cj`

`879591222` (23) → `1qfecgTGhI41TyPRCHP0cj`

`891514942` (16) → `rule=aWUpA0S5LOLglPP8MnSVz:100.00:1`

`926440545` (16) → `6cpOntJWaY0PM6KienOpud`

`934056609` (18) → `6cpOntJWaY0PM6KienOpud`

`989108178` (16) → `4sTodKrNyByM4guZ68MORR`

---

### H-M (Hashes 1000000000-2999999999)

`1032814809` (18) → `rule=3ekBeOhgTARIWsbWFLXXlV:100.00:1`

`1057463568` (crossrefs: varies) → Image history API v1/v2 pagination toggle

`1062277569` (16) → `71N4Jo1hoAkC2AgdDXKOKk` ; categories:model

`1092897457` (crossrefs: varies) → `is_tatertot_enabled`, `in_context_upsell_custom_prompt_enabled`, Plus/Team trial banners ; categories:tatertot/banner

`1138231213` (16) → `6vS0XLwzY0ev70A0LFGhbx`

`1154002920` (16) → no_plaintext

`1213809372` (18) → no_plaintext

`1214379119` (16) → `rule=3Da3vJtBawdpcHFOEpjzZA:10.00:2`

`1242184140` (16) → no_plaintext

`1281927149` (16) → `rule=BpeZLya4EhDVcnP7pLcih:1.00:5`

`1318146997` (16) → `rule=2AclmEgqaQBVFbxz37XKzy:100.00:5`

`1320400016` (16) → `rule=2AclmEgqaQBVFbxz37XKzy:100.00:5`

`1327278438` (16) → `37b90Pe22hQ4v4zxzvfsMd`

`1368081792` (crossrefs: varies) → Deep research/o3-mini upsell banners, model picker changes ; categories:tatertot/banner

`1382475798` (18) → `1gTx2Aj2GOaFnX0i5QH3xd`; `3P8OsGy1e5tQlR5dsTIWbL`

`1406552515` (19) → `rule=2YraErHICnArWRGDHJEJ32:0.00:1`

`1416952492` (16) → `rule=4cUAiUhaPmuDSuw2J4Wwmn:0.00:2`

`1422501431` (20) → `2FWfMqWUtJiyC5zXj1kE4j`

`1520205231` (21) → `01rYN29WNc33FVGlTeqiAb` ; Canvas image lightbox controls (21 HAR hits)

`1535847699` (17) → `rule=44UValrDnL3ZLP6DR6Ecke:100.00:2`

`1536947154` (23) → `rule=14TSzLrZM8HTspnFJDo0dg:100.00:1`

`1542198993` (17) → `rule=14TSzLrZM8HTspnFJDo0dg:100.00:1`

`1586944302` (18) → `6Y59g2W4iWZnRxhyTNJwCP` ; Codex upsell banners ; categories:tatertot

`1596731578` (20) → `rule=1G5t40VS8MrQBuGt3M9yNB:100.00:5`

`1611573287` (16) → `rule=159rwM3sBnviE9XWH24azn:100.00:2`

`1627380539` (19) → `XpQQXUL1hnJL24lgK6SNc` ; GPT-4o → GPT-5 preference logic

`1738106734` (crossrefs: varies) → Connector admin switches ; categories:tatertot

`1741586789` (20) → `4bd3o553p0ZCRkFmipROd8`

`1759425419` (20) → no_plaintext

`1825130190` (17) → `Nef2uMceNUF9U3ZYwSbpD`

`1854238036` (16) → `rule=7lT39hCYz9WrYPvJfQFhiU:100.00:2`

`1860647109` (20) → `is_continue_enabled`; `is_direct_continue_enabled`

`1887864177` (16) → `4aG4TMZXICKolzZX4PHocN`

`1894790777` (16) → `440aNijkk3to2aY5qzAuce`; `4aG4TMZXICKolzZX4PHocN`; `HqUecdZnSS5dtVzQybG0p`

`1900515849` (17) → `440aNijkk3to2aY5qzAuce`

`1909635392` (18) → no_plaintext

`2007094101` (21) → no_plaintext

`2067628123` (crossrefs: varies) → Preview backend switcher (cookie manipulation)

`2134057841` (19) → no_plaintext

`2179180337` (21) → `USeZCOloSU02kTe6xjZuA`; `default_attempts`; `is_experiment_active`; `is_user_in_experiment`

`2273762597` (19) → `7kaMWWoUxPT50SeIPlfCdh`; `Football`; `additional_category`; `enable_additional_categories` ; categories:connector

`2304807207` (crossrefs: varies) → `default_interval`, `image_gen`, `o1_pro`, `o3_pro` ; Model & checkout gates

`2398649844` (20) → `Show Fullscreen`; `is_experiment_active`; `is_user_in_experiment`; `prestart`

`2494348560` (17) → Android keyboard layout, connector admin ; categories:connector_admin

`2665240312` (19) → `2yyPpKFkcyShFLdyBksHG6`

`2711769261` (23) → `2yyPpKFkcyShFLdyBksHG6` ; Projects NUX tooltips

---

### N-Z (Hashes 3000000000-4294967295)

`3148583717` (20) → `2LMhhyBFNuqee6FxNBPYGD`

`3154019201` (19) → `rule=1fdDzhKkmiNG08p0dIBjd7:100.00:1`

`3206655705` (crossrefs: varies) → SharePoint/OneDrive, `enable_new_ux`, `web_enable_for_existing_users` ; categories:connector

`3376455464` (20) → `rule=3tYMumqGebbN1yyrefmMeI:100.00:2`

`3485296344` (21) → no_plaintext

`3492040717` (22) → `rule=3RJSdztPLwjW69f4hyIj7M:100.00:1`

`3536244140` (21) → `rule=5RBE3v1N1VpZgghEesstC2:100.00:1`

`3651421897` (22) → `rule=3GYoFAa0FRoEk1z8Rl6XCq:100.00:1`

`3678527908` (20) → `rule=2Qe7NvPSBVLx4FLp0gF0xe:100.00:2`

`3768341700` (22) → `5Jlrd9pFV0UhGDfWGHkhQO`; `is_produce_design`; `is_produce_text`; `is_produce_text_design` ; categories:tatertot/projects/banner

`3860515571` (18) → `6AHTTZOZ7zK6ZwfVd3yEGZ`

`3861158060` (crossrefs: varies) → Additional Tatertot banner controls ; categories:tatertot

`3930843960` (20) → `rule=1FrJBUMS0ziDyHPTOCwGc1:100.00:7`

`3950229590` (19) → `enable_mobile_app_upsell_banner`; `enable_moodeng_upsell_banner`; `enabled_custom_checkout_for_plus`; `enabled_custom_checkout_for_pro` ; categories:tatertot/checkout/banner

`4011688770` (crossrefs: varies) → OpenTelemetry lazy loading, gate evaluation telemetry

---

## Usage Notes

### Interpreting Hash Values

**Statsig Rules**: Patterns like `rule=XXXXX:percentage:variation`
- Format: `rule={statsig_id}:{rollout_percentage}:{variation_id}`
- Example: `rule=14TSzLrZM8HTspnFJDo0dg:100.00:1` = 100% rollout, variation 1

**Feature Flags**: Boolean or string identifiers
- Example: `is_tatertot_enabled`, `enable_mobile_app_upsell_banner`

**Experiments**: Combination of allocation + feature flags
- Example: `is_experiment_active` + `is_user_in_experiment` + specific feature name

**Plaintext Gaps**: Hashes marked `no_plaintext`
- Found in RSC payloads but no corresponding plaintext string identified
- Often rule-only gates without descriptive names

### Category Tags

- `tatertot/*` - In-context upsell and banner system
- `connector/*` - Third-party integrations (Google, Box, etc.)
- `model/*` - AI model availability and features
- `checkout/*` - Subscription and billing flows
- `projects/*` - Projects/Snorlax feature set
- `banner/*` - UI banner displays
- `connector_admin/*` - Connector management features

---

## Research Methodology

This catalog was compiled through:

1. **HAR Capture Analysis**: 23+ HTTP Archive files analyzed for feature flag references
2. **RSC Payload Decoding**: React Server Component responses decoded to extract hash pointers
3. **Cross-Referencing**: Hash IDs correlated across multiple capture sessions
4. **Statsig Instrumentation**: Feature gate evaluation telemetry parsed
5. **Bundle Analysis**: JavaScript bundle examination for hash → plaintext mappings

**Frequency Interpretation**:
- **20+ crossrefs**: Core features used across most sessions
- **10-19 crossrefs**: Common features with user/plan dependencies
- **1-9 crossrefs**: Experimental features, A/B tests, or rare configurations
- **0 crossrefs**: May indicate removed features or mapping errors

---

## Maintenance Notes

**Last Updated**: Extracted October 2025
**Source Data**: Research archives (to be archived post-publication)
**Completeness**: 996/996 hash IDs extracted (100%)

**Known Limitations**:
- Hashes may rotate with new deployments
- Some `no_plaintext` entries remain unresolved
- Crossref counts are session-dependent and may not reflect global usage

---

**Note**: This catalog represents a point-in-time snapshot of ChatGPT's internal feature gating system. Hash values and mappings may change as the platform evolves. The catalog is provided for research and debugging purposes to help understand ChatGPT's architecture and feature deployment patterns.
