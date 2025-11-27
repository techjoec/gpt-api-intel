# Statsig Payload References

- `statsig_decoding.md` – walkthrough of decoding the `/v1/initialize` bootstrap payload (hashed gate IDs → readable names).
- `data/statsig_inventory.json` – catalog of resolved Statsig gate/config IDs from captured payloads.

See also `chatgpt/docs/security/obfuscation_hits.json` for inline base64 blobs containing additional gate IDs.

## October 2025 Updates

- **Quota safeguards:** Recon triad `analysis/recon/triads/statsig-quota-triad.md` and session log `analysis/recon/sessions/2025-10-12_quota.md` document the `Statsig Keys: ${S.length}` guard and `QuotaExceededError` persistence checks.
- **Emitter coverage:** Bundle notes at `analysis/javascript/notes/bundles/cs7toih8jegb7teq.md#statsig-instrumentation` and `analysis/javascript/notes/bundles/dmck639k4dv7claj.md` list the live Statsig emitters (`setTrackingConsent`, `startSessionReplayRecording`, gate/experiment evaluations).
- **Flag registry sync:** `analysis/feature_flags/registry.md` and idea queue entries in `analysis/feature_flags/notes/idea_queue.md` map the Statsig payloads back to feature-flag tracking tasks.
- **Watch targets:** `analysis/javascript/notes/watch_list.md` tracks router hash `lxgn8k46ba24438b` and dependency `nfubiloo9rdxk3kj` for future Statsig-related rotations.
