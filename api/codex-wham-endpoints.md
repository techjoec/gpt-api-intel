# Codex / WHAM REST API Endpoints

**Source**: HAR captures, network analysis, Codex CLI reverse engineering (September-November 2025)
**Total Documented**: 65+ endpoints
**WHAM**: Web Hosted Application Management - ChatGPT Codex backend API

---

## Environment Management

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/wham/environments` | GET | 200 | Lists environments with full metadata: identifiers (`id`, `machine_id`, `label`), workspace hints (`workspace_dir`, `description`, `task_count`, `is_pinned`), execution policy (`agent_network_access`), setup knobs (`auto_setup_settings`, `cache_settings`, `setup`, `maintenance_setup`), GitHub state (`repos[]`, `repo_map{}`), and bookkeeping (`creator_id`, `created_at`, `share_settings`, `share_targets`, `secrets`, `env_vars`). See `examples/wham-examples_environments-list.json` |
| `/backend-api/wham/environments/recent` | GET | 200 | Same shape as above, filtered to recently used environments |
| `/backend-api/wham/environments/{environment_id}` | GET | 200 | Environment detail (identical shape, includes `setup`/`maintenance_setup` scripts) |
| `/backend-api/wham/environments/with-creators` | GET | 200 | Batched environment list that expands each entry with `creator` and `machine` blocks |
| `/backend-api/wham/environments/{environment_id}/with-creator-and-machine` | GET | 200 | Adds explicit `creator {id,email,name}` and `machine {label, limits}` blocks. See `examples/wham-examples_environment-with-creator.json` |
| `/backend-api/wham/environments/by-repo/{provider}/{owner}/{repository}` | GET | 200 | Resolve environment ID from repository metadata. Returns `environments[]` array with `id`, `label`, `name`, `repository_full_name`, `default_branch` |
| `/backend-api/wham/environments/{environment_id}/reset-cache` | POST | 200 | Returns `null`; triggers cache invalidation |
| `/backend-api/wham/environments/test` | POST | SSE | Initiates an environment diagnostic run by posting the full environment definition. Server replies with `text/event-stream; charset=utf-8` data while attempting to provision the requested machine. When no matching machine exists, browsers surface `net::ERR_HTTP2_PROTOCOL_ERROR` after ~12s |
| `/backend-api/wham/environments/{environment_id}` | DELETE | 204 | Removes the environment immediately |
| `/backend-api/codex/environments` | GET | 200 | Codex CLI environment list (similar structure to WHAM environments) |
| `/backend-api/codex/environments/{environment_id}/repos` | GET | 200 | Codex CLI repository list for environment |

---

## Task Management

### Task CRUD

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/wham/tasks` | POST | 200 | Accepts either a `new_task` (with `title`, `input_items[]`, `environment_id`, etc.) or `follow_up` payload; each `input_item` matches shapes defined in `schemas/cloud_task_bundle.schema.json`. Returns refreshed task bundle |
| `/backend-api/wham/tasks/list?limit=…&task_filter=current\|all\|archived` | GET | 200 | Returns summary collection with `items[]` and pagination token in `cursor`. Each summary includes `id`, `title`, `has_generated_title`, `created_at`, `updated_at`, `archived`, `has_unread_turn`, `pull_requests[]`, and `task_status_display`. See `examples/wham-examples_tasks-list.json` |
| `/backend-api/wham/tasks` | GET | 200 | Lightweight feed of recent tasks with `items[]` containing both `task` (metadata) and latest assistant `turn`. See `examples/wham-examples_tasks-response.json` |
| `/backend-api/wham/tasks/{task_id}` | GET | 200 | Provides current task bundle with `task`, `current_user_turn`, `current_assistant_turn`, and `current_diff_task_turn`. Includes `denormalized_metadata` such as `diff_stats`, `start_branch_name`, `pushed_branch_name`, `num_follow_ups`, `external_pull_requests[]`. See `examples/wham-examples_task-bundle.json` |

### Task Turns & Execution

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/wham/tasks/{task_id}/turns` | GET | 200 | Returns `turn_mapping` keyed by turn id plus `current_turn_id`. User turns expose `input_items`, `user_model_slug`, and timestamps; assistant turns include `turn_status`, `output_items[]` (messages, patches, diagnostics), `error` blocks, `branch`, `base_commit_sha`, `logs`, `worklog.messages[]`, and relationships via `previous_turn_id`, `sibling_turn_ids`, and `children[]`. See `examples/wham-examples_turn-mapping.json` |
| `/backend-api/wham/tasks/{task_id}/turns/{turn_id}` | GET | 200 | Returns single turn document mirroring structures in `turn_mapping`; useful when polling for updates. See `examples/wham-examples_task-turn-detail.json` |
| `/backend-api/wham/tasks/{task_id}/logs` | GET | 200 | Retrieve task-level execution logs for diagnostic analysis (`logs[]` with `timestamp`, `level`, `message`, `source`) |
| `/backend-api/wham/tasks/{task_id}/turns/{turn_id}/logs` | GET | 200 | Returns `logs` array for specific turn |
| `/backend-api/wham/tasks/{task_id}/turns/{turn_id}/sibling_turns` | GET | 200 | Returns `sibling_turns` array showing alternate execution branches |
| `/backend-api/wham/tasks/{task_id}/turns/{turn_id}/stream?item_type=task_turn_event&…` | POST | SSE | Opens SSE stream. Events have `{event, data}` payloads where `data` unmarshals into `{id, item_type, timestamp, payload}`. Recognized `item_type` values: `task_turn_event`, `work_log_message`, `log`, `task_title_generated` |

### Speculative Turns

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/wham/tasks/{task_id}/speculative_turns/{turn_id}` | GET | 200 | Retrieve alternative execution branch (best-of candidate) with `turn` details |
| `/backend-api/wham/tasks/{task_id}/speculative_turns/{turn_id}/view` | GET | 200 | Track view/interaction with speculative turn for analytics |

### Task Actions

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/wham/tasks/{task_id}/recover` | POST | 200 | Responds with `{"success":true}` or `null` |
| `/backend-api/wham/tasks/{task_id}/archive` | POST | 200 | Archives task |
| `/backend-api/wham/tasks/{task_id}/cancel` | POST | 200 | Cancels task execution |
| `/backend-api/wham/tasks/{task_id}/fork` | POST | 200 | Forks task to new branch |
| `/backend-api/wham/tasks/{task_id}/mark_read` | POST | 200 | Marks task as read |
| `/backend-api/wham/tasks/{task_id}/turns/{turn_id}/viewed` | POST | 200 | Marks turn as viewed |
| `/backend-api/wham/tasks/{task_id}/turns/{turn_id}/cancel` | POST | 200 | Cancels specific turn |
| `/backend-api/wham/tasks/{task_id}/turns/{turn_id}/discard` | POST | 200 | Discards turn |
| `/backend-api/wham/tasks/{task_id}/turns/{turn_id}/copy_git_apply` | POST | 200 | Copies git apply command |
| `/backend-api/wham/tasks/{task_id}/turns/{turn_id}/pr` | POST | 200 | Creates pull request from turn |
| `/backend-api/wham/tasks/{task_id}/turns/{turn_id}/undo_all_discards_for_siblings` | POST | 200 | Undoes all discards for sibling turns |

### Task Quotas

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/wham/tasks/rate_limit` | GET | 200 | Advertises current quotas with `allowed`, `limit`, `remaining`, `resets_after`, `resets_after_text`, `user_plan_type`, and `windows[]` (each includes `limit_window_mins`). See `examples/wham-examples_tasks-rate-limit.json` |

---

## GitHub Integration

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/wham/github/installations` | GET | 200 | GitHub installation roster. See `examples/wham-examples_github-installations.json` |
| `/backend-api/wham/github/installations/v2` | GET | 200 | GitHub installations v2 format. See `examples/wham-examples_github-installations-v2.json` |
| `/backend-api/wham/github/installations/events` | GET | 200 | GitHub installation events |
| `/backend-api/wham/github/installations/events/v2` | GET | 200 | Returns `installations_without_events[]`. See `examples/wham-examples_github-installations-events.json` |
| `/backend-api/wham/github/repositories/{repo_id}` | GET | 200 | Repository permissions and merge policies. See `examples/wham-examples_github-repository.json` |
| `/backend-api/wham/github/repositories/v2/{installation_id}` | GET | 200 | Enhanced GitHub repository listing with permissions (`repositories[]` with `id`, `full_name`, `default_branch`, `permissions`) |
| `/backend-api/wham/github/branches/{repo_id}/search` | GET | 200 | Returns branch names with pagination. See `examples/wham-examples_github-branches-search.json` |
| `/backend-api/wham/task_suggestions/github/user_handle` | GET | 200 | Resolves saved GitHub handle. See `examples/wham-examples_task-suggestions-github-user-handle.json` |

---

## Settings & Configuration

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/wham/settings/user` | GET | 200 | Returns `{user_id, git_diff_mode, branch_format, custom_instructions, code_review_preference, alpha_opt_in}`. See `examples/wham-examples_settings-user.json` |
| `/backend-api/wham/settings/user` | PATCH | 200 | Accepts subset of user settings keys and echoes updated document |
| `/backend-api/wham/settings/code_review` | GET | 200 | Supplies `repo_review_settings[]` plus audit metadata. See `examples/wham-examples_settings-code-review.json` |
| `/backend-api/wham/settings/configs/user-preferences` | GET | 200 | Static helper describing allowed `branch_format` substitution tokens (`{feature}`, `{uuid}`, `{repo}`, `{timestamp}`). See `examples/wham-examples_settings-config-user-preferences.json` |

---

## Machines

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/backend-api/wham/machines` | GET | 200 | List of available machine definitions (currently returns `[]` in captures). See `examples/wham-examples_machines.json` |

---

## Legacy `/wham/…` Routes

Observed via patches/logs - same semantics as `/backend-api/wham/...` but direct path (older API usage):

- `/wham/tasks` and sub-routes
- `/wham/environments`, `/wham/environments/recent`, `/wham/environments/{id}`, `/wham/environments/by-repo/...`
- `/wham/accounts/check` – Capability check (rich account payload with features, entitlements)
- `/wham/feedback` – Feedback submission (rare in captures)

---

## React Server Components (RSC) Routes

Binary payloads using `.data` extension:

| Path Pattern | Description |
|--------------|-------------|
| `/codex/settings/*.data` | Settings pages (code-review, general, environments, etc.) |
| `/codex/tasks/{task_id}.data` | Task detail page data |

Query parameter: `?_routes=routes%2Fcodex.{path}`

---

## Authentication Flow

| Endpoint | Purpose |
|----------|---------|
| `https://auth.openai.com/oauth/authorize` | OAuth authorization endpoint |
| `https://auth.openai.com/oauth/token` | Token exchange endpoint |

---

## Task Turn Output Items

### Output Item Types

**`type="message"`** entries contain `content_type` variants:
- `text` - Plain text content
- `terminal_chunk_citation` - Fields: `terminal_chunk_id`, `line_range_start`, `line_range_end`
- `repo_file_citation` - Fields: `path`, `line_range_start`, `line_range_end` (links to GitHub blobs)

**`type="partial_repo_snapshot"`** exposes:
- `files[]` with `path`, optional `contents`
- `line_range_contents[]` - Each chunk: `{line_range_start, line_range_end, content[], contains_end_of_file}`
- `missing_reason` when payloads are omitted

### Worklog Structure

Each `worklog.messages[]` entry carries:
- `channel` - `commentary`, `final`, or `null`
- `content.language` / `response_format_name` (optional)
- Extended metadata: `exclude_after_next_user_message`, `reasoning_status`, `first_content_token_index`, `message_content_token_count`, `is_initial_reasoning_message`, `error`
- Nested namespaces: e.g., `l1239dk1.inline_comments[]` for inline review anchors

### Environment Snapshots

Turn-level `environment` includes:
- `agent_network_access` with `preset_allowlist="all"`
- `auto_setup_settings`, `cache_settings` with `cache_invalidation_key`
- `setup[]`, `maintenance_setup[]` scripts
- `repo_map{}` with permission booleans (`allow_merge_commit`, `allow_rebase_merge`, etc.)
- `env_vars` with explicit toolchain pins:
  - Python 3.12
  - Node 20
  - Ruby 3.4.4
  - Rust 1.89.0
  - Go 1.24.3
  - Bun 1.2.14
  - PHP 8.4
  - Java 21
  - Swift 6.1

---

## Schema References

- **Primary schema**: `schemas/cloud_task_bundle.schema.json` - Covers `task`, `current_assistant_turn`, `turn_mapping`, and related WHAM response fields
- All environment schemas in `schemas/backend_api_wham_environments*.schema.json`
- All task schemas in `schemas/backend_api_wham_tasks*.schema.json`
- Settings schemas in `schemas/backend_api_wham_settings*.schema.json`

---

## Notes

- All WHAM endpoints require authentication headers: `Authorization: Bearer {token}`, `ChatGPT-Account-Id: {account_id}`
- Task operations use cursor-based pagination with opaque `+RID:...` tokens
- SSE streams use `text/event-stream; charset=utf-8` content type
- Pull request integration supports `refs/pull/<n>/head` for code review queues
- Full request/response examples available in `examples/` directory
- Endpoint selection driven by `ModelProviderInfo` (configurable via config file, command-line overrides, or profiles)
