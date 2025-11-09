# Statsig Hash Decoding Guide

This note captures the workflow we use to translate hashed Statsig gate/config
IDs into human-readable names and track anything that still needs decoding.

## Toolchain

| Script | Purpose | Typical command |
|--------|---------|-----------------|
| `tools/statsig_resolver.py` | Decode a single `/v1/initialize` payload (HAR or HTML dump). |
| `tools/statsig_inventory.py` | Sweep directories and aggregate decoded gates/configs into JSON. |
| `tools/hash_scanner.py` | Find quoted numeric literals ≥ 9 digits that are not yet mapped (and not in known call-sites). |

## Current Inventory

`data/statsig_inventory.json` now aggregates captures through
15 Oct 2025:

- **382** feature gates with recorded boolean outcomes (`true` / `false`).
- Dynamic configs are currently tracked per-capture; the consolidated inventory
  has no resolved config entries in the latest sweep (pending fresh decoded
  payloads that expose config metadata).

Desktop/Sidetron critical hashes resolved so far (also summarised in
`chatgpt/docs/sidetron.md`):

- `1696863369` → `has_sidekick_access`, `show_nux_banner`.
- `1697140512` → `can_download_sidetron`, `show_nux_banner`.
- `4250072504` → `is_enterprise_enabled`, `is_enterprise_desktop_enabled`, `is_desktop_enterprise_enabled`.
- `3637408529` → anon/desktop UX toggles including `is_desktop_primary_auth_button_on_right`.
- `312855442` / `4093727931` → Trending widgets (`enable_chatgpt_trending`, `num_desktop_results`).
- `3533083032` / `4031588851` → Homepage/autocomplete experiments (`chatgpt_anon_heading_enabled`, `enable_new_homepage_anon`, …).

## Outstanding Hashes

`chatgpt/docs/unmatched_hashes.json` now tracks **237** numeric strings not yet
covered by the inventory. Most fall into benign categories (timestamps, VAT
placeholders, Datadog trace IDs). Only four are tied to Statsig helpers and
need fresh payloads to decode:

| Literal | Call site | Notes |
|---------|-----------|-------|
| `1057463568` | `checkGate("1057463568")` | Selects `/my/recent/v2/image_gen` vs legacy image history endpoint. |
| `2137702454` | `ae(…, "2137702454")` | Fetches `max_words` limit (paired with `Ka`, below). |
| `3656028793` | `Ka(…, "3656028793").get("max_words", 4)` | Companion to `2137702454`. |
| `3274829134` | `Qe(…, "3274829134")` | SSE keep-alive/logging guard. |

Regenerate the inventory once new HARs surface these IDs—the resolver will then
attach readable names automatically.

### Opt-in instrumentation

Recent bundle refreshes expose Statsig-backed telemetry for the audio paragen
preview flow:

- `chatgpt_audio_paragen_opt_in_shown`
- `chatgpt_audio_paragen_opt_in_accepted`
- `chatgpt_audio_paragen_opt_in_actively_declined`

These events fire alongside gate checks for the audio assistant preview and
capture whether users opt in, accept, or actively dismiss the preview dialog.
See `analysis/deobf/hnw079jsdm76umup/deobfuscated.js` for the emitting
call-sites in the Statsig logging helpers.

## Workflow

1. **Decode single payloads** with `tools/statsig_resolver.py` to inspect unfamiliar
   captures quickly.
2. **Update the master inventory** whenever new data sources are added
   (`tools/statsig_inventory.py`).
3. **Run the hash scanner** to verify that no new hashed strings remain
   unresolved; triage anything that isn’t a timestamp, placeholder, or known
   helper.
4. **Document impact** (e.g., update `chatgpt/docs/sidetron.md`) whenever a new
   hash maps to functionality we care about.

_Last updated: 2025-10-15._
